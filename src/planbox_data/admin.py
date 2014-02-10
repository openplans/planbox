# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from genericadmin.admin import GenericAdminModelAdmin
from planbox_data.models import Profile, Project, Event


class ProfileAdmin (admin.ModelAdmin):
    list_display = ('__unicode__', '_date_joined', 'email')
    filter_horizontal = ('organizations',)
    raw_id_fields = ('auth',)

    def _date_joined(self, obj):
        return obj.created_at
    _date_joined.short_description = _('Date joined')
    _date_joined.admin_order_field = 'created_at'


class EventInline (admin.TabularInline):
    model = Event
    extra = 2
    readonly_fields = ('index',)


class ProjectAdmin (GenericAdminModelAdmin):
    list_display = ('__unicode__', '_permalink', 'owner', 'slug', 'status', 'public')
    list_filter = ('status',)
    prepopulated_fields = {"slug": ("title",)}

    inlines = (
        EventInline,
    )

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        return qs.select_related('owner')

    def _permalink(self, project):
        return format_html(
            '''<a href="{0}" target="_blank">&#8663</a>''',  # 8663 is the ⇗ character
            reverse('app-project', kwargs={'owner_name': project.owner.slug, 'slug': project.slug})
        )
    _permalink.allow_tags = True
    _permalink.short_description = _('Link')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
