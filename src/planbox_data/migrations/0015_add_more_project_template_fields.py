# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0014_project_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileprojecttemplate',
            name='long_description',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profileprojecttemplate',
            name='image_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profileprojecttemplate',
            name='short_description',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profileprojecttemplate',
            name='index',
            field=models.PositiveIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='profileprojecttemplate',
            name='label',
            field=models.TextField(default='', blank=True),
        ),
    ]
