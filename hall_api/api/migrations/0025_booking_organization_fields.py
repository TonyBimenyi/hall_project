from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_room_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='customer_kind',
            field=models.CharField(choices=[('individual', 'Particulier'), ('organization', 'Organisation')], default='individual', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='organization_contact_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='booking',
            name='organization_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
