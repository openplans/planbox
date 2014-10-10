# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moonclerk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='reference',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
