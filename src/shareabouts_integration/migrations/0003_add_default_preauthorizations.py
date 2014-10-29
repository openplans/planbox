# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


def add_default_shareabouts_preauthorization(apps, schema_editor):
    Project = apps.get_model('planbox_data', 'Project')
    Preauthorization = apps.get_model('shareabouts_integration', 'Preauthorization')

    for project in Project.objects.all().select_related('shareabouts_preauthorization'):
        try:
            project.shareabouts_preauthorization
        except models.ObjectDoesNotExist:
            Preauthorization.objects.create(project=project, username=settings.SHAREABOUTS_USERNAME)


class Migration(migrations.Migration):

    dependencies = [
        ('shareabouts_integration', '0002_rename_shareabouts_user'),
        ('planbox_data', '0008_project_layout'),
    ]

    operations = [
        migrations.RunPython(add_default_shareabouts_preauthorization)
    ]
