from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Booking, Hall, Payment
from .views import _compute_booking_totals


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


class BookingAddonsPricingTests(TestCase):
    def test_compute_totals_with_additional_services(self):
        hall = Hall.objects.create(
            name='Salle Services',
            capacity=100,
            price_per_day='100000.00',
            additional_services=[
                {'name': 'Sonorisation', 'price': '25000.00', 'has_subservices': False, 'subservices': []},
                {'name': 'Décoration', 'price': '0.00', 'has_subservices': True, 'subservices': [
                    {'name': 'Simple', 'price': '30000.00'},
                    {'name': 'Premium', 'price': '60000.00'},
                ]},
            ],
        )

        start = timezone.localdate() + timedelta(days=10)
        end = start + timedelta(days=1)
        selected = [
            {'name': 'Sonorisation'},
            {'name': 'Décoration', 'subservices': [{'name': 'Premium'}]},
        ]

        base_total, addons_total, total, normalized_selected = _compute_booking_totals(hall, start, end, selected)
        self.assertEqual(str(base_total), '200000.00')
        self.assertEqual(str(addons_total), '85000.00')
        self.assertEqual(str(total), '285000.00')
        self.assertEqual(normalized_selected[0]['name'], 'Sonorisation')
        self.assertEqual(normalized_selected[1]['name'], 'Décoration')


class PaymentInvoiceEmailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.hall = Hall.objects.create(
            name='Grande Salle',
            capacity=250,
            price_per_day='150000.00',
        )

    def test_sends_invoice_email_when_new_paid_payment_has_customer_email(self):
        booking = Booking.objects.create(
            hall=self.hall,
            customer_name='Client Test',
            customer_email='client@example.com',
            event_type='Mariage',
            start_date=timezone.localdate() + timedelta(days=10),
            end_date=timezone.localdate() + timedelta(days=11),
            total_price='300000.00',
            status='confirmed',
        )

        response = self.client.post('/api/payments/', {
            'booking': booking.id,
            'date': str(timezone.localdate()),
            'reference': 'REF-EMAIL-001',
            'amount': '100000.00',
            'method': 'Cash',
            'kind': 'advance',
            'status': 'paid',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['invoice_email_sent'])
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['client@example.com'])
        self.assertIn('Recu de paiement', mail.outbox[0].subject)
        self.assertIn(booking.code, mail.outbox[0].subject)
        self.assertIn(booking.code, mail.outbox[0].body)
        self.assertIn('100 000.00 Fbu', mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertIn('text/html', mail.outbox[0].alternatives[0].mime_type)

    def test_skips_invoice_email_when_booking_has_no_customer_email(self):
        booking = Booking.objects.create(
            hall=self.hall,
            customer_name='Client Sans Email',
            customer_email='',
            event_type='Conference',
            start_date=timezone.localdate() + timedelta(days=15),
            end_date=timezone.localdate() + timedelta(days=15),
            total_price='150000.00',
            status='confirmed',
        )

        response = self.client.post('/api/payments/', {
            'booking': booking.id,
            'date': str(timezone.localdate()),
            'reference': 'REF-EMAIL-002',
            'amount': '50000.00',
            'method': 'Cash',
            'kind': 'advance',
            'status': 'paid',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['invoice_email_sent'])
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
