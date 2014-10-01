# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from django.contrib.gis import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import TextField
from django.http import HttpResponseRedirect
from django.forms import TextInput, Textarea
from django.forms.models import inlineformset_factory, modelform_factory
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django_ace import AceWidget
from django_object_actions import DjangoObjectActions
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline
from jsonfield import JSONField
from planbox_data.models import Profile, ProfileProjectTemplate, Roundup, Project, Event, Theme, Section, Attachment


class PrettyAceWidget (AceWidget):
    def render(self, name, value, attrs=None):
        if value:
            try:
                # If we can prettify the JSON, we should
                value = json.dumps(json.loads(value), indent=2)
            except ValueError:
                # If we cannot, then we should still display the value
                pass
        return super(PrettyAceWidget, self).render(name, value, attrs=attrs)


class AttachmentAdmin (GenericAdminModelAdmin):
    pass


class ProfileProjectTemplateInline (admin.TabularInline):
    model = ProfileProjectTemplate
    extra = 0
    raw_id_fields = ('project',)
    exclude = ('created_at', 'updated_at')
    formfield_overrides = {
        TextField: {'widget': TextInput(attrs={'class': 'vTextField'})},
    }


class ProfileAdmin (admin.ModelAdmin):
    list_display = ('__str__', '_date_joined', 'affiliation', 'email')
    filter_horizontal = ('teams',)
    raw_id_fields = ('auth',)
    search_fields = ('slug',)

    inlines = (ProfileProjectTemplateInline,)

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
        # JSONField: {'widget': Textarea(attrs={'class': 'vLargeTextField'})},
        JSONField: {'widget': PrettyAceWidget(mode='json', width='100%', wordwrap=True)},
        # JSONField: {'widget': AceWidget(mode='json', theme='github')},
    }


