from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0026_booking_room_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='room_stays',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
