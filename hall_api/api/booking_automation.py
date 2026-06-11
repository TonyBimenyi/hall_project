from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Booking


def _booking_status_label(status_value: str) -> str:
    return {
        'pending': 'En attente',
        'confirmed': 'Confirmé',
        'paid': 'Payé',
        'cancelled': 'Annulé',
    }.get(status_value, status_value or '')


def _send_pending_confirmation_reminder_email(booking: Booking) -> None:
    email = (getattr(booking, 'customer_email', '') or '').strip()
    if not email:
        return

    subject = 'Rappel: votre réservation attend toujours une confirmation'
    body = (
        f"Bonjour {booking.customer_name},\n\n"
        "Votre réservation est toujours en attente de confirmation.\n"
        "Il vous reste 1 jour avant son annulation automatique si elle n'est pas confirmée.\n\n"
        "Détails de la réservation :\n"
        f"- ID de réservation : {booking.id}\n"
        f"- Salle : {booking.hall.name}\n"
        f"- Type d'événement : {booking.event_type}\n"
        f"- Date début : {booking.start_date}\n"
        f"- Date fin : {booking.end_date}\n"
        f"- Statut : {_booking_status_label(booking.status)}\n\n"
        "Merci de prendre contact avec LaBertha Villa ou de finaliser les démarches nécessaires avant l'expiration.\n"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@hall.local',
        recipient_list=[email],
        fail_silently=False,
    )


def _send_auto_cancellation_email(booking: Booking) -> None:
    email = (getattr(booking, 'customer_email', '') or '').strip()
    if not email:
        return

    subject = 'Annulation automatique de votre réservation'
    body = (
        f"Bonjour {booking.customer_name},\n\n"
        "Votre réservation a été annulée automatiquement car elle est restée en attente de confirmation pendant 3 jours.\n\n"
        "Détails de la réservation :\n"
        f"- ID de réservation : {booking.id}\n"
        f"- Salle : {booking.hall.name}\n"
        f"- Type d'événement : {booking.event_type}\n"
        f"- Date début : {booking.start_date}\n"
        f"- Date fin : {booking.end_date}\n"
        f"- Statut : {_booking_status_label('cancelled')}\n\n"
        "Si vous souhaitez réserver à nouveau, merci de contacter LaBertha Villa.\n"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@hall.local',
        recipient_list=[email],
        fail_silently=False,
    )


def process_pending_booking_expirations(now=None):
    now = now or timezone.now()
    reminder_cutoff = now - timedelta(days=2)
    cancellation_cutoff = now - timedelta(days=3)

    reminder_count = 0
    cancelled_count = 0

    reminder_bookings = Booking.objects.select_related('hall').filter(
        status='pending',
        created_at__lte=reminder_cutoff,
        created_at__gt=cancellation_cutoff,
        pending_reminder_sent_at__isnull=True,
    )

    for booking in reminder_bookings:
        if (getattr(booking, 'customer_email', '') or '').strip():
            _send_pending_confirmation_reminder_email(booking)
            booking.pending_reminder_sent_at = now
            booking.save(update_fields=['pending_reminder_sent_at'])
            reminder_count += 1

    cancellation_bookings = Booking.objects.select_related('hall').filter(
        status='pending',
        created_at__lte=cancellation_cutoff,
    )

    for booking in cancellation_bookings:
        booking.status = 'cancelled'
        booking.auto_cancelled_at = now
        booking.save(update_fields=['status', 'auto_cancelled_at'])
        if (getattr(booking, 'customer_email', '') or '').strip():
            _send_auto_cancellation_email(booking)
        cancelled_count += 1

    return {
        'reminders_sent': reminder_count,
        'bookings_cancelled': cancelled_count,
    }
