# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import __builtin__
import jsonfield.fields
import planbox_data.models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0003_move_projects_from_user_profiles'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roundup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('title', models.TextField(blank=True)),
                ('slug', models.CharField(max_length=128, blank=True)),
                ('details', jsonfield.fields.JSONField(default=__builtin__.dict, blank=True)),
                ('owner', models.ForeignKey(related_name='roundups', to='planbox_data.Profile')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='planbox_data.Roundup', help_text='The roundup, if any, that this one is based off of', null=True)),
                ('theme', models.ForeignKey(related_name='roundups', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='planbox_data.Theme', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(planbox_data.models.ModelWithSlugMixin, planbox_data.models.CloneableModelMixin, models.Model),
        ),
    ]
