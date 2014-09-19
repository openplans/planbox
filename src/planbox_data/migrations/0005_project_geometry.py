# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0004_roundup'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, blank=True),
            preserve_default=True,
        ),
    ]
