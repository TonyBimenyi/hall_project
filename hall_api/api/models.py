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

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('twin', 'Twin'),
        ('suite', 'Suite'),
        ('family', 'Family'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('cleaning', 'Cleaning'),
        ('maintenance', 'Maintenance'),
    ]
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    additional_services = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_rooms')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def room_type_label(self):
        mapping = {
            'single': 'Simple',
            'double': 'Double',
            'twin': 'Twin',
            'suite': 'Suite',
            'family': 'Familiale',
            'Single': 'Simple',
            'Double': 'Double',
            'Twin': 'Twin',
            'Suite': 'Suite',
            'Family': 'Familiale',
        }
        return mapping.get(self.room_type, self.room_type)

    def __str__(self):
        return f"{self.room_number} - {self.name} ({self.room_type_label})"


class Customer(models.Model):
    IDENTITY_TYPE_CHOICES = [
        ('', 'Non renseigné'),
        ('passport', 'Passeport'),
        ('id_card', "Carte d'identité"),
        ('driving_license', 'Permis de conduire'),
        ('other', 'Autre'),
    ]

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True, default='')
    phone = models.CharField(max_length=30, db_index=True)
    email = models.EmailField(blank=True, default='')
    identity_type = models.CharField(max_length=30, choices=IDENTITY_TYPE_CHOICES, blank=True, default='')
    identity_number = models.CharField(max_length=60, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_customers')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name or self.phone


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]
    CUSTOMER_KIND_CHOICES = [
        ('individual', 'Particulier'),
        ('organization', 'Organisation'),
    ]
    BOOKING_TYPE_CHOICES = [
        ('hall', 'Salle'),
        ('room', 'Chambre'),
    ]
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='hall')
    customer_kind = models.CharField(max_length=20, choices=CUSTOMER_KIND_CHOICES, default='individual')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    room_ids = models.JSONField(default=list, blank=True)
    room_stays = models.JSONField(default=list, blank=True)
    organization_name = models.CharField(max_length=150, blank=True, default='')
    organization_contact_name = models.CharField(max_length=120, blank=True, default='')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True, default='')
    customer_phone = models.CharField(max_length=30, blank=True, default='')
    guest_full_name = models.CharField(max_length=120, blank=True, default='')
    guest_id_type = models.CharField(max_length=30, blank=True, default='')
    guest_id_number = models.CharField(max_length=60, blank=True, default='')
    event_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
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
        if self.booking_type != 'room':
            self.room = None
            self.room_ids = []
            self.room_stays = []
        else:
            normalized = []
            raw_ids = self.room_ids if isinstance(self.room_ids, list) else []
            for value in raw_ids:
                try:
                    room_id = int(value)
                except (TypeError, ValueError):
                    continue
                if room_id not in normalized:
                    normalized.append(room_id)
            if self.room_id and self.room_id not in normalized:
                normalized.insert(0, self.room_id)
            self.room_ids = normalized
            if normalized and not self.room_id:
                self.room_id = normalized[0]
            existing_stays = {}
            raw_stays = self.room_stays if isinstance(self.room_stays, list) else []
            for item in raw_stays:
                if not isinstance(item, dict):
                    continue
                try:
                    stay_room_id = int(item.get('room_id'))
                except (TypeError, ValueError):
                    continue
                guests = item.get('guests') if isinstance(item.get('guests'), list) else []
                existing_stays[stay_room_id] = {
                    'room_id': stay_room_id,
                    'checked_in_at': item.get('checked_in_at') or None,
                    'checked_out_at': item.get('checked_out_at') or None,
                    'guests': [
                        {
                            'full_name': str(guest.get('full_name') or '').strip(),
                            'id_type': str(guest.get('id_type') or '').strip(),
                            'id_number': str(guest.get('id_number') or '').strip(),
                        }
                        for guest in guests
                        if isinstance(guest, dict) and str(guest.get('full_name') or '').strip()
                    ],
                }
            self.room_stays = [
                existing_stays.get(room_id, {
                    'room_id': room_id,
                    'checked_in_at': None,
                    'checked_out_at': None,
                    'guests': [],
                })
                for room_id in normalized
            ]
        super().save(*args, **kwargs)

    @property
    def selected_room_ids(self):
        ids = []
        raw_ids = self.room_ids if isinstance(self.room_ids, list) else []
        for value in raw_ids:
            try:
                room_id = int(value)
            except (TypeError, ValueError):
                continue
            if room_id not in ids:
                ids.append(room_id)
        if self.room_id and self.room_id not in ids:
            ids.insert(0, self.room_id)
        return ids

    @property
    def selected_rooms(self):
        room_ids = self.selected_room_ids
        if not room_ids:
            return []
        room_map = {room.id: room for room in Room.objects.filter(id__in=room_ids)}
        return [room_map[room_id] for room_id in room_ids if room_id in room_map]

    @property
    def room_display_summary(self):
        if self.booking_type != 'room':
            return ''
        labels = [str(room) for room in self.selected_rooms]
        if not labels and self.room:
            labels = [str(self.room)]
        return ', '.join(labels)

    @property
    def normalized_room_stays(self):
        stays = self.room_stays if isinstance(self.room_stays, list) else []
        stay_map = {}
        for item in stays:
            if not isinstance(item, dict):
                continue
            try:
                room_id = int(item.get('room_id'))
            except (TypeError, ValueError):
                continue
            guests = item.get('guests') if isinstance(item.get('guests'), list) else []
            stay_map[room_id] = {
                'room_id': room_id,
                'checked_in_at': item.get('checked_in_at') or None,
                'checked_out_at': item.get('checked_out_at') or None,
                'guests': [
                    {
                        'full_name': str(guest.get('full_name') or '').strip(),
                        'id_type': str(guest.get('id_type') or '').strip(),
                        'id_number': str(guest.get('id_number') or '').strip(),
                    }
                    for guest in guests
                    if isinstance(guest, dict) and str(guest.get('full_name') or '').strip()
                ],
            }
        return [
            stay_map.get(room_id, {
                'room_id': room_id,
                'checked_in_at': None,
                'checked_out_at': None,
                'guests': [],
            })
            for room_id in self.selected_room_ids
        ]

    @property
    def representative_guest(self):
        for stay in self.normalized_room_stays:
            guests = stay.get('guests') or []
            if guests:
                return guests[0]
        return {}

    @property
    def booked_item_name(self):
        if self.booking_type == 'hall' and self.hall:
            return self.hall.name
        elif self.booking_type == 'room':
            return self.room_display_summary or (str(self.room) if self.room else '')
        return 'Non spécifié'

    @property
    def active_guest_name(self):
        representative = self.representative_guest
        if representative:
            return str(representative.get('full_name') or '').strip() or (self.organization_contact_name or '').strip() or (self.customer_name or '').strip()
        if self.customer_kind == 'organization':
            return (self.organization_contact_name or '').strip() or (self.guest_full_name or '').strip() or (self.customer_name or '').strip()
        return (self.guest_full_name or '').strip() or (self.customer_name or '').strip()

    def __str__(self):
        return f"{self.customer_name} - {self.booked_item_name}"

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
