# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_roundup_page(profile, Roundup):
    if not profile.roundups.all().exists():
        roundup = Roundup(
            title='%s\'s Plans' % (profile.name or profile.slug,),
            slug=profile.slug)
        profile.roundups.add(roundup)


def update_all_team_profiles(apps, schema_editor):
    Profile = apps.get_model('planbox_data', 'Profile')
    Roundup = apps.get_model('planbox_data', 'Roundup')
    for team_profile in Profile.objects.filter(auth=None):
        add_roundup_page(team_profile, Roundup)


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0005_project_geometry'),
    ]

    operations = [
        migrations.RunPython(update_all_team_profiles)
    ]
