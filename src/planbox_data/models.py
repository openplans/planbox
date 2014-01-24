from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

UserAuth = auth.get_user_model()


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


def create_user_profile(sender, instance, created, **kwargs):
    auth = instance
    if created:
        profile = User(auth=auth)
        profile.save()
post_save.connect(create_user_profile, sender=UserAuth, dispatch_uid="user-profile-creation-signal")


class ProjectQuerySet (models.query.QuerySet):
    def Q_owner(self, owner):
        if isinstance(owner, UserAuth):
            owner = owner.profile

        owner_type = ContentType.objects.get_for_model(owner)
        return models.Q(owner_type=owner_type, owner_id=owner.pk)

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
    slug = models.CharField(max_length=128, blank=True)
    public = models.BooleanField(default=False)
    status = models.CharField(help_text=_("A string representing the project's status"), choices=STATUS_CHOICES, default='not-started', max_length=32)
    location = models.CharField(help_text=_("The general location of the project, e.g. \"Philadelphia, PA\", \"Clifton Heights, Louisville, KY\", \"4th St. Corridor, Brooklyn, NY\", etc."), max_length=256, default='', blank=True)
    description = models.TextField(help_text=_("An introductory description of the project"), default='', blank=True)
    contact = models.TextField(help_text=_("The contact information for the project"), default='', blank=True)

    # An owner can be either a user or an organization
    owner_type = models.ForeignKey(ContentType, limit_choices_to=OWNER_MODEL_CHOICES)
    owner_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_type', 'owner_id')

    objects = ProjectManager()

    class Meta:
        unique_together = [('owner_type', 'owner_id', 'slug')]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title and not self.slug:
            self.slug = uniquify_slug(
                slugify(self.title),
                [p.slug for p in self.owner.projects.all()]
            )
        super(Project, self).save(*args, **kwargs)

    def owned_by(self, obj):
        if isinstance(obj, UserAuth):
            try:
                obj = obj.profile
            except User.DoesNotExist:
                return False

        if isinstance(obj, self.owner_type.model_class()) and self.owner_id == obj.pk:
            return True

        return False


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

    class Meta:
        verbose_name = 'Organization Profile'
        verbose_name_plural = 'Organization Profiles'

    def __str__(self):
        return self.name


class UserManager (models.Manager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset().select_related('auth')


@python_2_unicode_compatible
class User (models.Model):
    auth = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', help_text=_("The authentication account to use for this user"))
    projects = generic.GenericRelation(Project, content_type_field='owner_type', object_id_field='owner_id')
    organizations = models.ManyToManyField(Organization, related_name='members', blank=True)
    affiliation = models.CharField(max_length=256, blank=True, default='')

    objects = UserManager()

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.auth.username
