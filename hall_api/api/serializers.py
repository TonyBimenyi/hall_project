from rest_framework import serializers
from decimal import Decimal
from .models import Hall, Booking, Personnel, Material, Expense, Payment, Notification

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

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

class BookingSerializer(serializers.ModelSerializer):
    hall_name = serializers.ReadOnlyField(source='hall.name')
    remaining_amount = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source='created_by_id')
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    class Meta:
        model = Booking
        fields = '__all__'

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
    booking_customer_name = serializers.ReadOnlyField(source='booking.customer_name')
    booking_customer_email = serializers.ReadOnlyField(source='booking.customer_email')
    booking_hall_name = serializers.ReadOnlyField(source='booking.hall.name')
    booking_event_type = serializers.ReadOnlyField(source='booking.event_type')
    booking_start_date = serializers.ReadOnlyField(source='booking.start_date')
    booking_end_date = serializers.ReadOnlyField(source='booking.end_date')
    booking_total_price = serializers.ReadOnlyField(source='booking.total_price')
    booking_paid_amount = serializers.ReadOnlyField(source='booking.paid_amount')
    booking_remaining_amount = serializers.SerializerMethodField()
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

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate(self, attrs):
        booking = attrs.get('booking') or getattr(self.instance, 'booking', None)
        amount = attrs.get('amount')
        status = attrs.get('status', getattr(self.instance, 'status', 'paid'))

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

        return attrs

class NotificationSerializer(serializers.ModelSerializer):
    booking_code = serializers.ReadOnlyField(source='booking.code')
    payment_code = serializers.ReadOnlyField(source='payment.code')
    material_name = serializers.ReadOnlyField(source='material.name')

    class Meta:
        model = Notification
        fields = '__all__'
