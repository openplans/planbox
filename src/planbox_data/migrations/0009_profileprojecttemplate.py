# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import django.utils.timezone
import planbox_data.models


def create_default_templates(apps, schema_editor):
    # try:
    templates_profile_slug = settings.TEMPLATES_PROFILE
    # except:
    #     return

    Profile = apps.get_model('planbox_data', 'Profile')
    ProfileProjectTemplate = apps.get_model('planbox_data', 'ProfileProjectTemplate')

    try:
        templates_profile = Profile.objects.get(slug=templates_profile_slug)
    except Profile.DoesNotExist:
        return

    index = 0
    for project in templates_profile.projects.all():
        ProfileProjectTemplate.objects.create(
            profile=templates_profile,
            project=project,
            label=project.title,
            index=index)
        index += 1


def noop(*args, **kwargs): pass


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0008_project_layout'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileProjectTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('label', models.TextField()),
                ('index', models.PositiveIntegerField()),
                ('profile', models.ForeignKey(related_name='project_templates', to='planbox_data.Profile')),
                ('project', models.ForeignKey(to='planbox_data.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(planbox_data.models.OrderedModelMixin, models.Model),
        ),
        migrations.RunPython(create_default_templates, noop)
    ]
