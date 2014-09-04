# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import custom_domains.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DomainMapping',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=250, verbose_name='Custom domain')),
                ('root_path', models.CharField(max_length=250, help_text='The path of the root URL for which this domain is a shortcut.')),
            ],
            options={
            },
            bases=(custom_domains.models.BaseDomainMappingMixin, models.Model),
        ),
    ]
