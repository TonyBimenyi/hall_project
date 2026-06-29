from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_booking_room_stays'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reference', models.CharField(max_length=80)),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(blank=True, default='Autre', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('received_from', models.CharField(blank=True, default='', max_length=120)),
                ('received_by', models.CharField(blank=True, default='', max_length=120)),
                ('notes', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('paid', 'Validee'), ('pending', 'En attente')], default='paid', max_length=20)),
                ('code', models.CharField(blank=True, editable=False, max_length=20, unique=True)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_entrees', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_entrees', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
