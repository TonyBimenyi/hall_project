from django.contrib import admin
from .models import Hall, Booking, Personnel, Material, Expense, Payment, MagicLoginToken

admin.site.site_header = 'Hall Management'
admin.site.site_title = 'Hall Management'
admin.site.index_title = 'Administration'


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'capacity', 'price_per_day')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'hall',
        'customer_name',
        'customer_email',
        'customer_phone',
        'event_type',
        'start_date',
        'end_date',
        'total_price',
        'paid_amount',
        'status',
        'created_by',
    )
    list_filter = ('status', 'hall', 'start_date', 'end_date')
    search_fields = ('customer_name', 'customer_email', 'event_type', 'hall__name')
    date_hierarchy = 'start_date'
    ordering = ('-start_date', '-id')


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'phone', 'status')
    list_filter = ('status', 'role')
    search_fields = ('name', 'role', 'phone')
    ordering = ('name',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'total_quantity', 'available_quantity', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name', 'category')
    ordering = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'description', 'category', 'amount', 'paid_by', 'paid_to', 'status')
    list_filter = ('status', 'category', 'date')
    search_fields = ('description', 'category', 'paid_by', 'paid_to')
    date_hierarchy = 'date'
    ordering = ('-date', '-id')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'reference', 'booking', 'amount', 'method', 'kind', 'status')
    list_filter = ('status', 'kind', 'method', 'date')
    search_fields = ('reference', 'method', 'booking__customer_name', 'booking__customer_email')
    date_hierarchy = 'date'
    ordering = ('-date', '-id')


@admin.register(MagicLoginToken)
class MagicLoginTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'expires_at', 'used_at', 'created_at')
    list_filter = ('used_at', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'token_hash')
    ordering = ('-created_at', '-id')
