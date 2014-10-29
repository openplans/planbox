# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0015_add_more_project_template_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preauthorization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shareabouts_user', models.TextField(blank=True)),
                ('project', models.ForeignKey(to='planbox_data.Project', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
