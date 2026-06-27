from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0025_booking_organization_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='room_ids',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
