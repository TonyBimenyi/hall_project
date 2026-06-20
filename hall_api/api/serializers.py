from rest_framework import serializers
from decimal import Decimal
from django.db.models import Q
from .models import Hall, Booking, Personnel, Material, Expense, Payment, Room, Notification, Customer

def _user_label(user):
    if not user:
        return ''
    full = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return full or getattr(user, 'email', '') or getattr(user, 'username', '')

class HallSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = '__all__'

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate_additional_services(self, value):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Les services additionnels doivent être une liste')

        normalized = []
        for service in value:
            if not isinstance(service, dict):
                raise serializers.ValidationError('Format de service invalide')

            name = str(service.get('name') or '').strip()
            has_subservices = bool(service.get('has_subservices'))
            subservices = service.get('subservices') or []

            if not name:
                raise serializers.ValidationError("Chaque service doit avoir un nom")

            if has_subservices:
                if not isinstance(subservices, list) or not subservices:
                    raise serializers.ValidationError(f"Le service '{name}' doit contenir au moins un sous-service")

                normalized_subservices = []
                for subservice in subservices:
                    if not isinstance(subservice, dict):
                        raise serializers.ValidationError(f"Sous-service invalide pour '{name}'")

                    sub_name = str(subservice.get('name') or '').strip()
                    sub_price = subservice.get('price', 0)
                    try:
                        sub_price = Decimal(str(sub_price or 0))
                    except Exception as exc:
                        raise serializers.ValidationError(f"Prix invalide pour un sous-service de '{name}'") from exc
                    if sub_price < 0:
                        raise serializers.ValidationError(f"Le prix d'un sous-service de '{name}' doit être >= 0")
                    if not sub_name:
                        raise serializers.ValidationError(f"Chaque sous-service de '{name}' doit avoir un nom")

                    normalized_subservices.append({
                        'name': sub_name,
                        'price': str(sub_price.quantize(Decimal('0.01'))),
                    })

                normalized.append({
                    'name': name,
                    'price': '0.00',
                    'has_subservices': True,
                    'subservices': normalized_subservices,
                })
                continue

            price = service.get('price', 0)
            try:
                price = Decimal(str(price or 0))
            except Exception as exc:
                raise serializers.ValidationError(f"Prix invalide pour le service '{name}'") from exc
            if price < 0:
                raise serializers.ValidationError(f"Le prix du service '{name}' doit être >= 0")

            normalized.append({
                'name': name,
                'price': str(price.quantize(Decimal('0.01'))),
                'has_subservices': False,
                'subservices': [],
            })

        return normalized

class RoomSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate_additional_services(self, value):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Les services additionnels doivent être une liste')

        normalized = []
        for service in value:
            if not isinstance(service, dict):
                raise serializers.ValidationError('Format de service invalide')

            name = str(service.get('name') or '').strip()
            has_subservices = bool(service.get('has_subservices'))
            subservices = service.get('subservices') or []

            if not name:
                raise serializers.ValidationError("Chaque service doit avoir un nom")

            if has_subservices:
                if not isinstance(subservices, list) or not subservices:
                    raise serializers.ValidationError(f"Le service '{name}' doit contenir au moins un sous-service")

                normalized_subservices = []
                for subservice in subservices:
                    if not isinstance(subservice, dict):
                        raise serializers.ValidationError(f"Sous-service invalide pour '{name}'")

                    sub_name = str(subservice.get('name') or '').strip()
                    sub_price = subservice.get('price', 0)
                    try:
                        sub_price = Decimal(str(sub_price or 0))
                    except Exception as exc:
                        raise serializers.ValidationError(f"Prix invalide pour un sous-service de '{name}'") from exc
                    if sub_price < 0:
                        raise serializers.ValidationError(f"Le prix d'un sous-service de '{name}' doit être >= 0")
                    if not sub_name:
                        raise serializers.ValidationError(f"Chaque sous-service de '{name}' doit avoir un nom")

                    normalized_subservices.append({
                        'name': sub_name,
                        'price': str(sub_price.quantize(Decimal('0.01'))),
                    })

                normalized.append({
                    'name': name,
                    'price': '0.00',
                    'has_subservices': True,
                    'subservices': normalized_subservices,
                })
                continue

            price = service.get('price', 0)
            try:
                price = Decimal(str(price or 0))
            except Exception as exc:
                raise serializers.ValidationError(f"Prix invalide pour le service '{name}'") from exc
            if price < 0:
                raise serializers.ValidationError(f"Le prix du service '{name}' doit être >= 0")

            normalized.append({
                'name': name,
                'price': str(price.quantize(Decimal('0.01'))),
                'has_subservices': False,
                'subservices': [],
            })

        return normalized

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance is None:
            return attrs

        next_status = attrs.get('status', getattr(instance, 'status', 'available'))
        has_active_stay = Booking.objects.filter(
            booking_type='room',
            room=instance,
            status__in=['confirmed', 'paid'],
            checked_in_at__isnull=False,
            checked_out_at__isnull=True,
        ).exists()

        if has_active_stay and next_status != 'occupied':
            raise serializers.ValidationError({
                'status': "Cette chambre a un client en séjour. Effectuez d'abord le check-out."
            })

        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_full_name(self, obj):
        return getattr(obj, 'full_name', '').strip()

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        first_name = str(attrs.get('first_name', getattr(instance, 'first_name', '')) or '').strip()
        last_name = str(attrs.get('last_name', getattr(instance, 'last_name', '')) or '').strip()
        phone = str(attrs.get('phone', getattr(instance, 'phone', '')) or '').strip()
        identity_type = str(attrs.get('identity_type', getattr(instance, 'identity_type', '')) or '').strip()
        identity_number = str(attrs.get('identity_number', getattr(instance, 'identity_number', '')) or '').strip()

        if not first_name and not last_name:
            raise serializers.ValidationError({'first_name': 'Le nom du client est requis'})
        if not phone:
            raise serializers.ValidationError({'phone': 'Le téléphone est requis'})
        if identity_number and not identity_type:
            attrs['identity_type'] = 'other'

        return attrs

