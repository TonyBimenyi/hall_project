from django.db import migrations
from decimal import Decimal


def backfill_tva_room_only(apps, schema_editor):
    Booking = apps.get_model('api', 'Booking')
    rate = Decimal('5.00')
    divisor = Decimal('1.05')
    q = Decimal('0.01')
    updated = []
    for b in Booking.objects.all():
        ttc = Decimal(str(b.total_price or '0.00'))
        booking_type = (getattr(b, 'booking_type', '') or '').strip().lower()
        if booking_type == 'room' and ttc > 0:
            ht = (ttc / divisor).quantize(q)
            tva = (ttc - ht).quantize(q)
            t_rate = rate
        else:
            ht = ttc.quantize(q)
            tva = Decimal('0.00')
            t_rate = rate
        b.subtotal_ht = ht
        b.tva_rate = t_rate
        b.tva_amount = tva
        updated.append(b)
    if updated:
        Booking.objects.bulk_update(updated, ['subtotal_ht', 'tva_rate', 'tva_amount'], batch_size=500)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_booking_subtotal_ht_tva_rate_tva_amount'),
    ]

    operations = [
        migrations.RunPython(backfill_tva_room_only, noop_reverse),
    ]
