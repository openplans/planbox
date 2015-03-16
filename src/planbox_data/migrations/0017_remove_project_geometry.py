# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0016_add_details_to_events'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='geometry',
        ),
    ]
