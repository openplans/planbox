from django.contrib import admin
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from password_reset.models import PasswordResetRequest


class FreshnessFilter (admin.SimpleListFilter):
    title = _('freshness')
    parameter_name = 'fresh'

    def lookups(self, request, model_admin):
        return [
            ('yes', _('Fresh')),
            ('no', _('Expired'))]

    def queryset(self, request, qs):
        if self.value() == 'yes':
            return qs.filter(expires_at__gt=now())
        elif self.value() == 'no':
            return qs.filter(expires_at__lte=now())
        else:
            return qs


class PasswordResetRequestAdmin (admin.ModelAdmin):
    list_display = ('auth', 'requested_at', '_expired')
    list_filter = (FreshnessFilter,)
    raw_id_fields = ('auth',)

    def _expired(self, obj):
        return obj.is_expired()
    _expired.short_description = _('Is expired?')
    _expired.boolean = True


admin.site.register(PasswordResetRequest, PasswordResetRequestAdmin)