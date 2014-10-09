# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import __builtin__
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('reference', models.CharField(max_length=30)),
                ('data', jsonfield.fields.JSONField(default=__builtin__.dict)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default=__builtin__.dict)),
                ('item_id', models.PositiveIntegerField(null=True, blank=True)),
                ('customer', models.ForeignKey(related_name=b'payments', to='moonclerk.Customer', null=True)),
                ('item_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
