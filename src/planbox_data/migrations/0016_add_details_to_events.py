# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import __builtin__
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0015_add_more_project_template_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='details',
            field=jsonfield.fields.JSONField(default=__builtin__.dict, blank=True),
            preserve_default=True,
        ),
    ]
