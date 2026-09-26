from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_course_alter_student_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreasuryAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('kind', models.CharField(choices=[('caisse', 'Caisse'), ('banque', 'Banque')], default='caisse', max_length=20)),
                ('bank_name', models.CharField(blank=True, default='', max_length=120)),
                ('account_number', models.CharField(blank=True, default='', max_length=80)),
                ('initial_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_treasury_accounts', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_treasury_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['kind', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TreasuryOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, editable=False, max_length=20, unique=True)),
                ('operation_type', models.CharField(choices=[('funding', 'Approvisionnement'), ('transfer', 'Transfert interne'), ('withdrawal', 'Retrait')], default='funding', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('date', models.DateField()),
                ('reference', models.CharField(blank=True, default='', max_length=80)),
                ('label', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('paid', 'Validé'), ('pending', 'En attente')], default='paid', max_length=20)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_treasury_operations', to=settings.AUTH_USER_MODEL)),
                ('from_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='operations_out', to='api.treasuryaccount')),
                ('to_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='operations_in', to='api.treasuryaccount')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_treasury_operations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-id'],
            },
        ),
        migrations.AddField(
            model_name='expense',
            name='treasury_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='api.treasuryaccount'),
        ),
        migrations.AddField(
            model_name='entree',
            name='treasury_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entrees', to='api.treasuryaccount'),
        ),
        migrations.AddField(
            model_name='payment',
            name='treasury_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='api.treasuryaccount'),
        ),
    ]
