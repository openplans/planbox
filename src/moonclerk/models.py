from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField


@python_2_unicode_compatible
class Customer (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    customer_id = models.PositiveIntegerField(primary_key=True)
    reference = models.CharField(max_length=30, null=True, blank=True)
    data = JSONField(default=dict)

    def __str__(self):
        return str(self.customer_id)


@python_2_unicode_compatible
class Payment (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    payment_id = models.PositiveIntegerField(primary_key=True)
    customer = models.ForeignKey('Customer', null=True, related_name='payments')
    data = JSONField(default=dict)

    item_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True)
    item_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey('item_type', 'item_id')

    def __str__(self):
        return str(self.payment_id)

    def is_onetime(self):
        return bool(self.payment_id)

    def is_recurring(self):
        return bool(self.customer_id)
