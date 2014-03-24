from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from jsonfield import JSONField

UserAuth = auth.get_user_model()


class TimeStampedModel (models.Model):
    created_at = models.DateTimeField(default=now, blank=True)
    updated_at = models.DateTimeField(default=now, blank=True)

    class Meta:
        abstract = True

    def save(self, update_times=True, *args, **kwargs):
        if update_times:
            if self.pk is None: self.created_at = now()
            self.updated_at = now()
        super(TimeStampedModel, self).save(*args, **kwargs)


def uniquify_slug(slug, existing_slugs):
    if slug not in existing_slugs:
        return slug

    uniquifier = 2
    while True:
        new_slug = '%s-%s' % (slug, uniquifier)
        if new_slug not in existing_slugs:
            return new_slug
        else:
            uniquifier += 1


def create_or_update_user_profile(sender, instance, created, **kwargs):
    auth = instance
    try:
        profile = Profile.objects.get(auth=auth)
    except Profile.DoesNotExist:
        profile = Profile(auth=auth)
    profile.slug = auth.username
    profile.email = auth.email
    profile.save()
post_save.connect(create_or_update_user_profile, sender=UserAuth, dispatch_uid="user-profile-create-signal")


class ProjectQuerySet (models.query.QuerySet):
    def Q_owner(self, owner):
        if isinstance(owner, UserAuth):
            owner = owner.profile

        return models.Q(owner=owner)

    def filter_by_owner_or_public(self, owner):
        owner_query = self.Q_owner(owner)
        public_query = models.Q(public=True)
        return self.filter(owner_query | public_query)


class ProjectManager (models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def filter_by_owner_or_public(self, owner):
        return self.get_queryset().filter_by_owner_or_public(owner)


@python_2_unicode_compatible
class Project (TimeStampedModel):
    STATUS_CHOICES = (
        ('not-started', _('Not Started')),
        ('active', _('Active')),
        ('complete', _('Complete')),
    )

    title = models.CharField(max_length=1024)
    slug = models.CharField(max_length=128, blank=True)
    public = models.BooleanField(default=False, blank=True)
    status = models.CharField(help_text=_("A string representing the project's status"), choices=STATUS_CHOICES, default='not-started', max_length=32, blank=True)
    location = models.CharField(help_text=_("The general location of the project, e.g. \"Philadelphia, PA\", \"Clifton Heights, Louisville, KY\", \"4th St. Corridor, Brooklyn, NY\", etc."), max_length=256, default='', blank=True)
    description = models.TextField(help_text=_("An introductory description of the project"), default='', blank=True)
    contact = models.TextField(help_text=_("The contact information for the project"), default='', blank=True)
    owner = models.ForeignKey('Profile', related_name='projects')
    theme = models.ForeignKey('Theme', related_name='projects', null=True, blank=True)
    template = models.ForeignKey('Project', null=True, blank=True)

    objects = ProjectManager()

    class Meta:
        unique_together = [('owner', 'slug')]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title and not self.slug:
            self.slug = uniquify_slug(
                slugify(strip_tags((self.title))),
                [p.slug for p in self.owner.projects.all()]
            )
        super(Project, self).save(*args, **kwargs)

    def owned_by(self, obj):
        if isinstance(obj, UserAuth):
            try: obj = obj.profile
            except Profile.DoesNotExist: return False
        return (self.owner == obj)


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


class ProfileManager (models.Manager):
    def get_queryset(self):
        return super(ProfileManager, self).get_queryset().select_related('auth')


@python_2_unicode_compatible
class Profile (TimeStampedModel):
    name = models.CharField(max_length=128, blank=True, help_text=_('The full name of the person or organization'))
    slug = models.CharField(max_length=128, unique=True, help_text=_('A short name that will be used in URLs for projects owned by this profile'))
    email = models.EmailField(blank=True, help_text=_('Contact email address of the profile holder'))
    # projects (reverse, Project)

    # User-profile specific
    auth = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', null=True, blank=True, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=256, blank=True, default='')
    organizations = models.ManyToManyField('Profile', related_name='members', blank=True, limit_choices_to={'auth__isnull': True})

    # Organization-profile specific
    # members (reverse, Profile)

    objects = ProfileManager()

    def __str__(self):
        return self.slug


@python_2_unicode_compatible
class Theme (TimeStampedModel):
    css_url = models.URLField(blank=True)

    def __str__(self):
        return self.css_url


@python_2_unicode_compatible
class Section (TimeStampedModel):
    SECTION_TYPE_CHOICES = (
        ('text', _('Text')),
        ('timeline', _('Timeline')),
    )

    project = models.ForeignKey('Project', related_name='sections')
    type = models.CharField(max_length=30, choices=SECTION_TYPE_CHOICES)

    label = models.TextField()
    menu_label = models.TextField()
    slug = models.CharField(max_length=30)
    details = JSONField(blank=True, default=lambda: '{}')

    index = models.PositiveIntegerField(blank=True)

    class Meta:
        ordering = ('project', 'index',)

    def __str__(self):
        return '%s section (%s)' % (self.type, self.slug)

    def save(self, *args, **kwargs):
        if self.index is None:
            sections = self.project.sections.aggregate(max_index=models.Max('index'))
            if sections['max_index'] is None: self.index = 0
            else: self.index = sections['max_index'] + 1
        return super(Section, self).save(*args, **kwargs)
