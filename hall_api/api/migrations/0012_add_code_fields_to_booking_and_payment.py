from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_booking_additional_services_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='code',
            field=models.CharField(max_length=20, unique=True, editable=False, default='LBR00000000'),
        ),
        migrations.AddField(
            model_name='payment',
            name='code',
            field=models.CharField(max_length=20, unique=True, editable=False, default='LBP00000000'),
        ),
    ]
