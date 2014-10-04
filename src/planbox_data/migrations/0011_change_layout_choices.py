# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0010_order_templates_by_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='layout',
            field=models.CharField(default='generic', max_length=20, choices=[('generic', 'Default (classic)'), ('shareabouts', 'Shareabouts Map')]),
        ),
    ]
