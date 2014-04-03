# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import TextField
from django.forms import TextInput, Textarea
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django_ace import AceWidget
from genericadmin.admin import GenericAdminModelAdmin
from jsonfield import JSONField
from planbox_data.models import Profile, Project, Event, Theme, Section


class ProfileAdmin (admin.ModelAdmin):
    list_display = ('__str__', '_date_joined', 'affiliation', 'email')
    filter_horizontal = ('organizations',)
    raw_id_fields = ('auth',)

    def _date_joined(self, obj):
        return obj.created_at
    _date_joined.short_description = _('Date joined')
    _date_joined.admin_order_field = 'created_at'


class SectionInline (admin.StackedInline):
    model = Section
    extra = 0
    prepopulated_fields = {"slug": ("menu_label",)}
    readonly_fields = ('created_at', 'updated_at')

    formfield_overrides = {
        TextField: {'widget': TextInput(attrs={'class': 'vTextField'})},
        JSONField: {'widget': Textarea(attrs={'class': 'vLargeTextField'})},
        # JSONField: {'widget': AceWidget(mode='json', theme='github')},
    }


class EventInline (admin.TabularInline):
    model = Event
    extra = 0
    prepopulated_fields = {"slug": ("label",)}
    readonly_fields = ('index',)


class ProjectAdmin (admin.ModelAdmin):
    list_display = ('_title', 'public', 'owner', '_owner_email', 'location', '_updated_at', '_created_at', '_permalink')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-updated_at',)

    inlines = (
        SectionInline,
        EventInline,
    )
    raw_id_fields = ('theme', 'template')

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        return qs.select_related('owner')

    def _permalink(self, project):
        return format_html(
            '''<a href="{0}" target="_blank">Link &#8663</a>''',  # 8663 is the ⇗ character
            reverse('app-project', kwargs={'owner_name': project.owner.slug, 'slug': project.slug})
        )
    _permalink.allow_tags = True
    _permalink.short_description = _('Link')

    def _title(self, project):
        if (len(project.title) + len(project.slug)) > 80:
            template = '{0}<br><small>({1})</small>'
        else:
            template = '{0} <small>({1})</small>'

        return format_html(
            template,
            project.title if project.title != '' else '[No Title]',
            project.slug
        )
    _title.short_description = _('Project')
    _title.admin_order_field = 'title'

    def _owner_email(self, project):
        return  project.owner.email
    _owner_email.short_description = _('Email')

    # Format datetimes
    def _updated_at(self, project):
        return project.updated_at.strftime('%Y-%m-%d %H:%M')
    _updated_at.short_description = _('Updated')
    _updated_at.admin_order_field = 'updated_at'

    def _created_at(self, project):
        return project.created_at.strftime('%Y-%m-%d %H:%M')
    _created_at.short_description = _('Created')
    _created_at.admin_order_field = 'created_at'


class ThemeAdmin (admin.ModelAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Theme, ThemeAdmin)
