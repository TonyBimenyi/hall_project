import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_room_status_guest_stay_flow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=80)),
                ('last_name', models.CharField(blank=True, default='', max_length=80)),
                ('phone', models.CharField(db_index=True, max_length=30)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('identity_type', models.CharField(blank=True, choices=[('', 'Non renseigné'), ('passport', 'Passeport'), ('id_card', "Carte d'identité"), ('driving_license', 'Permis de conduire'), ('other', 'Autre')], default='', max_length=30)),
                ('identity_number', models.CharField(blank=True, default='', max_length=60)),
                ('address', models.CharField(blank=True, default='', max_length=255)),
                ('notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_customers', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_customers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookings', to='api.customer'),
        ),
    ]
