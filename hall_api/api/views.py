from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import Hall, Booking, Personnel, Material, Expense, Payment, MagicLoginToken
from .serializers import (
    HallSerializer, BookingSerializer, PersonnelSerializer,
    MaterialSerializer, ExpenseSerializer, PaymentSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta, date
import hashlib
import secrets

class SummaryView(APIView):
    def get(self, request):
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today = timezone.localdate()
        start_28 = today - timedelta(days=27)
        end_28 = today

        start_q = (request.query_params.get('start_date') or request.query_params.get('start') or '').strip()
        end_q = (request.query_params.get('end_date') or request.query_params.get('end') or '').strip()
        if start_q or end_q:
            if not start_q or not end_q:
                return Response(
                    {'dates': 'start_date et end_date sont requis (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                range_start = date.fromisoformat(start_q)
                range_end = date.fromisoformat(end_q)
            except ValueError:
                return Response(
                    {'dates': 'Format de date invalide (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if range_end < range_start:
                return Response(
                    {'dates': 'La date fin doit être après la date début'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            range_start = start_28
            range_end = end_28

        range_days = (range_end - range_start).days + 1
        
        total_bookings = Booking.objects.count()
        active_halls = Hall.objects.count()
        total_revenue = Payment.objects.filter(status='paid', booking__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expenses = Expense.objects.filter(date__gte=first_day_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
        pending_payments = Payment.objects.filter(status='pending', booking__isnull=False).count()
        material_losses = Material.objects.filter(status='lost').count()
        
        # Monthly stats for reports
        monthly_revenue = Payment.objects.filter(date__gte=first_day_of_month, status='paid', booking__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_last_28_days = Payment.objects.filter(status='paid', date__gte=start_28, booking__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0
        expenses_last_28_days = Expense.objects.filter(date__gte=start_28).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_in_range = Payment.objects.filter(
            status='paid',
            booking__isnull=False,
            date__gte=range_start,
            date__lte=range_end,
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        expenses_in_range = Expense.objects.filter(
            date__gte=range_start,
            date__lte=range_end,
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Occupation (last 28 days): based on booked days across all halls
        total_available_days_28 = Hall.objects.count() * 28
        booked_days_total_28 = 0
        booked_days_by_type = {}

        bookings_28 = Booking.objects.filter(
            status__in=['pending', 'confirmed', 'paid'],
            start_date__lte=end_28,
            end_date__gte=start_28,
        ).values('event_type', 'start_date', 'end_date')

        for b in bookings_28:
            start = b['start_date']
            end = b['end_date']
            if not start or not end:
                continue
            overlap_start = max(start, start_28)
            overlap_end = min(end, end_28)
            if overlap_end < overlap_start:
                continue
            days = (overlap_end - overlap_start).days + 1
            booked_days_total_28 += days
            key = b.get('event_type') or 'Autre'
            booked_days_by_type[key] = booked_days_by_type.get(key, 0) + days

        if total_available_days_28 > 0:
            occupation_rate_28_days = round((booked_days_total_28 / total_available_days_28) * 100, 1)
        else:
            occupation_rate_28_days = 0

        occupation_data = []
        if booked_days_total_28 > 0:
            for event_type, days in booked_days_by_type.items():
                pct = round((days / booked_days_total_28) * 100, 1)
                occupation_data.append({'type': event_type, 'percentage': pct})
            occupation_data.sort(key=lambda x: x['percentage'], reverse=True)

        total_available_days_range = Hall.objects.count() * max(0, range_days)
        booked_days_total_range = 0
        booked_days_by_type_range = {}

        bookings_range = Booking.objects.filter(
            status__in=['pending', 'confirmed', 'paid'],
            start_date__lte=range_end,
            end_date__gte=range_start,
        ).values('event_type', 'start_date', 'end_date')

        for b in bookings_range:
            start = b['start_date']
            end = b['end_date']
            if not start or not end:
                continue
            overlap_start = max(start, range_start)
            overlap_end = min(end, range_end)
            if overlap_end < overlap_start:
                continue
            days = (overlap_end - overlap_start).days + 1
            booked_days_total_range += days
            key = b.get('event_type') or 'Autre'
            booked_days_by_type_range[key] = booked_days_by_type_range.get(key, 0) + days

        if total_available_days_range > 0:
            occupation_rate_in_range = round((booked_days_total_range / total_available_days_range) * 100, 1)
        else:
            occupation_rate_in_range = 0

        occupation_data_in_range = []
        if booked_days_total_range > 0:
            for event_type, days in booked_days_by_type_range.items():
                pct = round((days / booked_days_total_range) * 100, 1)
                occupation_data_in_range.append({'type': event_type, 'percentage': pct})
            occupation_data_in_range.sort(key=lambda x: x['percentage'], reverse=True)

        return Response({
            'total_bookings': total_bookings,
            'active_halls': active_halls,
            'total_revenue': total_revenue,
            'monthly_expenses': monthly_expenses,
            'pending_payments': pending_payments,
            'material_losses': material_losses,
            'monthly_revenue': monthly_revenue,
            'revenue_last_28_days': revenue_last_28_days,
            'expenses_last_28_days': expenses_last_28_days,
            'occupation_rate_28_days': occupation_rate_28_days,
            'occupation_data': occupation_data,
            'range_start': range_start.isoformat(),
            'range_end': range_end.isoformat(),
            'range_days': range_days,
            'revenue_in_range': revenue_in_range,
            'expenses_in_range': expenses_in_range,
            'occupation_rate_in_range': occupation_rate_in_range,
            'occupation_data_in_range': occupation_data_in_range,
        })

def _hash_magic_token(raw_token: str) -> str:
    token = '' if raw_token is None else str(raw_token)
    material = f"{token}{settings.SECRET_KEY}".encode('utf-8')
    return hashlib.sha256(material).hexdigest()

def _issue_magic_token(user):
    raw = secrets.token_urlsafe(32)
    token_hash = _hash_magic_token(raw)
    now = timezone.now()
    expires_at = now + timedelta(minutes=15)
    record = MagicLoginToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    return raw, record

def _split_full_name(full_name: str):
    value = (full_name or '').strip()
    if not value:
        return '', ''
    parts = [p for p in value.split(' ') if p]
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], ' '.join(parts[1:])

def _build_magic_login_url(request, raw_token: str):
    origin = (getattr(settings, 'FRONTEND_URL', '') or getattr(settings, 'FRONTEND_ORIGIN', '') or '').strip() or 'http://localhost:3000'
    
    return f"{origin.rstrip('/')}/login?token={raw_token}"

def _send_reservation_email(*, to_email: str, full_name: str, booking: Booking, magic_url: str, account_created: bool):
    first_name, _ = _split_full_name(full_name)
    greeting_name = first_name or full_name or 'Client'
    subject = 'Confirmation de réservation'
    account_line = (
        "Nous avons également créé automatiquement votre compte afin que vous puissiez gérer facilement vos réservations, consulter votre historique et effectuer vos prochaines réservations plus rapidement.\n\n"
        if account_created
        else ""
    )
    status_map = {
        'pending': 'En attente',
        'confirmed': 'Confirmé',
        'paid': 'Payé',
        'cancelled': 'Annulé',
    }
    status_label = status_map.get(getattr(booking, 'status', ''), getattr(booking, 'status', ''))
    intro_line = (
        "Votre réservation a été enregistrée avec succès.\n\n"
        if booking.status == 'pending'
        else "Votre réservation a été confirmée avec succès.\n\n"
    )
    body = (
        f"Bonjour {greeting_name},\n\n"
        f"{intro_line}"
        "Détails de la réservation :\n"
        f"- Salle : {booking.hall.name}\n"
        f"- Type d evenement : {booking.event_type}\n"
        f"- date debbut : {booking.start_date}\n"
        f"- date fin : {booking.end_date}\n\n"
        f"- Statut : {status_label}\n\n"
        f"{account_line}"
        "Utilisez le lien sécurisé ci-dessous pour accéder instantanément à votre compte :\n\n"
        "[Gérer mes réservations]\n\n"
        f"{magic_url}\n\n"
        "Pour des raisons de sécurité, ce lien d’accès expirera dans 15 minutes.\n\n"
        "Si vous le souhaitez, vous pourrez ensuite définir un mot de passe permanent dans les paramètres de votre compte.\n\n"
        "Merci de votre confiance et à bientôt.\n"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@hall.local',
        recipient_list=[to_email],
        fail_silently=False,
    )

def _phone_username_candidates(raw_username):
    raw = '' if raw_username is None else str(raw_username)
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if not digits:
        return [raw] if raw else []

    candidates = []
    seen = set()

    def add(value):
        if value and value not in seen:
            seen.add(value)
            candidates.append(value)

    add(raw.strip())
    add(digits)

    if digits.startswith('0') and len(digits) > 1:
        add(digits[1:])

    stripped = digits[1:] if digits.startswith('0') else digits
    if stripped and not stripped.startswith('257') and len(stripped) in (8, 9):
        add(f'257{stripped}')

    if digits.startswith('257') and len(digits) > 3:
        add(digits[3:])

    return candidates

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_field = self.username_field
        raw_username = attrs.get(username_field)
        password = attrs.get('password')

        user = None
        for candidate in _phone_username_candidates(raw_username):
            user = authenticate(
                request=self.context.get('request'),
                **{username_field: candidate, 'password': password},
            )
            if user is not None:
                break

        if user is None:
            raise AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        refresh = self.get_token(user)
        data = {'refresh': str(refresh), 'access': str(refresh.access_token)}

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data

class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.get_username(),
            'email': getattr(user, 'email', ''),
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data or {}
        phone = str(payload.get('phone') or payload.get('username') or '').strip()
        password = payload.get('password') or ''
        first_name = payload.get('first_name') or ''
        last_name = payload.get('last_name') or ''
        email = payload.get('email') or ''

        phone_norm = ''.join(ch for ch in phone if ch.isdigit())

        if not phone_norm:
            return Response({'phone': 'Numéro de téléphone requis'}, status=status.HTTP_400_BAD_REQUEST)
        if len(phone_norm) < 8:
            return Response({'phone': 'Numéro de téléphone invalide'}, status=status.HTTP_400_BAD_REQUEST)
        if not password or len(password) < 6:
            return Response({'password': 'Mot de passe (min 6 caractères) requis'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        if User.objects.filter(username=phone_norm).exists():
            return Response({'phone': 'Ce numéro est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=phone_norm,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
        )

        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

class HallViewSet(viewsets.ModelViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='guest')
    def guest(self, request):
        payload = request.data or {}

        full_name = (payload.get('full_name') or payload.get('customer_name') or '').strip()
        email = (payload.get('email') or payload.get('customer_email') or '').strip().lower()
        phone = (payload.get('phone') or payload.get('customer_phone') or '').strip()
        hall_id = payload.get('hall')
        event_type = (payload.get('event_type') or '').strip()
        start_date = payload.get('start_date') or payload.get('date_debut') or payload.get('date_start')
        end_date = payload.get('end_date') or payload.get('date_fin') or payload.get('date_end')

        if not full_name:
            return Response({'full_name': 'Nom complet requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'email': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not phone:
            return Response({'phone': 'Téléphone requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not hall_id:
            return Response({'hall': 'Salle requise'}, status=status.HTTP_400_BAD_REQUEST)
        if not event_type:
            return Response({'event_type': "Type d'événement requis"}, status=status.HTTP_400_BAD_REQUEST)
        if not start_date:
            return Response({'start_date': 'Date début requise'}, status=status.HTTP_400_BAD_REQUEST)
        if not end_date:
            return Response({'end_date': 'Date fin requise'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hall = Hall.objects.get(id=hall_id)
        except Hall.DoesNotExist:
            return Response({'hall': 'Salle introuvable'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_dt = date.fromisoformat(str(start_date))
            end_dt = date.fromisoformat(str(end_date))
        except ValueError:
            return Response({'dates': 'Format de date invalide (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        if end_dt < start_dt:
            return Response({'dates': 'La date fin doit être après la date début'}, status=status.HTTP_400_BAD_REQUEST)

        overlap_exists = Booking.objects.filter(
            hall=hall,
            status__in=['pending', 'confirmed', 'paid'],
            start_date__lte=end_dt,
            end_date__gte=start_dt,
        ).exists()
        if overlap_exists:
            return Response({'dates': 'Ces dates ne sont pas disponibles pour cette salle'}, status=status.HTTP_400_BAD_REQUEST)

        days = (end_dt - start_dt).days + 1
        total_price = (Decimal(days) * (hall.price_per_day or Decimal('0.00'))).quantize(Decimal('0.01'))

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        account_created = False
        if user is None:
            account_created = True
            phone_digits = ''.join(ch for ch in phone if ch.isdigit())
            base_username = phone_digits or email
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                suffix += 1
                username = f"{base_username}-{suffix}"

            first_name, last_name = _split_full_name(full_name)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
        elif not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])

        booking = Booking.objects.create(
            hall=hall,
            customer_name=full_name,
            customer_email=email,
            customer_phone=phone,
            event_type=event_type,
            start_date=start_dt,
            end_date=end_dt,
            total_price=total_price,
            status='pending',
            created_by=user,
        )

        raw_token, _ = _issue_magic_token(user)
        magic_url = _build_magic_login_url(request, raw_token)
        _send_reservation_email(to_email=email, full_name=full_name, booking=booking, magic_url=magic_url, account_created=account_created)

        return Response(
            {
                'booking': BookingSerializer(booking).data,
                'message': "Réservation confirmée. Un email avec un lien sécurisé a été envoyé.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='calendar')
    def calendar(self, request):
        hall_id = request.query_params.get('hall')
        qs = Booking.objects.all()
        if hall_id:
            qs = qs.filter(hall_id=hall_id)
        qs = qs.exclude(status='cancelled').values('hall_id', 'start_date', 'end_date')
        return Response(list(qs))

class MagicLinkRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data or {}
        email = (payload.get('email') or '').strip().lower()
        if not email:
            return Response({'email': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user is None:
            return Response({'detail': "Email introuvable"}, status=status.HTTP_404_NOT_FOUND)

        raw_token, _ = _issue_magic_token(user)
        magic_url = _build_magic_login_url(request, raw_token)
        subject = "Votre lien de connexion"
        body = (
            "Bonjour,\n\n"
            "Utilisez le lien sécurisé ci-dessous pour vous connecter :\n\n"
            f"{magic_url}\n\n"
            "Pour des raisons de sécurité, ce lien d’accès expirera dans 15 minutes.\n"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@hall.local',
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': "Lien envoyé par email."}, status=status.HTTP_200_OK)

class MagicLinkVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data or {}
        raw_token = payload.get('token') or ''
        token_hash = _hash_magic_token(raw_token)
        now = timezone.now()

        record = MagicLoginToken.objects.select_related('user').filter(token_hash=token_hash).first()
        if record is None:
            return Response({'detail': 'Lien invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
        if record.used_at is not None:
            return Response({'detail': 'Lien déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        if record.expires_at < now:
            return Response({'detail': 'Lien expiré'}, status=status.HTTP_400_BAD_REQUEST)

        record.used_at = now
        record.save(update_fields=['used_at'])

        refresh = RefreshToken.for_user(record.user)
        access = str(refresh.access_token)
        return Response(
            {
                'refresh': str(refresh),
                'access': access,
                'redirect_to': '/dashboard',
            },
            status=status.HTTP_200_OK,
        )

class SetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payload = request.data or {}
        password = payload.get('password') or ''
        if not password or len(password) < 6:
            return Response({'password': 'Mot de passe (min 6 caractères) requis'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.set_password(password)
        user.save(update_fields=['password'])
        return Response({'message': 'Mot de passe défini avec succès'}, status=status.HTTP_200_OK)

class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def _recalc_booking_paid(self, booking):
        paid_total = Payment.objects.filter(booking=booking, status='paid').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        booking.paid_amount = paid_total
        if booking.total_price and paid_total >= booking.total_price:
            booking.status = 'paid'
        else:
            if booking.status == 'pending' and paid_total > 0:
                booking.status = 'confirmed'
        booking.save(update_fields=['paid_amount', 'status'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        amount = payment.amount or Decimal('0.00')
        total = payment.booking.total_price or Decimal('0.00')
        paid = payment.booking.paid_amount or Decimal('0.00')
        remaining_before = total - paid
        if remaining_before < 0:
            remaining_before = Decimal('0.00')

        if payment.status == 'paid':
            if amount >= remaining_before and remaining_before > 0:
                payment.kind = 'full'
            else:
                payment.kind = 'advance'
            payment.save(update_fields=['kind'])

        self._recalc_booking_paid(payment.booking)

        output = self.get_serializer(payment)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = self.get_object()
        self._recalc_booking_paid(instance.booking)
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking = instance.booking
        response = super().destroy(request, *args, **kwargs)
        self._recalc_booking_paid(booking)
        return response
