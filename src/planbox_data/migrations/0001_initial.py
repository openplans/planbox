# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings
import django.db.models.deletion
import planbox_data.models
import builtins
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('url', models.URLField(max_length=2048)),
                ('thumbnail_url', models.URLField(null=True, max_length=2048, blank=True)),
                ('label', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('type', models.CharField(max_length=256, blank=True)),
                ('index', models.PositiveIntegerField(blank=True)),
                ('attached_to_id', models.PositiveIntegerField()),
                ('attached_to_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('attached_to_type', 'attached_to_id', 'index'),
            },
            bases=(planbox_data.models.OrderedModelMixin, planbox_data.models.CloneableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.TextField(help_text='The time label for the event, e.g. "January 15th, 2015", "Spring 2015 Phase", "Phase II, Summer 2015", etc.')),
                ('slug', models.CharField(max_length=64, blank=True)),
                ('description', models.TextField(help_text='A summary description of the timeline item', blank=True, default='')),
                ('index', models.PositiveIntegerField(help_text='Leave this field blank; it will be filled in automatically')),
                ('datetime_label', models.TextField(help_text="A description of this event's date and time, preferably in a parsable format.", blank=True)),
                ('start_datetime', models.DateTimeField(null=True, blank=True)),
                ('end_datetime', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ('project', 'index'),
            },
            bases=(planbox_data.models.OrderedModelMixin, planbox_data.models.ModelWithSlugMixin, planbox_data.models.CloneableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('name', models.CharField(help_text='The full name of the person or team', max_length=128, blank=True)),
                ('slug', models.CharField(help_text='A short name that will be used in URLs for projects owned by this profile', max_length=128, blank=True, unique=True)),
                ('email', models.EmailField(help_text='Contact email address of the profile holder', max_length=75, blank=True)),
                ('description', models.TextField(blank=True, default='')),
                ('avatar_url', models.URLField(null=True, blank=True)),
                ('affiliation', models.CharField(max_length=256, default='', blank=True)),
                ('project_editor_version', models.PositiveIntegerField(default=2, choices=[(1, 'Amethyst'), (2, 'Bistre')])),
                ('auth', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL, related_name='profile', blank=True)),
                ('teams', models.ManyToManyField(related_name='members', to='planbox_data.Profile', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(planbox_data.models.ModelWithSlugMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('title', models.TextField(blank=True)),
                ('slug', models.CharField(max_length=128, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('status', models.CharField(blank=True, help_text="A string representing the project's status", max_length=32, default='not-started', choices=[('not-started', 'Not Started'), ('active', 'Active'), ('complete', 'Complete')])),
                ('location', models.TextField(help_text='The general location of the project, e.g. "Philadelphia, PA", "Clifton Heights, Louisville, KY", "4th St. Corridor, Brooklyn, NY", etc.', blank=True, default='')),
                ('contact', models.TextField(help_text='The contact information for the project', blank=True, default='')),
                ('details', jsonfield.fields.JSONField(blank=True, default=builtins.dict)),
                ('cover_img_url', models.URLField(max_length=2048, blank=True, verbose_name='Cover Image URL')),
                ('logo_img_url', models.URLField(max_length=2048, blank=True, verbose_name='Logo Image URL')),
                ('happening_now_description', models.TextField(blank=True)),
                ('happening_now_link_type', models.CharField(blank=True, max_length=16, choices=[('event', 'Event'), ('section', 'Section'), ('external', 'External URL')])),
                ('happening_now_link_url', models.CharField(max_length=2048, blank=True)),
                ('get_involved_description', models.TextField(blank=True)),
                ('get_involved_link_type', models.CharField(blank=True, max_length=16, choices=[('event', 'Event'), ('section', 'Section'), ('external', 'External URL')])),
                ('get_involved_link_url', models.CharField(max_length=2048, blank=True)),
                ('last_opened_at', models.DateTimeField(null=True, blank=True)),
                ('last_saved_at', models.DateTimeField(null=True, blank=True)),
                ('last_opened_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', blank=True)),
                ('last_saved_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', blank=True)),
                ('owner', models.ForeignKey(related_name='projects', to='planbox_data.Profile')),
                ('template', models.ForeignKey(null=True, to='planbox_data.Project', help_text='The project, if any, that this one is based off of', on_delete=django.db.models.deletion.SET_NULL, blank=True)),
            ],
            options={
            },
            bases=(planbox_data.models.ModelWithSlugMixin, planbox_data.models.CloneableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('type', models.CharField(max_length=30, choices=[('text', 'Text'), ('image', 'Image'), ('timeline', 'Timeline'), ('shareabouts', 'Shareabouts'), ('raw', 'Raw HTML')])),
                ('label', models.TextField(blank=True)),
                ('menu_label', models.TextField(blank=True)),
                ('slug', models.CharField(max_length=30, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('details', jsonfield.fields.JSONField(blank=True, default=builtins.dict)),
                ('index', models.PositiveIntegerField(blank=True)),
                ('project', models.ForeignKey(related_name='sections', to='planbox_data.Project')),
            ],
            options={
                'ordering': ('project', 'index'),
            },
            bases=(planbox_data.models.OrderedModelMixin, planbox_data.models.ModelWithSlugMixin, planbox_data.models.CloneableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100, blank=True, verbose_name='Theme name')),
                ('definition', jsonfield.fields.JSONField(help_text='<p><b>The theme definition can consist of the following:</b></p><ul><li><i>css</i>: A URL or array of URLs for more than one stylesheet</li><li><i>js</i>: A URL or array of URLs for more than one script</li><li><i>favicon</i>: A URL</li><li><i>icons</i>: An array of objects with <code>{"url": (required), "sizes": (optional), "type": (optional)}</li></ul>', default=builtins.dict)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together=set([('project', 'slug')]),
        ),
        migrations.AddField(
            model_name='project',
            name='theme',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='planbox_data.Theme', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('owner', 'slug')]),
        ),
        migrations.AddField(
            model_name='event',
            name='project',
            field=models.ForeignKey(related_name='events', to='planbox_data.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('project', 'slug')]),
        ),
    ]
