# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0007_separate_shareabouts_section_maps_and_descriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='layout',
            field=models.CharField(default='generic', max_length=20, choices=[('generic', 'Generic (classic)'), ('shareabouts', 'Shareabouts Map')]),
            preserve_default=True,
        ),
    ]
