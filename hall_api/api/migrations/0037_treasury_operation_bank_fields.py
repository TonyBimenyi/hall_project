from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_treasury_banque_caisse'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasuryoperation',
            name='bank_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='treasuryoperation',
            name='account_number',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
    ]