class BookingSerializer(serializers.ModelSerializer):
    customer_full_name = serializers.ReadOnlyField(source='customer.full_name')
    customer_profile_phone = serializers.ReadOnlyField(source='customer.phone')
    customer_profile_email = serializers.ReadOnlyField(source='customer.email')
    customer_profile_identity_type = serializers.ReadOnlyField(source='customer.identity_type')
    customer_profile_identity_number = serializers.ReadOnlyField(source='customer.identity_number')
    hall_name = serializers.ReadOnlyField(source='hall.name')
    room_display = serializers.SerializerMethodField()
    room_status = serializers.ReadOnlyField(source='room.status')
    remaining_amount = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source='created_by_id')
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    stay_history = serializers.SerializerMethodField()
    stay_history_count = serializers.SerializerMethodField()
    can_check_in = serializers.SerializerMethodField()
    can_check_out = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_room_display(self, obj):
        if obj.booking_type == 'room' and obj.room:
            return str(obj.room)
        return None

    def validate(self, data):
        instance = getattr(self, 'instance', None)
        booking_type = data.get('booking_type', getattr(instance, 'booking_type', 'hall'))
        hall = data.get('hall', getattr(instance, 'hall', None))
        room = data.get('room', getattr(instance, 'room', None))

        if booking_type == 'hall' and not hall:
            raise serializers.ValidationError({'hall': 'Ce champ est obligatoire pour une réservation de salle'})
        if booking_type == 'room' and not room:
            raise serializers.ValidationError({'room': 'Ce champ est obligatoire pour une réservation de chambre'})
        if booking_type == 'room' and room and getattr(room, 'status', '') == 'maintenance':
            raise serializers.ValidationError({'room': 'Cette chambre est actuellement en maintenance'})

        if booking_type == 'room':
            guest_full_name = str(data.get('guest_full_name', getattr(instance, 'guest_full_name', '')) or '').strip()
            guest_id_type = str(data.get('guest_id_type', getattr(instance, 'guest_id_type', '')) or '').strip()
            guest_id_number = str(data.get('guest_id_number', getattr(instance, 'guest_id_number', '')) or '').strip()
            if not guest_full_name:
                raise serializers.ValidationError({'guest_full_name': 'Le nom complet du client heberge est requis'})
            if not guest_id_type:
                raise serializers.ValidationError({'guest_id_type': 'Le type de piece est requis'})
            if not guest_id_number:
                raise serializers.ValidationError({'guest_id_number': 'Le numero de piece est requis'})

        return data

    def validate_additional_services_selected(self, value):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Les services sélectionnés doivent être une liste')

        normalized = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Format de service sélectionné invalide')
            name = str(item.get('name') or '').strip()
            if not name:
                raise serializers.ValidationError("Chaque service sélectionné doit avoir un nom")

            subservices = item.get('subservices') or []
            if subservices and not isinstance(subservices, list):
                raise serializers.ValidationError(f"Sous-services invalides pour '{name}'")

            normalized_subservices = []
            for sub in subservices:
                if not isinstance(sub, dict):
                    raise serializers.ValidationError(f"Sous-service invalide pour '{name}'")
                sub_name = str(sub.get('name') or '').strip()
                if not sub_name:
                    raise serializers.ValidationError(f"Chaque sous-service de '{name}' doit avoir un nom")
                normalized_subservices.append({'name': sub_name})

            payload = {'name': name}
            if normalized_subservices:
                payload['subservices'] = normalized_subservices
            normalized.append(payload)

        return normalized

    def get_remaining_amount(self, obj):
        total = obj.total_price or Decimal('0.00')
        paid = obj.paid_amount or Decimal('0.00')
        remaining = total - paid
        if remaining < 0:
            remaining = Decimal('0.00')
        return remaining

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def get_stay_history(self, obj):
        if obj.booking_type != 'room':
            return []

        filters = Q()
        guest_id_number = str(getattr(obj, 'guest_id_number', '') or '').strip()
        guest_full_name = str(getattr(obj, 'guest_full_name', '') or '').strip()
        customer_email = str(getattr(obj, 'customer_email', '') or '').strip()

        if guest_id_number:
            filters |= Q(guest_id_number__iexact=guest_id_number)
        if guest_full_name:
            filters |= Q(guest_full_name__iexact=guest_full_name)
        if customer_email:
            filters |= Q(customer_email__iexact=customer_email)

        if not filters:
            return []

        stays = (
            Booking.objects
            .filter(filters, booking_type='room')
            .exclude(id=obj.id)
            .exclude(status='cancelled')
            .select_related('room')
            .order_by('-start_date', '-id')[:5]
        )
        return [
            {
                'id': stay.id,
                'code': stay.code,
                'room_display': str(stay.room) if stay.room else '',
                'start_date': stay.start_date.isoformat() if stay.start_date else None,
                'end_date': stay.end_date.isoformat() if stay.end_date else None,
                'status': stay.status,
                'checked_in_at': stay.checked_in_at.isoformat() if stay.checked_in_at else None,
                'checked_out_at': stay.checked_out_at.isoformat() if stay.checked_out_at else None,
            }
            for stay in stays
        ]

    def get_stay_history_count(self, obj):
        return len(self.get_stay_history(obj))

    def get_can_check_in(self, obj):
        return bool(obj.booking_type == 'room' and not obj.checked_in_at and obj.status == 'paid')

    def get_can_check_out(self, obj):
        return bool(obj.booking_type == 'room' and obj.checked_in_at and not obj.checked_out_at)

