from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_audit_fields_and_optional_booking_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='auto_cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='booking',
            name='pending_reminder_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
