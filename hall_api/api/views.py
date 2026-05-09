from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import Hall, Booking, Personnel, Material, Expense, Payment
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
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

class SummaryView(APIView):
    def get(self, request):
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_bookings = Booking.objects.count()
        active_halls = Hall.objects.count()
        total_revenue = Payment.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expenses = Expense.objects.filter(date__gte=first_day_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
        pending_payments = Payment.objects.filter(status='pending').count()
        material_losses = Material.objects.filter(status='lost').count()
        
        # Monthly stats for reports
        monthly_revenue = Payment.objects.filter(date__gte=first_day_of_month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Occupation by event type
        occupation_stats = Booking.objects.values('event_type').annotate(count=Count('id'))
        total_b = Booking.objects.count()
        occupation_data = []
        for stat in occupation_stats:
            percentage = (stat['count'] / total_b * 100) if total_b > 0 else 0
            occupation_data.append({
                'type': stat['event_type'],
                'percentage': round(percentage, 1)
            })

        return Response({
            'total_bookings': total_bookings,
            'active_halls': active_halls,
            'total_revenue': total_revenue,
            'monthly_expenses': monthly_expenses,
            'pending_payments': pending_payments,
            'material_losses': material_losses,
            'monthly_revenue': monthly_revenue,
            'occupation_data': occupation_data
        })

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

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='calendar')
    def calendar(self, request):
        hall_id = request.query_params.get('hall')
        qs = Booking.objects.all()
        if hall_id:
            qs = qs.filter(hall_id=hall_id)
        qs = qs.exclude(status='cancelled').values('hall_id', 'start_date', 'end_date')
        return Response(list(qs))

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
