from rest_framework import serializers
from decimal import Decimal
from django.db.models import Q
from .models import Hall, Booking, Personnel, Material, Expense, Entree, Payment, Room, Notification, Customer

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
    room_count = serializers.SerializerMethodField()
    room_stays = serializers.SerializerMethodField()
    pending_room_count = serializers.SerializerMethodField()
    in_house_room_count = serializers.SerializerMethodField()
    completed_room_count = serializers.SerializerMethodField()
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
        if obj.booking_type == 'room':
            return obj.room_display_summary or (str(obj.room) if obj.room else None)
        return None

    def get_room_count(self, obj):
        if obj.booking_type != 'room':
            return 0
        return len(obj.selected_room_ids)

    def get_room_stays(self, obj):
        if obj.booking_type != 'room':
            return []
        room_map = {room.id: room for room in obj.selected_rooms}
        items = []
        for stay in obj.normalized_room_stays:
            room_id = stay.get('room_id')
            room = room_map.get(room_id)
            checked_in_at = stay.get('checked_in_at')
            checked_out_at = stay.get('checked_out_at')
            if checked_in_at and not checked_out_at:
                stay_status = 'occupied'
            elif checked_out_at:
                stay_status = 'cleaning'
            elif str(obj.status or '') == 'paid':
                stay_status = 'reserved'
            else:
                stay_status = 'pending'
            guests = stay.get('guests') or []
            items.append({
                'room_id': room_id,
                'room_display': str(room) if room else '',
                'room_number': getattr(room, 'room_number', ''),
                'room_name': getattr(room, 'name', ''),
                'room_type': getattr(room, 'room_type', ''),
                'room_capacity': getattr(room, 'capacity', 0),
                'room_status': getattr(room, 'status', ''),
                'stay_status': stay_status,
                'checked_in_at': checked_in_at,
                'checked_out_at': checked_out_at,
                'guest_count': len(guests),
                'guests': guests,
                'can_check_in': bool(str(obj.status or '') == 'paid' and not checked_in_at),
                'can_check_out': bool(checked_in_at and not checked_out_at),
            })
        return items

    def get_pending_room_count(self, obj):
        if obj.booking_type != 'room':
            return 0
        return sum(1 for stay in obj.normalized_room_stays if not stay.get('checked_in_at'))

    def get_in_house_room_count(self, obj):
        if obj.booking_type != 'room':
            return 0
        return sum(1 for stay in obj.normalized_room_stays if stay.get('checked_in_at') and not stay.get('checked_out_at'))

    def get_completed_room_count(self, obj):
        if obj.booking_type != 'room':
            return 0
        return sum(1 for stay in obj.normalized_room_stays if stay.get('checked_out_at'))

    def validate(self, data):
        instance = getattr(self, 'instance', None)
        booking_type = data.get('booking_type', getattr(instance, 'booking_type', 'hall'))
        customer_kind = str(data.get('customer_kind', getattr(instance, 'customer_kind', 'individual')) or 'individual').strip() or 'individual'
        hall = data.get('hall', getattr(instance, 'hall', None))
        room = data.get('room', getattr(instance, 'room', None))
        raw_room_ids = data.get('room_ids', getattr(instance, 'room_ids', []))
        organization_name = str(data.get('organization_name', getattr(instance, 'organization_name', '')) or '').strip()
        organization_contact_name = str(data.get('organization_contact_name', getattr(instance, 'organization_contact_name', '')) or '').strip()

        normalized_room_ids = []
        if booking_type == 'room':
            source_ids = raw_room_ids if isinstance(raw_room_ids, list) else []
            for value in source_ids:
                try:
                    room_id = int(value)
                except (TypeError, ValueError):
                    continue
                if room_id not in normalized_room_ids:
                    normalized_room_ids.append(room_id)
            if getattr(room, 'id', None) and room.id not in normalized_room_ids:
                normalized_room_ids.insert(0, room.id)
            if not normalized_room_ids and getattr(room, 'id', None):
                normalized_room_ids = [room.id]
        data['room_ids'] = normalized_room_ids

        if booking_type == 'hall' and not hall:
            raise serializers.ValidationError({'hall': 'Ce champ est obligatoire pour une réservation de salle'})
        if booking_type == 'room' and not normalized_room_ids:
            raise serializers.ValidationError({'room_ids': 'Choisissez au moins une chambre'})
        if booking_type == 'room':
            rooms = list(Room.objects.filter(id__in=normalized_room_ids))
            rooms_map = {item.id: item for item in rooms}
            missing_ids = [room_id for room_id in normalized_room_ids if room_id not in rooms_map]
            if missing_ids:
                raise serializers.ValidationError({'room_ids': 'Une ou plusieurs chambres sélectionnées sont introuvables'})
            ordered_rooms = [rooms_map[room_id] for room_id in normalized_room_ids]
            maintenance_room = next((item for item in ordered_rooms if getattr(item, 'status', '') == 'maintenance'), None)
            if maintenance_room is not None:
                raise serializers.ValidationError({'room_ids': f"La chambre {maintenance_room} est actuellement en maintenance"})
            data['room'] = ordered_rooms[0]
            start_date = data.get('start_date', getattr(instance, 'start_date', None))
            end_date = data.get('end_date', getattr(instance, 'end_date', None))
            if start_date and end_date:
                overlapping_bookings = (
                    Booking.objects
                    .filter(booking_type='room', status__in=['pending', 'confirmed', 'paid'], start_date__lte=end_date, end_date__gte=start_date)
                    .exclude(id=getattr(instance, 'id', None))
                )
                busy_room_ids = set()
                for booking in overlapping_bookings:
                    for booking_room_id in booking.selected_room_ids:
                        busy_room_ids.add(int(booking_room_id))
                conflicts = [rooms_map[room_id] for room_id in normalized_room_ids if room_id in busy_room_ids]
                if conflicts:
                    raise serializers.ValidationError({
                        'room_ids': f"Ces chambres ne sont pas disponibles pour cette période: {', '.join(str(room) for room in conflicts)}"
                    })
            selected_services = data.get('additional_services_selected', getattr(instance, 'additional_services_selected', []))
            if len(normalized_room_ids) != 1 and selected_services:
                raise serializers.ValidationError({
                    'additional_services_selected': 'Les services additionnels sont disponibles uniquement pour une réservation avec une seule chambre'
                })

        if customer_kind == 'organization' and not organization_name:
            raise serializers.ValidationError({'organization_name': "Le nom de l'organisation est requis"})

        if booking_type == 'room':
            guest_full_name = str(data.get('guest_full_name', getattr(instance, 'guest_full_name', '')) or '').strip()
            if customer_kind == 'organization' and organization_contact_name and not guest_full_name:
                data['guest_full_name'] = organization_contact_name

        return data

    def validate_additional_services_selected(self, value):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Les services sélectionnés doivent être une liste')

        def _normalize_quantity(raw_value, *, label):
            if raw_value in (None, ''):
                return 1
            try:
                quantity = int(raw_value)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"Quantité invalide pour '{label}'")
            if quantity < 1:
                raise serializers.ValidationError(f"La quantité doit être supérieure ou égale à 1 pour '{label}'")
            return quantity

        normalized = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Format de service sélectionné invalide')
            name = str(item.get('name') or '').strip()
            if not name:
                raise serializers.ValidationError("Chaque service sélectionné doit avoir un nom")
            quantity = _normalize_quantity(item.get('quantity', 1), label=name)

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
                sub_quantity = _normalize_quantity(sub.get('quantity', 1), label=sub_name)
                normalized_subservices.append({'name': sub_name, 'quantity': sub_quantity})

            payload = {'name': name, 'quantity': quantity}
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
                'room_display': stay.room_display_summary or (str(stay.room) if stay.room else ''),
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
        return bool(obj.booking_type == 'room' and obj.status == 'paid' and any(not stay.get('checked_in_at') for stay in obj.normalized_room_stays))

    def get_can_check_out(self, obj):
        return bool(obj.booking_type == 'room' and any(stay.get('checked_in_at') and not stay.get('checked_out_at') for stay in obj.normalized_room_stays))

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

class EntreeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Entree
        fields = '__all__'

    def get_created_by_name(self, obj):
        return _user_label(getattr(obj, 'created_by', None))

    def get_updated_by_name(self, obj):
        return _user_label(getattr(obj, 'updated_by', None))

    def validate(self, attrs):
        amount = attrs.get('amount', getattr(self.instance, 'amount', None))
        if amount is not None and Decimal(str(amount or 0)) <= 0:
            raise serializers.ValidationError({'amount': 'Le montant doit être supérieur à 0'})
        reference = str(attrs.get('reference', getattr(self.instance, 'reference', '')) or '').strip()
        title = str(attrs.get('title', getattr(self.instance, 'title', '')) or '').strip()
        if not reference:
            raise serializers.ValidationError({'reference': 'La référence est requise'})
        if not title:
            raise serializers.ValidationError({'title': "L'intitulé est requis"})
        return attrs

class PaymentSerializer(serializers.ModelSerializer):
    booking_code = serializers.ReadOnlyField(source='booking.code')
    booking_type = serializers.ReadOnlyField(source='booking.booking_type')
    booking_customer_name = serializers.ReadOnlyField(source='booking.customer_name')
    booking_customer_email = serializers.ReadOnlyField(source='booking.customer_email')
    booking_hall_name = serializers.ReadOnlyField(source='booking.hall.name')
    booking_room_display = serializers.SerializerMethodField()
    booking_room_status = serializers.ReadOnlyField(source='booking.room.status')
    booking_room_count = serializers.SerializerMethodField()
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
        if not booking or booking.booking_type != 'room':
            return None
        return booking.room_display_summary or (str(booking.room) if booking.room else None)

    def get_booking_room_count(self, obj):
        booking = getattr(obj, 'booking', None)
        if not booking or booking.booking_type != 'room':
            return 0
        return len(booking.selected_room_ids)

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
            raise serializers.ValidationError({
                'room_action': "Utilisez la gestion des chambres pour le check-in et le check-out par chambre"
            })

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
