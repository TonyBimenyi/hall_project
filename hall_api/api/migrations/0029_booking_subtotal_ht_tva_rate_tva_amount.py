# Generated manually on 2026-08-08 — Add TVA fields to Booking

from decimal import Decimal
from django.db import migrations, models


def backfill_tva_fields(apps, schema_editor):
    Booking = apps.get_model('api', 'Booking')
    rate = Decimal('10.00')
    divisor = Decimal('1.10')
    q = Decimal('0.01')
    updated = []
    for b in Booking.objects.all():
        ttc = Decimal(str(b.total_price or '0.00'))
        if ttc <= 0:
            ht = Decimal('0.00')
            tva = Decimal('0.00')
        else:
            ht = (ttc / divisor).quantize(q)
            tva = (ttc - ht).quantize(q)
        b.subtotal_ht = ht
        b.tva_rate = rate
        b.tva_amount = tva
        updated.append(b)
    if updated:
        Booking.objects.bulk_update(updated, ['subtotal_ht', 'tva_rate', 'tva_amount'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_entree'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='subtotal_ht',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12),
        ),
        migrations.AddField(
            model_name='booking',
            name='tva_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), max_digits=6),
        ),
        migrations.AddField(
            model_name='booking',
            name='tva_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12),
        ),
        migrations.RunPython(backfill_tva_fields, migrations.RunPython.noop),
    ]
