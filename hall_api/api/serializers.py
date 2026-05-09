from rest_framework import serializers
from decimal import Decimal
from .models import Hall, Booking, Personnel, Material, Expense, Payment

class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    hall_name = serializers.ReadOnlyField(source='hall.name')
    remaining_amount = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source='created_by_id')
    class Meta:
        model = Booking
        fields = '__all__'

    def get_remaining_amount(self, obj):
        total = obj.total_price or Decimal('0.00')
        paid = obj.paid_amount or Decimal('0.00')
        remaining = total - paid
        if remaining < 0:
            remaining = Decimal('0.00')
        return remaining

class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    booking_customer_name = serializers.ReadOnlyField(source='booking.customer_name')
    booking_customer_email = serializers.ReadOnlyField(source='booking.customer_email')
    booking_hall_name = serializers.ReadOnlyField(source='booking.hall.name')
    booking_event_type = serializers.ReadOnlyField(source='booking.event_type')
    booking_start_date = serializers.ReadOnlyField(source='booking.start_date')
    booking_end_date = serializers.ReadOnlyField(source='booking.end_date')
    booking_total_price = serializers.ReadOnlyField(source='booking.total_price')
    booking_paid_amount = serializers.ReadOnlyField(source='booking.paid_amount')
    booking_remaining_amount = serializers.SerializerMethodField()

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
