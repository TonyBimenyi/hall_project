from django.core.management.base import BaseCommand

from api.booking_automation import process_pending_booking_expirations


class Command(BaseCommand):
    help = "Send 2-day pending reminders and auto-cancel pending bookings after 3 days."

    def handle(self, *args, **options):
        result = process_pending_booking_expirations()
        self.stdout.write(
            self.style.SUCCESS(
                f"Pending bookings processed: reminders_sent={result['reminders_sent']}, "
                f"bookings_cancelled={result['bookings_cancelled']}"
            )
        )
