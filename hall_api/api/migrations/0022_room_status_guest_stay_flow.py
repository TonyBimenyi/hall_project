from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_room_booking_updates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='floor',
        ),
        migrations.AddField(
            model_name='room',
            name='status',
            field=models.CharField(
                choices=[
                    ('available', 'Available'),
                    ('occupied', 'Occupied'),
                    ('cleaning', 'Cleaning'),
                    ('maintenance', 'Maintenance'),
                ],
                default='available',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='checked_in_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='checked_out_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='guest_full_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='booking',
            name='guest_id_number',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
        migrations.AddField(
            model_name='booking',
            name='guest_id_type',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
