from django.contrib import admin
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline
from moonclerk.models import Customer, Payment


class CustomerAdmin (admin.ModelAdmin):
    raw_id_fields = ('user',)


class PaymentAdmin (GenericAdminModelAdmin):
    list_display = ('__str__', 'item')

    raw_id_fields = ('user', 'customer')
    generic_fk_fields = [{
        'ct_field': 'item_type',
        'fk_field': 'item_id',
    }]

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Payment, PaymentAdmin)
