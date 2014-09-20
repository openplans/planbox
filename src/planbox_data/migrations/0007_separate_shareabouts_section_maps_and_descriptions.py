# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def uniquify_slug(slug, existing_slugs):
    """
    ...from planbox_data.models...
    """
    if slug not in existing_slugs:
        return slug

    uniquifier = 2
    while True:
        new_slug = '%s-%s' % (slug, uniquifier)
        if new_slug not in existing_slugs:
            return new_slug
        else:
            uniquifier += 1


def separate_shareabouts_section_maps_and_descriptions(apps, schema_editor):
    Section = apps.get_model('planbox_data', 'Section')
    sections = Section.objects.filter(type='shareabouts')

    for section in sections:
        label = section.label
        menu_label = section.menu_label
        description = section.details.get('description', '')

        # If it's already just a map, leave it alone
        if not label and not menu_label and not description:
            continue

        # Select all the sections that come after this one
        later_sections = section.project.sections.filter(index__gte=section.index)
        for sibling in later_sections:
            sibling.index += 1
            sibling.save()

        # Create a new Shareabouts section
        slugs = [s.slug for s in section.project.sections.all()]
        shareabouts_details = section.details.copy()
        shareabouts_details.pop('description', None)
        shareabouts_section = Section(
            project=section.project,
            type='shareabouts',
            details=shareabouts_details,
            index=section.index + 1,
            slug=uniquify_slug('map', slugs))
        shareabouts_section.save()

        # Convert the existing section into a text section
        text_details = {'content': description}
        text_section = section
        text_section.type = 'text'
        text_section.details = text_details
        text_section.save()


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0006_add_roundup_pages'),
    ]

    operations = [
        migrations.RunPython(separate_shareabouts_section_maps_and_descriptions)
    ]
