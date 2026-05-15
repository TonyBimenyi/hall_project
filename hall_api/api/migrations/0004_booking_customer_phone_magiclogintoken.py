from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_booking_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='customer_phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.CreateModel(
            name='MagicLoginToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField()),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='magic_login_tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
