# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def decouple_user_profile(profile_manager, user_profile):
    """
    Set the user's profile slug to an arbitrary value, and create a new team
    with the user's original slug value.
    """
    # store the profile slug
    original_slug = user_profile.slug

    # set the slug to 'user-' + user id
    user_profile.slug = 'user-{}'.format(user_profile.auth_id)
    user_profile.save()

    # create a new "team" profile with the original slug
    team_profile = profile_manager.create(
        slug=original_slug,
        name=user_profile.affiliation,
        email=user_profile.email)

    # add the user to the team
    team_profile.members.add(user_profile)
    return team_profile

def move_projects_to_team_profile(user_profile, team_profile):
    """
    Reassign all of a user's projects to a "team" profile
    """
    user_profile.projects.all().update(owner=team_profile)

def move_all_projects_to_teams(apps, schema_editor):
    Profile = apps.get_model('planbox_data', 'Profile')

    for user_profile in Profile.objects.all().exclude(auth_id=None):
        team_profile = decouple_user_profile(Profile.objects, user_profile)
        move_projects_to_team_profile(user_profile, team_profile)

def noop(): pass


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0002_create_default_template'),
    ]

    operations = [
        migrations.RunPython(move_all_projects_to_teams, noop)
    ]
