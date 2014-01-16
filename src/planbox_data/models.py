from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _


@python_2_unicode_compatible
class Project (models.Model):
    STATUS_CHOICES = (
        ('not-started', _('Not Started')),
        ('active', _('Active')),
        ('complete', _('Complete')),
    )

    OWNER_MODEL_CHOICES = (
        models.Q(app_label='planbox_data', model='user') | 
        models.Q(app_label='planbox_data', model='organization')
    )

    title = models.CharField(max_length=1024)
    slug = models.CharField(max_length=128)
    status = models.CharField(help_text=_("A string representing the project's status"), choices=STATUS_CHOICES, default='not-started', max_length=32)
    location = models.CharField(help_text=_("The general location of the project, e.g. \"Philadelphia, PA\", \"Clifton Heights, Louisville, KY\", \"4th St. Corridor, Brooklyn, NY\", etc."), max_length=256, default='')
    description = models.TextField(help_text=_("An introductory description of the project"), default='')
    contact = models.TextField(help_text=_("The contact information for the project"), default='', blank=True)

    # An owner can be either a user or an organization
    owner_type = models.ForeignKey(ContentType, limit_choices_to=OWNER_MODEL_CHOICES)
    owner_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_type', 'owner_id')

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Event (models.Model):
    label = models.CharField(help_text=_("The time label for the event, e.g. \"January 15th, 2015\", \"Spring 2015 Phase\", \"Phase II, Summer 2015\", etc."), max_length=1024)
    description = models.TextField(help_text=_("A summary description of the timeline item"), default='', blank=True)
    index = models.PositiveIntegerField(help_text=_("Leave this field blank; it will be filled in automatically"))
    project = models.ForeignKey(Project, related_name='events')

    class Meta:
        ordering = ('project', 'index',)

    def __str__(self):
        if self.index is not None:
            return '%s. %s' % (self.index + 1, self.label)
        else:
            return self.label

    def save(self, *args, **kwargs):
        if self.index is None:
            events = self.project.events.aggregate(max_index=models.Max('index'))
            if events['max_index'] is None: self.index = 0
            else: self.index = events['max_index'] + 1
        return super(Event, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Organization (models.Model):
    name = models.CharField(max_length=128)
    projects = generic.GenericRelation(Project, content_type_field='owner_type', object_id_field='owner_id')

    def __str__(self):
        return self.name


class UserManager (models.Manager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset().select_related('auth')


@python_2_unicode_compatible
class User (models.Model):
    auth = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='planbox_user', help_text=_("The authentication account to use for this user"))
    projects = generic.GenericRelation(Project, content_type_field='owner_type', object_id_field='owner_id')
    organizations = models.ManyToManyField(Organization, related_name='members', blank=True)

    objects = UserManager()

    def __str__(self):
        return self.auth.username
