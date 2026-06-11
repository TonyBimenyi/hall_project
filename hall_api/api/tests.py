from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import Booking, Hall
from .views import _send_reservation_email


class PendingBookingAutomationTests(TestCase):
    def setUp(self):
        self.hall = Hall.objects.create(
            name='Grande Salle',
            capacity=250,
            price_per_day='150000.00',
        )

    def test_sends_pending_reminder_after_two_days(self):
        booking = Booking.objects.create(
            hall=self.hall,
            customer_name='Client Test',
            customer_email='client@example.com',
            event_type='Mariage',
            start_date=timezone.localdate() + timedelta(days=10),
            end_date=timezone.localdate() + timedelta(days=12),
            total_price='450000.00',
            status='pending',
            created_at=timezone.now() - timedelta(days=2, hours=1),
        )

        call_command('process_pending_bookings')

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'pending')
        self.assertIsNotNone(booking.pending_reminder_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('attend toujours une confirmation', mail.outbox[0].subject)
        self.assertIn(str(booking.id), mail.outbox[0].body)

    def test_auto_cancels_pending_booking_after_three_days(self):
        booking = Booking.objects.create(
            hall=self.hall,
            customer_name='Client Test',
            customer_email='client@example.com',
            event_type='Séminaire',
            start_date=timezone.localdate() + timedelta(days=10),
            end_date=timezone.localdate() + timedelta(days=10),
            total_price='150000.00',
            status='pending',
            created_at=timezone.now() - timedelta(days=3, hours=1),
        )

        call_command('process_pending_bookings')

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertIsNotNone(booking.auto_cancelled_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Annulation automatique', mail.outbox[0].subject)
        self.assertIn(str(booking.id), mail.outbox[0].body)


class ReservationEmailAttachmentTests(TestCase):
    def setUp(self):
        self.hall = Hall.objects.create(
            name='Salle Prestige',
            capacity=180,
            price_per_day='200000.00',
        )

    def test_reservation_email_attaches_printable_jeton_pdf(self):
        booking = Booking.objects.create(
            hall=self.hall,
            customer_name='Alice Client',
            customer_email='alice@example.com',
            event_type='Gala',
            start_date=timezone.localdate() + timedelta(days=7),
            end_date=timezone.localdate() + timedelta(days=8),
            total_price='400000.00',
            status='pending',
        )

        _send_reservation_email(
            to_email='alice@example.com',
            full_name='Alice Client',
            booking=booking,
            magic_url='http://localhost:3000/login?token=test-token',
            account_created=False,
        )

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['alice@example.com'])
        self.assertEqual(len(email.attachments), 1)
        filename, content, mimetype = email.attachments[0]
        self.assertEqual(filename, f'jeton-reservation-{booking.id}.pdf')
        self.assertEqual(mimetype, 'application/pdf')
        self.assertTrue(content.startswith(b'%PDF'))
