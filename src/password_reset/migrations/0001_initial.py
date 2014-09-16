# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import password_reset.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('token', models.CharField(verbose_name='Reset token', max_length=200)),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(default=password_reset.models.PasswordResetRequest.Utils.make_default_expiration)),
                ('auth', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='User Auth Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