class PersonnelSerializer(serializers.ModelSerializer):
    has_account = serializers.SerializerMethodField()
    account_username = serializers.SerializerMethodField()
    must_change_password = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Personnel
        fields = '__all__'

    def get_has_account(self, obj):
        return bool(getattr(obj, 'user_id', None))

    def get_account_username(self, obj):
        return getattr(getattr(obj, 'user', None), 'username', '')

    def get_must_change_password(self, obj):
        security = getattr(getattr(obj, 'user', None), 'security_profile', None)
        return bool(getattr(security, 'must_change_password', False))

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

class MaterialSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    def _normalize_and_recalc(self, attrs, instance=None):
        total = attrs.get('total_quantity', getattr(instance, 'total_quantity', 0))
        damaged = attrs.get('damaged_quantity', getattr(instance, 'damaged_quantity', 0))
        lost = attrs.get('lost_quantity', getattr(instance, 'lost_quantity', 0))

        try:
            total = int(total)
            damaged = int(damaged)
            lost = int(lost)
        except (TypeError, ValueError):
            raise serializers.ValidationError('Quantités invalides')

        if total < 0:
            raise serializers.ValidationError({'total_quantity': 'Doit être >= 0'})
        if damaged < 0:
            raise serializers.ValidationError({'damaged_quantity': 'Doit être >= 0'})
        if lost < 0:
            raise serializers.ValidationError({'lost_quantity': 'Doit être >= 0'})
        if damaged + lost > total:
            raise serializers.ValidationError({'non_field_errors': 'Endommagé + Perdu ne peut pas dépasser le total'})

        available = total - damaged - lost
        attrs['available_quantity'] = available

        if lost == total and total > 0:
            attrs['status'] = 'lost'
        elif damaged > 0:
            attrs['status'] = 'damaged'
        else:
            attrs['status'] = 'good'

        return attrs

    def validate(self, attrs):
        return self._normalize_and_recalc(attrs, instance=self.instance)

    def create(self, validated_data):
        validated_data = self._normalize_and_recalc(validated_data, instance=None)
        if 'damaged_quantity' not in validated_data:
            validated_data['damaged_quantity'] = 0
        if 'lost_quantity' not in validated_data:
            validated_data['lost_quantity'] = 0
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._normalize_and_recalc(validated_data, instance=instance)
        return super().update(instance, validated_data)

    class Meta:
        model = Material
        fields = '__all__'

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

class ExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

