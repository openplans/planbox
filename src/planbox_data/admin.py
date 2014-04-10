# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import TextField
from django.forms import TextInput, Textarea
from django.forms.models import inlineformset_factory, modelform_factory
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django_ace import AceWidget
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline
from jsonfield import JSONField
from planbox_data.models import Profile, Project, Event, Theme, Section, Attachment


class AttachmentAdmin (GenericAdminModelAdmin):
    pass


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


class AttachmentInline (GenericTabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('index',)
    ct_field = 'attached_to_type'
    ct_fk_field = 'attached_to_id'
    exclude = ('created_at', 'updated_at')
    form = modelform_factory(Attachment, widgets={
        'label': TextInput(),
    })


class EventAdmin (admin.ModelAdmin):
    list_display = ('label', 'project', 'index')
    inlines = (
        AttachmentInline,
    )
    raw_id_fields = ('project',)
    form = modelform_factory(Event, widgets={
        'label': TextInput(attrs={'class': 'vTextField'}),
        'datetime_label': TextInput(attrs={'class': 'vTextField'})
    })


class EventInline (admin.StackedInline):
    model = Event
    extra = 0
    prepopulated_fields = {"slug": ("label",)}
    readonly_fields = ('index',)

    form = modelform_factory(Event, widgets={
        'label': TextInput(attrs={'class': 'vTextField'}),
        'datetime_label': TextInput(attrs={'class': 'vTextField'})
    })


class ProjectAdmin (admin.ModelAdmin):
    list_display = ('_title', 'public', 'owner', '_owner_email', '_owner_affiliation', 'location', '_updated_at', '_created_at', '_permalink')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-updated_at',)

    inlines = (
        SectionInline,
        EventInline,
    )
    raw_id_fields = ('theme', 'template')
    form = modelform_factory(Project, widgets={
        'title': TextInput(attrs={'class': 'vTextField'}),
        'location': TextInput(attrs={'class': 'vTextField'}),
        'happening_now_description': TextInput(attrs={'class': 'vTextField'}),
        'get_involved_description': TextInput(attrs={'class': 'vTextField'}),
    })

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
        return format_html(
            '{0} <small style="white-space:nowrap">({1})</small>',
            project.title if project.title != '' else '[No Title]',
            project.slug
        )
    _title.short_description = _('Project')
    _title.admin_order_field = 'title'

    def _owner_email(self, project):
        return  project.owner.email
    _owner_email.short_description = _('Email')
    _owner_email.admin_order_field = 'owner__email'

    def _owner_affiliation(self, project):
        return project.owner.affiliation
    _owner_affiliation.short_description = _('Affiliation')
    _owner_affiliation.admin_order_field = 'owner__affiliation'

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
admin.site.register(Event, EventAdmin)
admin.site.register(Attachment, AttachmentAdmin)
