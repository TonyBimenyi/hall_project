from django.db import migrations
from django.utils import timezone

def update_codes(apps, schema_editor):
    Booking = apps.get_model('api', 'Booking')
    Payment = apps.get_model('api', 'Payment')
    
    # Update bookings
    for booking in Booking.objects.all():
        date_str = timezone.localdate().strftime('%m%y')
        if booking.created_at:
            date_str = booking.created_at.strftime('%m%y')
        # Use booking.id to ensure uniqueness
        booking.code = f"LBR{date_str}{booking.id:04d}"
        booking.save(update_fields=['code'])
    
    # Update payments
    for payment in Payment.objects.all():
        date_str = timezone.localdate().strftime('%m%y')
        if payment.date:
            date_str = payment.date.strftime('%m%y')
        # Use payment.id to ensure uniqueness
        payment.code = f"LBP{date_str}{payment.id:04d}"
        payment.save(update_fields=['code'])

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_booking_code_alter_payment_code'),
    ]

    operations = [
        migrations.RunPython(update_codes),
    ]