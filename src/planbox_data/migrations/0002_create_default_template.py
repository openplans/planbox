# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def get_or_create(Model, **kwargs):
    try:
        obj = Model.objects.get(**kwargs)
    except Model.DoesNotExist:
        obj = Model.objects.create(**kwargs)
    return obj


def create_template_project(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Profile = apps.get_model("planbox_data", "Profile")
    Project = apps.get_model("planbox_data", "Project")
    Section = apps.get_model("planbox_data", "Section")

    # We would use the managers' get_or_create, but South, SQLite3, and
    # atomic don't play well together.
    templates_profile = get_or_create(
        Profile,
        name='Project Templates',
        slug='templates')

    default_template = get_or_create(
        Project,
        owner=templates_profile,
        slug='default')

    description_section = get_or_create(
        Section,
        project=default_template,
        index=0,
        type='text',
        slug='description')
    description_section.details = {
      "content": "\n            <b>What is the problem?</b><br>In a sentence or two, describe the\n            problem this project will address. Explain it from a resident's\n            perspective. Avoid jargon!<br><br><b>How are we addressing the problem?\n            </b><br>In a sentence or two, describe how this project addresses the\n            problem.<br><br><b>How can you get involved?</b><br>Briefly describe\n            how people can be involved in the project, such as public meetings and\n            workshops.<br><br><b>What is the schedule?</b><br>Briefly describe the\n            schedule, even if it is tentative, to give readers a high level\n            understanding of the timeline.\n            "
    }
    description_section.save()

    shareabouts_section = get_or_create(
        Section,
        project=default_template,
        index=1,
        type='shareabouts',
        slug='map',
        menu_label='Interactive Map',
        label='We want to hear from you!')
    shareabouts_section.details = {
        "description": "Give us your input on the project location. Your input will share the plan. Anyone can post an idea.",
        "layers": [
            {
                "url": "//{s}.tiles.mapbox.com/v3/openplans.map-dmar86ym/{z}/{x}/{y}.png"
            }
        ],
        "map": {
            "center": [38.993572, -96.196289],  # The center of the US
            "zoom": 4,
            "scrollWheelZoom": False
        }
    }
    shareabouts_section.save()


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_template_project)
    ]
