from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_booking_pending_automation_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]

