from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_hall_additional_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='additional_services_selected',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='booking',
            name='addons_total',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12),
        ),
    ]

