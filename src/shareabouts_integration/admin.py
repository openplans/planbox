# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import TextField
from django.forms import TextInput
from shareabouts_integration.models import Preauthorization
from planbox_data.admin import ProjectAdmin

class ShareaboutsPreauthorizationInline (admin.TabularInline):
    model = Preauthorization
    verbose_name_plural = 'Shareabouts Preauthorization'
    formfield_overrides = {
        TextField: {'widget': TextInput(attrs={'class': 'vTextField'})},
    }

ProjectAdmin.inlines += (ShareaboutsPreauthorizationInline,)