class PaymentSerializer(serializers.ModelSerializer):
    booking_code = serializers.ReadOnlyField(source='booking.code')
    booking_type = serializers.ReadOnlyField(source='booking.booking_type')
    booking_customer_name = serializers.ReadOnlyField(source='booking.customer_name')
    booking_customer_email = serializers.ReadOnlyField(source='booking.customer_email')
    booking_hall_name = serializers.ReadOnlyField(source='booking.hall.name')
    booking_room_display = serializers.SerializerMethodField()
    booking_room_status = serializers.ReadOnlyField(source='booking.room.status')
    booking_guest_full_name = serializers.ReadOnlyField(source='booking.guest_full_name')
    booking_guest_id_type = serializers.ReadOnlyField(source='booking.guest_id_type')
    booking_guest_id_number = serializers.ReadOnlyField(source='booking.guest_id_number')
    booking_checked_in_at = serializers.ReadOnlyField(source='booking.checked_in_at')
    booking_checked_out_at = serializers.ReadOnlyField(source='booking.checked_out_at')
    booking_event_type = serializers.ReadOnlyField(source='booking.event_type')
    booking_start_date = serializers.ReadOnlyField(source='booking.start_date')
    booking_end_date = serializers.ReadOnlyField(source='booking.end_date')
    booking_total_price = serializers.ReadOnlyField(source='booking.total_price')
    booking_paid_amount = serializers.ReadOnlyField(source='booking.paid_amount')
    booking_remaining_amount = serializers.SerializerMethodField()
    room_action = serializers.ChoiceField(
        choices=[('none', 'Aucune action'), ('check_in', 'Check-in'), ('check_out', 'Check-out')],
        required=False,
        write_only=True,
        default='none',
    )
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_booking_remaining_amount(self, obj):
        total = obj.booking.total_price or Decimal('0.00')
        paid = obj.booking.paid_amount or Decimal('0.00')
        remaining = total - paid
        if remaining < 0:
            remaining = Decimal('0.00')
        return remaining

    def get_booking_room_display(self, obj):
        booking = getattr(obj, 'booking', None)
        if not booking or booking.booking_type != 'room' or not booking.room:
            return None
        return str(booking.room)

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate(self, attrs):
        booking = attrs.get('booking') or getattr(self.instance, 'booking', None)
        amount = attrs.get('amount')
        status = attrs.get('status', getattr(self.instance, 'status', 'paid'))
        room_action = attrs.get('room_action', 'none')

        if booking is None:
            raise serializers.ValidationError({'booking': 'Réservation requise'})
        if booking.status == 'cancelled':
            raise serializers.ValidationError({'booking': 'Impossible de payer une réservation annulée'})
        if amount is None:
            return attrs
        if amount <= 0:
            raise serializers.ValidationError({'amount': 'Le montant doit être supérieur à 0'})

        total = booking.total_price or Decimal('0.00')
        paid = booking.paid_amount or Decimal('0.00')
        remaining = total - paid
        if remaining < 0:
            remaining = Decimal('0.00')

        if status == 'paid' and amount > remaining:
            raise serializers.ValidationError({'amount': 'Le montant dépasse le reste à payer'})

        if room_action != 'none':
            if booking.booking_type != 'room':
                raise serializers.ValidationError({'room_action': 'Cette action est réservée aux réservations de chambre'})
            if status != 'paid':
                raise serializers.ValidationError({'room_action': 'Le paiement doit être marqué comme payé pour gérer le séjour'})
            if room_action == 'check_in':
                if booking.checked_in_at:
                    raise serializers.ValidationError({'room_action': 'Le check-in a déjà été effectué'})
                if not str(booking.guest_full_name or '').strip() or not str(booking.guest_id_type or '').strip() or not str(booking.guest_id_number or '').strip():
                    raise serializers.ValidationError({'room_action': 'Complétez le profil client et la pièce d’identité avant le check-in'})
            if room_action == 'check_out':
                if not booking.checked_in_at:
                    raise serializers.ValidationError({'room_action': 'Le check-in doit être effectué avant le check-out'})
                if booking.checked_out_at:
                    raise serializers.ValidationError({'room_action': 'Le check-out a déjà été effectué'})
                if amount is None or amount < remaining:
                    raise serializers.ValidationError({'room_action': 'Le séjour doit être soldé avant le check-out'})

        return attrs

    def create(self, validated_data):
        self._room_action = validated_data.pop('room_action', 'none')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._room_action = validated_data.pop('room_action', 'none')
        return super().update(instance, validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    booking_code = serializers.ReadOnlyField(source='booking.code')
    payment_code = serializers.ReadOnlyField(source='payment.code')
    material_name = serializers.ReadOnlyField(source='material.name')

    class Meta:
        model = Notification
        fields = '__all__'
