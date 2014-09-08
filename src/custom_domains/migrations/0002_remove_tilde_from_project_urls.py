# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_tildes(apps, schema_editor):
    DomainMapping = apps.get_model('custom_domains', 'DomainMapping')
    for mapping in DomainMapping.objects.all():
        if mapping.root_path.startswith('/~'):
            mapping.root_path = mapping.root_path[2:]
            mapping.save()


class Migration(migrations.Migration):

    dependencies = [
        ('custom_domains', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_tildes)
    ]
