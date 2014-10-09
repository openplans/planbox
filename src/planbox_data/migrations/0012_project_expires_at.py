# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0011_change_layout_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='expires_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