class AttachmentInline (GenericTabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('index',)
    ct_field = 'attached_to_type'
    ct_fk_field = 'attached_to_id'
    exclude = ('created_at', 'updated_at')
    form = modelform_factory(Attachment, fields='__all__', widgets={
        'label': TextInput(),
    })


class RoundupAdmin (DjangoObjectActions, admin.ModelAdmin):
    list_display = ('_title', '_owner_slug', '_owner_email', '_updated_at', '_created_at', '_permalink')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-updated_at',)
    search_fields = ('owner__name', 'owner__slug', 'title', 'slug')

    objectactions = ('clone_roundup',)
    raw_id_fields = ('theme', 'template', 'owner')

    def clone_roundup(self, request, obj):
        try:
            new_obj = obj.clone()
            new_obj_edit_url = reverse('admin:planbox_data_roundup_change', args=[new_obj.pk])
            return HttpResponseRedirect(new_obj_edit_url)
        except Exception as e:
            messages.error(request, 'Failed to clone roundup: %s (%s)' % (e, type(e).__name__))

    def get_queryset(self, request):
        qs = super(RoundupAdmin, self).get_queryset(request)
        return qs.select_related('owner')

    def _permalink(self, roundup):
        if len(roundup.owner.slug) == 0:
            return '(bad owner slug)'

        return format_html(
            '''<a href="{0}" target="_blank">Link &#8663</a>''',  # 8663 is the ⇗ character
            reverse('app-roundup', kwargs={'owner_slug': roundup.owner.slug})
        )
    _permalink.allow_tags = True
    _permalink.short_description = _('Link')

    def _title(self, roundup):
        return format_html(
            '{0} <small style="white-space:nowrap">({1})</small>',
            roundup.title if roundup.title != '' else '[No Title]',
            roundup.slug
        )
    _title.short_description = _('Roundup')
    _title.admin_order_field = 'title'

    def _owner_slug(self, roundup):
        return  roundup.owner.slug
    _owner_slug.short_description = _('Owner slug')
    _owner_slug.admin_order_field = 'owner__slug'

    def _owner_email(self, roundup):
        return  roundup.owner.email
    _owner_email.short_description = _('Email')
    _owner_email.admin_order_field = 'owner__email'

    def _owner_affiliation(self, roundup):
        return roundup.owner.affiliation
    _owner_affiliation.short_description = _('Affiliation')
    _owner_affiliation.admin_order_field = 'owner__affiliation'

    # Format datetimes
    def _updated_at(self, roundup):
        return roundup.updated_at.strftime('%Y-%m-%d %H:%M')
    _updated_at.short_description = _('Updated')
    _updated_at.admin_order_field = 'updated_at'

    def _created_at(self, roundup):
        return roundup.created_at.strftime('%Y-%m-%d %H:%M')
    _created_at.short_description = _('Created')
    _created_at.admin_order_field = 'created_at'


class EventAdmin (admin.ModelAdmin):
    list_display = ('label', 'project', 'index')
    inlines = (
        AttachmentInline,
    )
    raw_id_fields = ('project',)
    form = modelform_factory(Event, fields='__all__', widgets={
        'label': TextInput(attrs={'class': 'vTextField'}),
        'datetime_label': TextInput(attrs={'class': 'vTextField'})
    })


class EventInline (admin.StackedInline):
    model = Event
    extra = 0
    prepopulated_fields = {"slug": ("label",)}
    readonly_fields = ('index',)

    form = modelform_factory(Event, fields='__all__', widgets={
        'label': TextInput(attrs={'class': 'vTextField'}),
        'datetime_label': TextInput(attrs={'class': 'vTextField'})
    })


class ProjectAdmin (DjangoObjectActions, admin.ModelAdmin):
    list_display = ('_title', 'public', '_owner_slug', '_owner_email', '_owner_affiliation', 'location', '_updated_at', '_created_at', '_permalink')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-updated_at',)
    search_fields = ('owner__name', 'owner__slug', 'location', 'title', 'slug')

    inlines = (
        SectionInline,
        EventInline,
    )
    objectactions = ('clone_project',)
    raw_id_fields = ('theme', 'template', 'owner')
    readonly_fields = ('_api_url',)
    form = modelform_factory(Project, fields='__all__', widgets={
        'title': TextInput(attrs={'class': 'vTextField'}),
        'location': TextInput(attrs={'class': 'vTextField'}),
        'happening_now_description': TextInput(attrs={'class': 'vTextField'}),
        'get_involved_description': TextInput(attrs={'class': 'vTextField'}),
    })

    def clone_project(self, request, obj):
        try:
            new_obj = obj.clone()
            new_obj_edit_url = reverse('admin:planbox_data_project_change', args=[new_obj.pk])
            return HttpResponseRedirect(new_obj_edit_url)
        except Exception as e:
            messages.error(request, 'Failed to clone project: %s (%s)' % (e, type(e).__name__))

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        return qs.select_related('owner')

    def _permalink(self, project):
        if len(project.slug) == 0:
            return '(bad project slug)'

        if len(project.owner.slug) == 0:
            return '(bad owner slug)'

        return format_html(
            '''<a href="{0}" target="_blank">Link &#8663</a>''',  # 8663 is the ⇗ character
            reverse('app-project', kwargs={'owner_slug': project.owner.slug, 'project_slug': project.slug})
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

    def _owner_slug(self, project):
        return  project.owner.slug
    _owner_slug.short_description = _('Owner slug')
    _owner_slug.admin_order_field = 'owner__slug'

    def _owner_email(self, project):
        return  project.owner.email
    _owner_email.short_description = _('Email')
    _owner_email.admin_order_field = 'owner__email'

    def _owner_affiliation(self, project):
        return project.owner.affiliation
    _owner_affiliation.short_description = _('Affiliation')
    _owner_affiliation.admin_order_field = 'owner__affiliation'

    def _api_url(self, project):
        url = reverse('project-detail', args=[project.pk])
        return '<a href="{0}" target="_blank">{0}</a>'.format(url)
    _api_url.allow_tags = True
    _api_url.short_description = _('API URL')

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
    formfield_overrides = {
        JSONField: {'widget': PrettyAceWidget(mode='json', width='100%')},
        # JSONField: {'widget': AceWidget(mode='json', theme='github')},
    }


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Roundup, RoundupAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Attachment, AttachmentAdmin)
