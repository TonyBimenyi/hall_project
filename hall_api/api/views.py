from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import Hall, Booking, Personnel, Material, Expense, Payment, Notification, MagicLoginToken, AccountSecurityProfile, Room, Customer
from .serializers import (
    HallSerializer, BookingSerializer, PersonnelSerializer,
    MaterialSerializer, ExpenseSerializer, PaymentSerializer, NotificationSerializer, RoomSerializer, CustomerSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
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
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from datetime import timedelta, date
import hashlib
import secrets
import unicodedata

from .payment_email import send_payment_invoice_email

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
        active_rooms = Room.objects.filter(is_active=True).count()
        total_revenue = Payment.objects.filter(status='paid', booking__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expenses = Expense.objects.filter(date__gte=first_day_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
        pending_payments = Payment.objects.filter(status='pending', booking__isnull=False).count()
        material_losses = Material.objects.filter(status='lost').count()
        room_status_counts = {
            'available': Room.objects.filter(status='available').count(),
            'reserved': Room.objects.filter(status='reserved').count(),
            'occupied': Room.objects.filter(status='occupied').count(),
            'cleaning': Room.objects.filter(status='cleaning').count(),
            'maintenance': Room.objects.filter(status='maintenance').count(),
        }
        occupied_rooms_today = room_status_counts['occupied']
        room_occupancy_rate_today = round((occupied_rooms_today / active_rooms) * 100, 1) if active_rooms > 0 else 0
        todays_check_ins = Booking.objects.filter(booking_type='room', checked_in_at__date=today).count()
        todays_check_outs = Booking.objects.filter(booking_type='room', checked_out_at__date=today).count()
        
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
            'active_rooms': active_rooms,
            'total_revenue': total_revenue,
            'monthly_expenses': monthly_expenses,
            'pending_payments': pending_payments,
            'material_losses': material_losses,
            'room_occupancy_rate_today': room_occupancy_rate_today,
            'occupied_rooms_today': occupied_rooms_today,
            'todays_check_ins': todays_check_ins,
            'todays_check_outs': todays_check_outs,
            'room_status_counts': room_status_counts,
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
    item_label = 'Salle' if getattr(booking, 'booking_type', 'hall') == 'hall' else 'Chambre'
    item_name = getattr(booking, 'booked_item_name', '') or 'Non spécifié'
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
        f"- ID de réservation : {booking.id}\n"
        f"- {item_label} : {item_name}\n"
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

def _normalize_phone(raw_phone):
    return ''.join(ch for ch in str(raw_phone or '') if ch.isdigit())


def _match_customer(*, full_name='', phone='', email='', identity_number=''):
    filters = Q()
    phone_value = str(phone or '').strip()
    email_value = str(email or '').strip().lower()
    identity_value = str(identity_number or '').strip()
    first_name, last_name = _split_full_name(full_name)

    if phone_value:
        filters |= Q(phone__icontains=phone_value)
    if email_value:
        filters |= Q(email__iexact=email_value)
    if identity_value:
        filters |= Q(identity_number__iexact=identity_value)
    if first_name:
        filters |= Q(first_name__iexact=first_name, last_name__iexact=last_name)

    if not filters:
        return None

    return Customer.objects.filter(filters).order_by('-updated_at', '-id').first()


def _upsert_customer_from_snapshot(*, customer=None, full_name='', phone='', email='', identity_type='', identity_number='', actor=None):
    first_name, last_name = _split_full_name(full_name)
    phone_value = str(phone or '').strip()
    email_value = str(email or '').strip().lower()
    identity_type_value = str(identity_type or '').strip()
    identity_number_value = str(identity_number or '').strip()

    if customer is None:
        customer = _match_customer(
            full_name=full_name,
            phone=phone_value,
            email=email_value,
            identity_number=identity_number_value,
        )

    if customer is None:
        if not phone_value:
            return None
        customer = Customer(
            first_name=first_name or last_name or 'Client',
            last_name=last_name if first_name else '',
            phone=phone_value,
            email=email_value,
            identity_type=identity_type_value,
            identity_number=identity_number_value,
            created_by=actor,
            updated_by=actor,
        )
        customer.save()
        return customer

    changed = []
    next_first = first_name or customer.first_name
    next_last = last_name if first_name else (customer.last_name or last_name)
    if customer.first_name != next_first:
        customer.first_name = next_first
        changed.append('first_name')
    if customer.last_name != next_last:
        customer.last_name = next_last
        changed.append('last_name')
    if phone_value and customer.phone != phone_value:
        customer.phone = phone_value
        changed.append('phone')
    if email_value and customer.email != email_value:
        customer.email = email_value
        changed.append('email')
    if identity_type_value and customer.identity_type != identity_type_value:
        customer.identity_type = identity_type_value
        changed.append('identity_type')
    if identity_number_value and customer.identity_number != identity_number_value:
        customer.identity_number = identity_number_value
        changed.append('identity_number')
    if actor and getattr(customer, 'updated_by_id', None) != getattr(actor, 'id', None):
        customer.updated_by = actor
        changed.append('updated_by')
    if changed:
        changed.append('updated_at')
        customer.save(update_fields=changed)
    return customer


def _index_hall_additional_services(hall: Hall):
    services = getattr(hall, 'additional_services', None) or []
    index = {}
    for service in services:
        try:
            name = str(service.get('name') or '').strip()
        except Exception:
            continue
        if not name:
            continue

        has_sub = bool(service.get('has_subservices'))
        price = service.get('price', '0.00')
        subservices = service.get('subservices') or []
        sub_index = {}
        if has_sub and isinstance(subservices, list):
            for sub in subservices:
                if not isinstance(sub, dict):
                    continue
                sub_name = str(sub.get('name') or '').strip()
                if not sub_name:
                    continue
                sub_index[sub_name] = Decimal(str(sub.get('price') or '0.00'))

        index[name] = {
            'has_subservices': has_sub,
            'price': Decimal(str(price or '0.00')),
            'subservices': sub_index,
        }
    return index


def _compute_addons_total(item: Hall | Room, selected_services):
    selected_services = selected_services or []
    if not isinstance(selected_services, list):
        raise DjangoValidationError('Les services sélectionnés doivent être une liste')

    services_index = _index_hall_additional_services(item)
    addons_total = Decimal('0.00')
    normalized_selected = []

    for selected_item in selected_services:
        if not isinstance(selected_item, dict):
            raise DjangoValidationError('Format de service sélectionné invalide')

        name = str(selected_item.get('name') or '').strip()
        if not name:
            raise DjangoValidationError("Chaque service sélectionné doit avoir un nom")
        if name not in services_index:
            raise DjangoValidationError(f"Service '{name}' introuvable pour cette salle/chambre")

        cfg = services_index[name]
        if cfg['has_subservices']:
            subs = selected_item.get('subservices') or []
            if not isinstance(subs, list) or not subs:
                raise DjangoValidationError(f"Choisissez au moins un sous-service pour '{name}'")

            normalized_subs = []
            for sub in subs:
                if not isinstance(sub, dict):
                    raise DjangoValidationError(f"Sous-service invalide pour '{name}'")
                sub_name = str(sub.get('name') or '').strip()
                if not sub_name:
                    raise DjangoValidationError(f"Sous-service invalide pour '{name}'")
                if sub_name not in cfg['subservices']:
                    raise DjangoValidationError(f"Sous-service '{sub_name}' introuvable pour '{name}'")
                addons_total += cfg['subservices'][sub_name]
                normalized_subs.append({'name': sub_name})

            normalized_selected.append({'name': name, 'subservices': normalized_subs})
            continue

        if selected_item.get('subservices'):
            raise DjangoValidationError(f"Le service '{name}' n'a pas de sous-services")

        addons_total += cfg['price']
        normalized_selected.append({'name': name})

    return addons_total.quantize(Decimal('0.01')), normalized_selected


def _compute_booking_totals(item: Hall | Room, start_dt: date, end_dt: date, selected_services):
    if end_dt < start_dt:
        raise DjangoValidationError('La date fin doit être après la date début')
    days = (end_dt - start_dt).days + 1
    if isinstance(item, Hall):
        base_total = (Decimal(days) * Decimal(str(item.price_per_day or '0.00'))).quantize(Decimal('0.01'))
    elif isinstance(item, Room):
        base_total = (Decimal(days) * Decimal(str(item.price_per_night or '0.00'))).quantize(Decimal('0.01'))
    else:
        base_total = Decimal('0.00')
    addons_total, normalized_selected = _compute_addons_total(item, selected_services)
    total = (base_total + addons_total).quantize(Decimal('0.01'))
    return base_total, addons_total, total, normalized_selected

def _get_security_profile(user):
    if not user or not getattr(user, 'pk', None):
        return None
    profile, _ = AccountSecurityProfile.objects.get_or_create(user=user)
    return profile

def _user_payload(user):
    security = _get_security_profile(user)
    personnel = getattr(user, 'personnel_record', None)
    phone = getattr(personnel, 'phone', '') if personnel is not None else ''
    full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return {
        'id': user.id,
        'username': user.get_username(),
        'email': getattr(user, 'email', ''),
        'first_name': getattr(user, 'first_name', ''),
        'last_name': getattr(user, 'last_name', ''),
        'full_name': full_name,
        'phone': phone,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'must_change_password': bool(getattr(security, 'must_change_password', False)),
        'personnel_id': getattr(personnel, 'id', None),
        'personnel_role': getattr(personnel, 'role', ''),
        'can_manage_staff_accounts': _can_manage_staff_accounts(user),
    }

def _can_manage_staff_accounts(user):
    if not user or not user.is_authenticated:
        return False
    return bool(_staff_role_key(user) in {'super_admin', 'proprietaire', 'gestionnaire'})

def _actor(request):
    user = getattr(request, 'user', None)
    return user if getattr(user, 'is_authenticated', False) else None


def _sync_room_status_for_booking(booking, room_action='none'):
    if not booking or getattr(booking, 'booking_type', '') != 'room' or not getattr(booking, 'room_id', None):
        return

    room = booking.room
    now = timezone.now()
    booking_fields = []
    room_fields = []

    if room_action == 'check_in':
        if booking.checked_in_at is None:
            booking.checked_in_at = now
            booking_fields.append('checked_in_at')
        if room.status != 'occupied':
            room.status = 'occupied'
            room_fields.append('status')
    elif room_action == 'check_out':
        if booking.checked_out_at is None:
            booking.checked_out_at = now
            booking_fields.append('checked_out_at')
        if room.status != 'cleaning':
            room.status = 'cleaning'
            room_fields.append('status')
    else:
        if booking.checked_in_at and not booking.checked_out_at and room.status != 'occupied':
            room.status = 'occupied'
            room_fields.append('status')
        elif booking.checked_out_at and room.status != 'cleaning':
            room.status = 'cleaning'
            room_fields.append('status')
        else:
            if (
                not booking.checked_in_at
                and not booking.checked_out_at
                and getattr(booking, 'status', '') in ('pending', 'confirmed', 'paid')
                and room.status == 'available'
            ):
                room.status = 'reserved'
                room_fields.append('status')

    if booking_fields:
        booking.save(update_fields=booking_fields)
    if room_fields:
        room.save(update_fields=room_fields)


def _refresh_room_reservation_state(room):
    if not room or getattr(room, 'status', '') not in ('available', 'reserved'):
        return

    has_active_reservation = Booking.objects.filter(
        booking_type='room',
        room=room,
        status__in=['pending', 'confirmed', 'paid'],
        checked_in_at__isnull=True,
        checked_out_at__isnull=True,
    ).exists()

    desired = 'reserved' if has_active_reservation else 'available'
    if room.status != desired:
        room.status = desired
        room.save(update_fields=['status', 'updated_at'])

def _normalize_role_label(value):
    text = str(value or '').strip().lower()
    if not text:
        return ''
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def _staff_role_key(user):
    if not user or not user.is_active:
        return ''
    if user.is_superuser:
        return 'super_admin'

    personnel = getattr(user, 'personnel_record', None)
    role = _normalize_role_label(getattr(personnel, 'role', ''))
    if role in {'admin', 'proprietaire'}:
        return 'proprietaire'
    if role in {'manager', 'gestionnaire'}:
        return 'gestionnaire'
    if role == 'gerant':
        return 'gerant'
    if role in {'receptionniste', 'receptionist', 'reception'}:
        return 'receptionniste'
    if user.is_staff:
        return 'proprietaire'
    return role

def _is_admin_user(user):
    return _staff_role_key(user) in {'super_admin', 'proprietaire', 'gestionnaire', 'gerant'}

def _can_delete_booking(user):
    role = _staff_role_key(user)
    return role in {'super_admin', 'proprietaire', 'gestionnaire', 'receptionniste'}

def _notification_recipients(_category):
    recipients = []
    for user in get_user_model().objects.filter(is_active=True).distinct():
        if _is_admin_user(user):
            recipients.append(user)
    return recipients

def _create_notification_for_user(*, user, title, message, category, type, event_key=None, booking=None, payment=None, material=None):
    if event_key:
        notification, created = Notification.objects.get_or_create(
            user=user,
            event_key=event_key,
            defaults={
                'title': title,
                'message': message,
                'category': category,
                'type': type,
                'booking': booking,
                'payment': payment,
                'material': material,
            },
        )
        if not created:
            changed = False
            if notification.title != title:
                notification.title = title
                changed = True
            if notification.message != message:
                notification.message = message
                changed = True
            if notification.type != type:
                notification.type = type
                changed = True
            if notification.category != category:
                notification.category = category
                changed = True
            if notification.booking_id != getattr(booking, 'id', None):
                notification.booking = booking
                changed = True
            if notification.payment_id != getattr(payment, 'id', None):
                notification.payment = payment
                changed = True
            if notification.material_id != getattr(material, 'id', None):
                notification.material = material
                changed = True
            if changed:
                notification.save(update_fields=['title', 'message', 'type', 'category', 'booking', 'payment', 'material', 'updated_at'])
        return notification
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        category=category,
        type=type,
        booking=booking,
        payment=payment,
        material=material,
    )

def _create_role_notifications(*, title, message, category, type, event_key=None, booking=None, payment=None, material=None):
    for user in _notification_recipients(category):
        _create_notification_for_user(
            user=user,
            title=title,
            message=message,
            category=category,
            type=type,
            event_key=event_key,
            booking=booking,
            payment=payment,
            material=material,
        )

def _sync_overdue_notifications():
    today = timezone.localdate()
    overdue_bookings = Booking.objects.filter(
        end_date__lt=today,
        status__in=['pending', 'confirmed'],
    ).exclude(total_price__lte=0)

    active_keys = set()
    for booking in overdue_bookings:
        total = booking.total_price or Decimal('0.00')
        paid = booking.paid_amount or Decimal('0.00')
        remaining = total - paid
        if remaining <= 0:
            continue

        event_key = f"payment-overdue-booking-{booking.id}"
        active_keys.add(event_key)
        booking_code = booking.code or f"LBR{booking.id}"
        message = f"Paiement en retard pour la reservation {booking_code}."
        _create_role_notifications(
            title='Paiement en retard',
            message=message,
            category='payment_overdue',
            type='danger',
            event_key=event_key,
            booking=booking,
        )

    resolved = Notification.objects.filter(category='payment_overdue', is_read=False)
    if active_keys:
        resolved = resolved.exclude(event_key__in=active_keys)
    resolved.update(is_read=True, read_at=timezone.now())

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
        security = _get_security_profile(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'must_change_password': bool(getattr(security, 'must_change_password', False)),
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data

class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user))

    def patch(self, request):
        user = request.user
        payload = request.data or {}
        first_name = str(payload.get('first_name') or user.first_name or '').strip()
        last_name = str(payload.get('last_name') or user.last_name or '').strip()
        email = str(payload.get('email') or user.email or '').strip()
        username = str(payload.get('username') or '').strip()
        phone = str(payload.get('phone') or '').strip()

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        update_fields = ['first_name', 'last_name', 'email']

        if username and username != user.get_username():
            exists = get_user_model().objects.filter(username=username).exclude(id=user.id).exists()
            if exists:
                return Response({'username': "Ce nom d'utilisateur est déjà utilisé"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = username
            update_fields.append('username')

        personnel = getattr(user, 'personnel_record', None)
        if personnel is not None:
            personnel.phone = phone
            personnel.name = f"{first_name} {last_name}".strip() or personnel.name
            personnel.email = email
            personnel.save(update_fields=['name', 'email', 'phone'])

        user.save(update_fields=update_fields)
        return Response(_user_payload(user), status=status.HTTP_200_OK)

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

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        _sync_overdue_notifications()
        return Notification.objects.filter(user=self.request.user).order_by('-created_at', '-id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = str(request.query_params.get('status') or '').strip().lower()
        limit = str(request.query_params.get('limit') or '').strip()

        if status_filter == 'unread':
            queryset = queryset.filter(is_read=False)
        elif status_filter == 'read':
            queryset = queryset.filter(is_read=True)

        if limit.isdigit():
            queryset = queryset[:max(0, int(limit))]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        now = timezone.now()
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=now)
        return Response({'message': 'All notifications marked as read'})

class HallViewSet(viewsets.ModelViewSet):
    queryset = Hall.objects.all().order_by('-id')
    serializer_class = HallSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=_actor(self.request), updated_by=_actor(self.request))

    def perform_update(self, serializer):
        serializer.save(updated_by=_actor(self.request))

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by('-id')
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=_actor(self.request), updated_by=_actor(self.request))
        _refresh_room_reservation_state(serializer.instance)

    def perform_update(self, serializer):
        serializer.save(updated_by=_actor(self.request))
        _refresh_room_reservation_state(serializer.instance)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-updated_at', '-id')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = str(self.request.query_params.get('search') or '').strip()
        if search:
            parts = [part for part in search.split(' ') if part]
            filters = (
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(identity_number__icontains=search)
            )
            if len(parts) >= 2:
                filters |= Q(first_name__icontains=parts[0], last_name__icontains=' '.join(parts[1:]))
            queryset = queryset.filter(filters)

        limit = str(self.request.query_params.get('limit') or '').strip()
        if limit.isdigit():
            queryset = queryset[:max(1, min(int(limit), 25))]
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=_actor(self.request), updated_by=_actor(self.request))

    def perform_update(self, serializer):
        serializer.save(updated_by=_actor(self.request))

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all().order_by('-id')
        return Booking.objects.filter(created_by=user).order_by('-id')

    def destroy(self, request, *args, **kwargs):
        if (request.user.is_staff or request.user.is_superuser) and not _can_delete_booking(request.user):
            return Response({'detail': 'Suppression de réservation non autorisée pour ce rôle'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        customer = serializer.validated_data.get('customer')
        customer_name = serializer.validated_data.get('customer_name', '')
        customer_phone = serializer.validated_data.get('customer_phone', '')
        customer_email = serializer.validated_data.get('customer_email', '')
        guest_id_type = serializer.validated_data.get('guest_id_type', '')
        guest_id_number = serializer.validated_data.get('guest_id_number', '')
        resolved_customer = _upsert_customer_from_snapshot(
            customer=customer,
            full_name=customer_name,
            phone=customer_phone,
            email=customer_email,
            identity_type=guest_id_type,
            identity_number=guest_id_number,
            actor=_actor(self.request),
        )
        booking_type = serializer.validated_data.get('booking_type', 'hall')
        hall = serializer.validated_data.get('hall')
        room = serializer.validated_data.get('room')
        item = hall if booking_type == 'hall' else room
        start_dt = serializer.validated_data.get('start_date')
        end_dt = serializer.validated_data.get('end_date')
        selected = serializer.validated_data.get('additional_services_selected') or []
        _, addons_total, total, normalized_selected = _compute_booking_totals(item, start_dt, end_dt, selected)
        save_kwargs = {
            'created_by': self.request.user,
            'updated_by': self.request.user,
            'customer': resolved_customer,
            'total_price': total,
            'addons_total': addons_total,
            'additional_services_selected': normalized_selected,
        }
        if booking_type == 'hall':
            save_kwargs.update({
                'room': None,
                'guest_full_name': '',
                'guest_id_type': '',
                'guest_id_number': '',
                'checked_in_at': None,
                'checked_out_at': None,
            })
        else:
            save_kwargs['hall'] = None
        serializer.save(
            **save_kwargs,
        )
        if getattr(serializer.instance, 'booking_type', '') == 'room' and getattr(serializer.instance, 'room_id', None):
            _sync_room_status_for_booking(serializer.instance, 'none')

    def perform_update(self, serializer):
        instance = serializer.instance
        customer = serializer.validated_data.get('customer', getattr(instance, 'customer', None))
        customer_name = serializer.validated_data.get('customer_name', getattr(instance, 'customer_name', ''))
        customer_phone = serializer.validated_data.get('customer_phone', getattr(instance, 'customer_phone', ''))
        customer_email = serializer.validated_data.get('customer_email', getattr(instance, 'customer_email', ''))
        guest_id_type = serializer.validated_data.get('guest_id_type', getattr(instance, 'guest_id_type', ''))
        guest_id_number = serializer.validated_data.get('guest_id_number', getattr(instance, 'guest_id_number', ''))
        resolved_customer = _upsert_customer_from_snapshot(
            customer=customer,
            full_name=customer_name,
            phone=customer_phone,
            email=customer_email,
            identity_type=guest_id_type,
            identity_number=guest_id_number,
            actor=_actor(self.request),
        )
        booking_type = serializer.validated_data.get('booking_type', getattr(instance, 'booking_type', 'hall'))
        hall = serializer.validated_data.get('hall', getattr(instance, 'hall', None))
        room = serializer.validated_data.get('room', getattr(instance, 'room', None))
        item = hall if booking_type == 'hall' else room
        start_dt = serializer.validated_data.get('start_date', getattr(instance, 'start_date', None))
        end_dt = serializer.validated_data.get('end_date', getattr(instance, 'end_date', None))
        selected = serializer.validated_data.get('additional_services_selected', getattr(instance, 'additional_services_selected', [])) or []
        _, addons_total, total, normalized_selected = _compute_booking_totals(item, start_dt, end_dt, selected)
        save_kwargs = {
            'updated_by': _actor(self.request),
            'customer': resolved_customer,
            'total_price': total,
            'addons_total': addons_total,
            'additional_services_selected': normalized_selected,
        }
        if booking_type == 'hall':
            save_kwargs.update({
                'room': None,
                'guest_full_name': '',
                'guest_id_type': '',
                'guest_id_number': '',
                'checked_in_at': None,
                'checked_out_at': None,
            })
        else:
            save_kwargs['hall'] = None
        serializer.save(
            **save_kwargs,
        )
        if getattr(serializer.instance, 'booking_type', '') == 'room' and getattr(serializer.instance, 'room_id', None):
            _sync_room_status_for_booking(serializer.instance, 'none')
            _refresh_room_reservation_state(serializer.instance.room)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        booking = serializer.instance
        email_sent = False
        email = (getattr(booking, 'customer_email', '') or '').strip().lower()

        if email:
            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()
            account_created = False

            if user is None:
                account_created = True
                raw_username = _normalize_phone(getattr(booking, 'customer_phone', '') or '') or email
                username = raw_username
                suffix = 1
                while User.objects.filter(username=username).exists():
                    suffix += 1
                    username = f"{raw_username}-{suffix}"

                first_name, last_name = _split_full_name(getattr(booking, 'customer_name', '') or '')
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

            try:
                raw_token, _ = _issue_magic_token(user)
                magic_url = _build_magic_login_url(request, raw_token)
                _send_reservation_email(
                    to_email=email,
                    full_name=getattr(booking, 'customer_name', '') or '',
                    booking=booking,
                    magic_url=magic_url,
                    account_created=account_created,
                )
                email_sent = True
            except Exception:
                email_sent = False

        headers = self.get_success_headers(serializer.data)
        response_data = dict(serializer.data)
        response_data['email_sent'] = email_sent
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

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
        selected_services = payload.get('additional_services_selected') or []

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

        try:
            _, addons_total, total_price, normalized_selected = _compute_booking_totals(hall, start_dt, end_dt, selected_services)
        except DjangoValidationError as e:
            return Response({'additional_services_selected': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            addons_total=addons_total,
            additional_services_selected=normalized_selected,
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

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        booking = self.get_object()
        if booking.booking_type != 'room' or not booking.room_id:
            return Response({'detail': 'Action disponible uniquement pour une réservation de chambre'}, status=status.HTTP_400_BAD_REQUEST)
        if booking.checked_in_at:
            return Response({'detail': 'Le check-in a déjà été effectué'}, status=status.HTTP_400_BAD_REQUEST)
        if booking.status == 'cancelled':
            return Response({'detail': 'Impossible de gérer une réservation annulée'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(booking.room, 'status', '') in ('maintenance', 'cleaning'):
            return Response({'detail': "Cette chambre n'est pas prête pour le check-in"}, status=status.HTTP_400_BAD_REQUEST)
        if not str(booking.guest_full_name or '').strip() or not str(booking.guest_id_type or '').strip() or not str(booking.guest_id_number or '').strip():
            return Response({'detail': 'Complétez le profil client et la pièce d’identité avant le check-in'}, status=status.HTTP_400_BAD_REQUEST)
        if (booking.paid_amount or Decimal('0.00')) <= Decimal('0.00'):
            return Response({'detail': 'Enregistrez au moins un paiement avant le check-in'}, status=status.HTTP_400_BAD_REQUEST)
        _sync_room_status_for_booking(booking, 'check_in')
        booking.updated_by = _actor(request)
        booking.save(update_fields=['updated_by', 'updated_at'])
        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='check-out')
    def check_out(self, request, pk=None):
        booking = self.get_object()
        if booking.booking_type != 'room' or not booking.room_id:
            return Response({'detail': 'Action disponible uniquement pour une réservation de chambre'}, status=status.HTTP_400_BAD_REQUEST)
        if not booking.checked_in_at:
            return Response({'detail': 'Le check-in doit être effectué avant le check-out'}, status=status.HTTP_400_BAD_REQUEST)
        if booking.checked_out_at:
            return Response({'detail': 'Le check-out a déjà été effectué'}, status=status.HTTP_400_BAD_REQUEST)
        if booking.status == 'cancelled':
            return Response({'detail': 'Impossible de gérer une réservation annulée'}, status=status.HTTP_400_BAD_REQUEST)
        remaining = (booking.total_price or Decimal('0.00')) - (booking.paid_amount or Decimal('0.00'))
        if remaining > Decimal('0.00'):
            return Response({'detail': 'Le séjour doit être soldé avant le check-out'}, status=status.HTTP_400_BAD_REQUEST)
        _sync_room_status_for_booking(booking, 'check_out')
        booking.updated_by = _actor(request)
        booking.save(update_fields=['updated_by', 'updated_at'])
        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='calendar')
    def calendar(self, request):
        hall_id = request.query_params.get('hall')
        room_id = request.query_params.get('room')
        qs = Booking.objects.all()
        if hall_id:
            qs = qs.filter(hall_id=hall_id)
        if room_id:
            qs = qs.filter(room_id=room_id)
        qs = qs.exclude(status='cancelled').values('hall_id', 'room_id', 'start_date', 'end_date')
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
        confirm_password = payload.get('confirm_password') or ''
        if not password:
            return Response({'password': 'Mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)
        if password != confirm_password:
            return Response({'confirm_password': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            return Response({'password': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save(update_fields=['password'])
        security = _get_security_profile(user)
        if security is not None and security.must_change_password:
            security.must_change_password = False
            security.save(update_fields=['must_change_password'])
        return Response({'message': 'Mot de passe défini avec succès', 'must_change_password': False}, status=status.HTTP_200_OK)

class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all().order_by('-id')
    serializer_class = PersonnelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _require_staff_manager(self, request):
        if not _can_manage_staff_accounts(request.user):
            return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        return None

    def create(self, request, *args, **kwargs):
        denial = self._require_staff_manager(request)
        if denial is not None:
            return denial

        payload = request.data.copy()
        create_account = str(payload.get('create_account') or '').lower() in ('1', 'true', 'yes', 'on')
        temp_password = payload.get('temporary_password') or ''
        email = str(payload.get('email') or '').strip().lower()
        username = str(payload.get('username') or '').strip()
        phone = str(payload.get('phone') or '').strip()
        name = str(payload.get('name') or '').strip()

        user = None
        if create_account:
            if not username:
                return Response({'username': "Nom d'utilisateur requis"}, status=status.HTTP_400_BAD_REQUEST)
            if not temp_password:
                return Response({'temporary_password': 'Mot de passe temporaire requis'}, status=status.HTTP_400_BAD_REQUEST)
            if get_user_model().objects.filter(username=username).exists():
                return Response({'username': "Ce nom d'utilisateur est déjà utilisé"}, status=status.HTTP_400_BAD_REQUEST)
            if email and get_user_model().objects.filter(email__iexact=email).exists():
                return Response({'email': 'Cet email est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)

            first_name, last_name = _split_full_name(name)
            user = get_user_model().objects.create_user(
                username=username,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_active=True,
                is_staff=True,
            )
            security = _get_security_profile(user)
            security.must_change_password = True
            security.save(update_fields=['must_change_password'])

        serializer = self.get_serializer(data={
            'name': name,
            'role': payload.get('role'),
            'email': email,
            'phone': phone,
            'status': payload.get('status'),
            'user': getattr(user, 'id', None),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=_actor(request), updated_by=_actor(request))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        denial = self._require_staff_manager(request)
        if denial is not None:
            return denial

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        payload = request.data.copy()
        username = str(payload.get('username') or '').strip()
        payload.pop('username', None)
        payload['email'] = str(payload.get('email') or instance.email or '').strip().lower()
        payload['phone'] = str(payload.get('phone') or instance.phone or '').strip()
        payload['name'] = str(payload.get('name') or instance.name or '').strip()

        linked_user = getattr(instance, 'user', None)
        if linked_user is not None:
            if username and get_user_model().objects.filter(username=username).exclude(id=linked_user.id).exists():
                return Response({'username': "Ce nom d'utilisateur est déjà utilisé"}, status=status.HTTP_400_BAD_REQUEST)
            if payload.get('email') and get_user_model().objects.filter(email__iexact=payload.get('email')).exclude(id=linked_user.id).exists():
                return Response({'email': 'Cet email est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)

            first_name, last_name = _split_full_name(payload.get('name'))
            linked_user.first_name = first_name
            linked_user.last_name = last_name
            linked_user.email = payload.get('email')
            if username:
                linked_user.username = username
                linked_user.save(update_fields=['first_name', 'last_name', 'email', 'username'])
            else:
                linked_user.save(update_fields=['first_name', 'last_name', 'email'])

        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=_actor(request))
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        denial = self._require_staff_manager(request)
        if denial is not None:
            return denial
        instance = self.get_object()
        linked_user = getattr(instance, 'user', None)
        response = super().destroy(request, *args, **kwargs)
        if linked_user is not None:
            linked_user.delete()
        return response

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('-id')
    serializer_class = MaterialSerializer

    def _emit_stock_notifications(self, material, previous_available=None):
        available = int(material.available_quantity or 0)
        minimum = int(material.minimum_quantity or 0)
        previous = None if previous_available is None else int(previous_available)

        if available <= 0 and (previous is None or previous > 0):
            _create_role_notifications(
                title='Rupture de stock',
                message=f"Rupture de stock : {material.name}.",
                category='out_of_stock',
                type='danger',
                material=material,
            )
            return

        if available <= minimum and available > 0 and (previous is None or previous > minimum or previous <= 0):
            _create_role_notifications(
                title='Alerte stock faible',
                message=f"Alerte stock faible : il reste {available} pour {material.name}.",
                category='low_inventory',
                type='warning',
                material=material,
            )

    def perform_create(self, serializer):
        material = serializer.save(created_by=_actor(self.request), updated_by=_actor(self.request))
        self._emit_stock_notifications(material)

    def perform_update(self, serializer):
        previous_available = getattr(serializer.instance, 'available_quantity', 0)
        material = serializer.save(updated_by=_actor(self.request))
        self._emit_stock_notifications(material, previous_available=previous_available)

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-id')
    serializer_class = ExpenseSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=_actor(self.request), updated_by=_actor(self.request))

    def perform_update(self, serializer):
        serializer.save(updated_by=_actor(self.request))

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-id')
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

    def _emit_payment_received_notification(self, payment):
        if payment.status != 'paid':
            return
        booking = getattr(payment, 'booking', None)
        booking_code = getattr(booking, 'code', '') or f"LBR{getattr(booking, 'id', '')}"
        _create_role_notifications(
            title='Paiement recu',
            message=f"Paiement recu pour la reservation {booking_code}.",
            category='payment_received',
            type='success',
            event_key=f"payment-received-{payment.id}",
            booking=booking,
            payment=payment,
        )

    def _apply_room_action(self, payment, room_action):
        booking = getattr(payment, 'booking', None)
        if not booking or room_action == 'none':
            return
        _sync_room_status_for_booking(booking, room_action)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(created_by=_actor(request), updated_by=_actor(request))
        room_action = getattr(serializer, '_room_action', 'none')
        invoice_email_sent = False

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
        self._apply_room_action(payment, room_action)
        self._emit_payment_received_notification(payment)
        try:
            invoice_email_sent = send_payment_invoice_email(payment)
        except Exception:
            invoice_email_sent = False
        _sync_overdue_notifications()

        output = self.get_serializer(payment)
        response_data = dict(output.data)
        response_data['invoice_email_sent'] = invoice_email_sent
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = kwargs.get('partial', False)
        instance = self.get_object()
        was_paid = instance.status == 'paid'
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs['partial'])
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        payment = serializer.instance
        room_action = getattr(serializer, '_room_action', 'none')
        self._recalc_booking_paid(payment.booking)
        self._apply_room_action(payment, room_action)
        response = Response(self.get_serializer(payment).data)
        if not was_paid and payment.status == 'paid':
            self._emit_payment_received_notification(payment)
            try:
                send_payment_invoice_email(payment)
            except Exception:
                pass
        _sync_overdue_notifications()
        return response

    def perform_update(self, serializer):
        serializer.save(updated_by=_actor(self.request))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking = instance.booking
        response = super().destroy(request, *args, **kwargs)
        self._recalc_booking_paid(booking)
        _sync_overdue_notifications()
        return response
