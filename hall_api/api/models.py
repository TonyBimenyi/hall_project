from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

class Hall(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True, default='')
    event_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')

    def __str__(self):
        return f"{self.customer_name} - {self.hall.name}"

class Personnel(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('on_duty', 'En service'),
        ('off_duty', 'En congé'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='personnel_record',
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name

class AccountSecurityProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_profile',
    )
    must_change_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SecurityProfile(user_id={self.user_id}, must_change={self.must_change_password})"

class Material(models.Model):
    STATUS_CHOICES = [
        ('good', 'Bon état'),
        ('damaged', 'Endommagé'),
        ('lost', 'Perdu'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    total_quantity = models.IntegerField()
    damaged_quantity = models.IntegerField(default=0)
    lost_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='good')

    def __str__(self):
        return self.name

class Expense(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Payé'),
        ('pending', 'En attente'),
    ]
    date = models.DateField()
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_by = models.CharField(max_length=100)
    paid_to = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')

    def __str__(self):
        return self.description

class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Complété'),
        ('pending', 'En attente'),
        ('failed', 'Échoué'),
    ]
    KIND_CHOICES = [
        ('advance', 'Avance'),
        ('full', 'Paiement total'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    date = models.DateField()
    reference = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='advance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')

    def __str__(self):
        return self.reference

class MagicLoginToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='magic_login_tokens')
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"MagicLoginToken(user_id={self.user_id}, expires_at={self.expires_at}, used={bool(self.used_at)})"
