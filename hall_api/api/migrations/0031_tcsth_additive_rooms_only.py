from django.db import migrations
from decimal import Decimal


def backfill_tcsth_additive(apps, schema_editor):
    Booking = apps.get_model('api', 'Booking')
    rate = Decimal('5.00')
    mult = Decimal('0.05')
    q = Decimal('0.01')
    updated = []
    for b in Booking.objects.all():
        booking_type = (getattr(b, 'booking_type', '') or '').strip().lower()
        total_price = Decimal(str(b.total_price or '0.00'))
        addons_total = Decimal(str(getattr(b, 'addons_total', 0) or '0.00'))
        if booking_type == 'room':
            # total_price original: TTC before TCSTH additive
            # base accommodation HT = total_price (before migration) minus addons
            base_accomodation_ht = (total_price - addons_total).quantize(q)
            if base_accomodation_ht < 0:
                base_accomodation_ht = Decimal('0.00')
            tcsth_amount = (base_accomodation_ht * mult).quantize(q)
            # New total = total_price (base+addons) + TCSTH
            new_total = (total_price + tcsth_amount).quantize(q)
            subtotal_ht = total_price.quantize(q)  # rooms HT + addons (no tax on addons)
            tva_rate = rate
        else:
            tcsth_amount = Decimal('0.00')
            new_total = total_price.quantize(q)
            subtotal_ht = total_price.quantize(q)
            tva_rate = rate
        b.total_price = new_total
        b.subtotal_ht = subtotal_ht
        b.tva_rate = tva_rate
        b.tva_amount = tcsth_amount
        updated.append(b)
    if updated:
        Booking.objects.bulk_update(updated, ['total_price', 'subtotal_ht', 'tva_rate', 'tva_amount'], batch_size=500)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_tva_5pct_hotel_only'),
    ]

    operations = [
        migrations.RunPython(backfill_tcsth_additive, noop_reverse),
    ]
