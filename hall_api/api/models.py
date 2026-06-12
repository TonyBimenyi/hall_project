from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


def _next_monthly_code(model, prefix, created_at):
    month_year = created_at.strftime('%m%y')
    code_prefix = f"{prefix}{month_year}"
    last_code = (
        model.objects
        .filter(code__startswith=code_prefix)
        .order_by('-code')
        .values_list('code', flat=True)
        .first()
    )

    next_index = 1
    if last_code:
        try:
            next_index = int(str(last_code)[-4:]) + 1
        except (TypeError, ValueError):
            next_index = 1

    return f"{code_prefix}{next_index:04d}"




class Hall(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=12, decimal_places=2)
    additional_services = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_halls')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_halls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    customer_email = models.EmailField(blank=True, default='')
    customer_phone = models.CharField(max_length=30, blank=True, default='')
    event_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    addons_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    additional_services_selected = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    pending_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    auto_cancelled_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_bookings')
    code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = _next_monthly_code(Booking, 'LBR', self.created_at)
        super().save(*args, **kwargs)

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
    phone = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_personnel')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_personnel')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    minimum_quantity = models.IntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='good')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_materials')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_materials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_expenses')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_payments')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_payments')
    code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = _next_monthly_code(Payment, 'LBP', self.created_at)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

class Notification(models.Model):
    TYPE_CHOICES = [
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info'),
    ]
    CATEGORY_CHOICES = [
        ('payment_received', 'Payment Received'),
        ('payment_overdue', 'Payment Overdue'),
        ('low_inventory', 'Low Inventory Warning'),
        ('out_of_stock', 'Out of Stock Warning'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    event_key = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> user_id={self.user_id}"

class MagicLoginToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='magic_login_tokens')
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"MagicLoginToken(user_id={self.user_id}, expires_at={self.expires_at}, used={bool(self.used_at)})"
