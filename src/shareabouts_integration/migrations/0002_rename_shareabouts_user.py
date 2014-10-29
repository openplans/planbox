# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shareabouts_integration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preauthorization',
            old_name='shareabouts_user',
            new_name='username',
        ),
        migrations.AlterField(
            model_name='preauthorization',
            name='username',
            field=models.TextField(help_text='The username of the Shareabouts user', blank=True),
        ),
        migrations.AlterField(
            model_name='preauthorization',
            name='project',
            field=models.OneToOneField(related_name=b'shareabouts_preauthorization', to='planbox_data.Project'),
        ),
    ]
