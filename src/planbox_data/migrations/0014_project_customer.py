# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moonclerk', '__first__'),
        ('planbox_data', '0013_project_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='customer',
            field=models.OneToOneField(related_name='project', null=True, blank=True, to='moonclerk.Customer'),
            preserve_default=True,
        ),
    ]
