from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
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
    """
    Create a unique version of the given slug with respect to the given list
    of slugs. Do this by appending integers to the end of slug until a string
    not in the existing list is found.

    Arguments:

    slug -- An initial version of the slug string to be uniquified.
    existing_slugs -- Other slug strings to be compared against.

    Example:

    >>> uniquify_slug('my-section', ['my-section', 'my-other-section'])
    'my-section-2'

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


def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Update the corresponding profile for a user authentication object with the
    auth object's username as the slug, and the email address as the profile
    email. Create the user profile object for the authentication object if it
    doesn't already exist.

    Connect as a post-save signal on the user authentication model, so that
    the above process is done every time a user authentication object is saved.

    Arguments:

    sender -- The user authentication model class.
    instance -- The user authentication model object that has been saved.
    created -- True if called as a result of the authentication model object
        being created; False otherwise.

    Example:

    >>> ## Create a user...
    >>>
    >>> user = UserAuth.objects.create_user(
    ...     username='my-user',
    ...     email='my-user@example.com',
    ...     password='123')
    >>> user.profile.slug
    'my-user'
    >>> user.profile.email
    'my-user@example.com'
    >>>
    >>> ## Update the user...
    >>>
    >>> user.username = 'my-new-username'
    >>> user.save()
    >>> user.profile.slug
    'my-new-username'

    """
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

    def get_by_natural_key(self, owner, slug):
        """
        Build a project from its natural key.

        Arguments:

        owner -- The owner profile's slug.
        slug -- The project's slug.

        """
        return self.get(owner__slug=owner, slug=slug)


class OrderedModelMixin (object):
    def save(self, *args, **kwargs):
        if self.index is None:
            siblings = self.get_siblings()
            if siblings['max_index'] is None: self.index = 0
            else: self.index = siblings['max_index'] + 1
        return super(OrderedModelMixin, self).save(*args, **kwargs)


class CloneableModelMixin (object):
    def clone(self, commit=True, **inst_kwargs):
        """
        Create a duplicate of the model instance, replacing any properties
        specified as keyword arguments.
        """
        fields = self._meta.fields
        pk_name = self._meta.pk.name

        for fld in fields:
            if fld.name != pk_name:
                fld_value = getattr(self, fld.name)
                inst_kwargs.setdefault(fld.name, fld_value)

        new_inst = self.__class__(**inst_kwargs)

        if commit:
            new_inst.save()

        return new_inst


class ModelWithSlugMixin (object):
    """
    A model that adds a slug on save if one does not exist. This model needs
    the following methods:

    get_slug_basis -- Get the string off that will be slugified to construct the slug.
    get_all_slugs -- Generate the set of all mututally unique slugs with
        respect to this model.

    """
    def ensure_slug(self, force=False, basis=None):
        """
        Determines a slug based on the slug's basis if no slug is set. When
        force is True, the slug is set even if it already has a value.
        """
        basis = basis or self.get_slug_basis()
        if basis and (force or not self.slug):
            max_length = self._meta.get_field('slug').max_length

            # Leave some room in the slug length for the uniquifier.
            max_length -= 16

            self.slug = uniquify_slug(
                slugify(strip_tags(basis))[:max_length],
                self.get_all_slugs()
            )
        return self.slug

    def save(self, *args, **kwargs):
        self.ensure_slug()
        return super(ModelWithSlugMixin, self).save(*args, **kwargs)

    def clone(self, commit=True, *args, **kwargs):
        new_inst = super(ModelWithSlugMixin, self).clone(commit=False, *args, **kwargs)
        new_inst.ensure_slug(force=True, basis=self.slug)
        if commit:
            new_inst.save()
        return new_inst


@python_2_unicode_compatible
class Project (ModelWithSlugMixin, CloneableModelMixin, TimeStampedModel):
    STATUS_CHOICES = (
        ('not-started', _('Not Started')),
        ('active', _('Active')),
        ('complete', _('Complete')),
    )

    LINK_TYPE_CHOICES = (
        ('event', _('Event')),
        ('section', _('Section')),
        ('external', _('External URL')),
    )

    title = models.TextField(blank=True)
    slug = models.CharField(max_length=128, blank=True)
    public = models.BooleanField(default=False, blank=True)
    status = models.CharField(help_text=_("A string representing the project's status"), choices=STATUS_CHOICES, default='not-started', max_length=32, blank=True)
    location = models.TextField(help_text=_("The general location of the project, e.g. \"Philadelphia, PA\", \"Clifton Heights, Louisville, KY\", \"4th St. Corridor, Brooklyn, NY\", etc."), default='', blank=True)
    contact = models.TextField(help_text=_("The contact information for the project"), default='', blank=True)
    owner = models.ForeignKey('Profile', related_name='projects')
    details = JSONField(blank=True, default=dict)
    theme = models.ForeignKey('Theme', related_name='projects', null=True, blank=True, on_delete=models.SET_NULL)
    cover_img_url = models.URLField(_('Cover Image URL'), blank=True, max_length=2048)
    logo_img_url = models.URLField(_('Logo Image URL'), blank=True, max_length=2048)
    template = models.ForeignKey('Project', help_text=_("The project, if any, that this one is based off of"), null=True, blank=True, on_delete=models.SET_NULL)

    # NOTE: These may belong in a separate model, but are on the project for
    #       now. I think the model would be called a Highlight.
    happening_now_description = models.TextField(blank=True)
    happening_now_link_type = models.CharField(max_length=16, choices=LINK_TYPE_CHOICES, blank=True)
    happening_now_link_url = models.CharField(max_length=2048, blank=True)

    get_involved_description = models.TextField(blank=True)
    get_involved_link_type = models.CharField(max_length=16, choices=LINK_TYPE_CHOICES, blank=True)
    get_involved_link_url = models.CharField(max_length=2048, blank=True)

    objects = ProjectManager()

    class Meta:
        unique_together = [('owner', 'slug')]

    def __str__(self):
        return self.title

    def natural_key(self):
        return self.owner.natural_key() + (self.slug,)

    def get_slug_basis(self):
        """
        Get the string off that will be slugified to construct the slug.
        """
        return self.title

    def get_all_slugs(self):
        """
        Generate the set of all mututally unique slugs with respect to this
        model.
        """
        return [p.slug for p in self.owner.projects.all()]

    def clone(self, *args, **kwargs):
        new_inst = super(Project, self).clone(*args, **kwargs)
        for e in self.events.all(): e.clone(project=new_inst)
        for s in self.sections.all(): s.clone(project=new_inst)
        return new_inst

    def owned_by(self, obj):
        if isinstance(obj, UserAuth):
            try: obj = obj.profile
            except Profile.DoesNotExist: return False
        return (self.owner == obj)


class EventManager (models.Manager):
    def get_by_natural_key(self, owner, project, index):
        """
        Build an event from its natural key.

        Arguments:

        owner -- The slug of the event's project's owner.
        project -- The slug of the event's containing project.
        index -- The index of the event within the project.

        """
        return self.get(project__owner__slug=owner, project__slug=project, index=index)


@python_2_unicode_compatible
class Event (OrderedModelMixin, ModelWithSlugMixin, CloneableModelMixin, models.Model):
    label = models.TextField(help_text=_("The time label for the event, e.g. \"January 15th, 2015\", \"Spring 2015 Phase\", \"Phase II, Summer 2015\", etc."))
    slug = models.CharField(max_length=64, blank=True)
    description = models.TextField(help_text=_("A summary description of the timeline item"), default='', blank=True)
    index = models.PositiveIntegerField(help_text=_("Leave this field blank; it will be filled in automatically"))
    project = models.ForeignKey(Project, related_name='events')

    datetime_label = models.TextField(blank=True, help_text=_("A description of this event's date and time, preferably in a parsable format."))
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    attachments = GenericRelation('Attachment',
                                  object_id_field='attached_to_id',
                                  content_type_field='attached_to_type')

    objects = EventManager()

    class Meta:
        ordering = ('project', 'index',)
        unique_together = [('project', 'slug')]

    def __str__(self):
        if self.index is not None:
            return '%s. %s' % (self.index + 1, self.label)
        else:
            return self.label

    def natural_key(self):
        return self.project.natural_key() + (self.index,)

    def get_slug_basis(self):
        return self.label

    def get_all_slugs(self):
        return [e.slug for e in self.project.events.all()]

    def get_siblings(self):
        return self.project.events.aggregate(max_index=models.Max('index'))

    def clone(self, *args, **kwargs):
        new_inst = super(Event, self).clone(*args, **kwargs)
        for a in self.attachments.all(): a.clone(attached_to=new_inst)
        return new_inst


class ProfileManager (models.Manager):
    def get_queryset(self):
        return super(ProfileManager, self).get_queryset().select_related('auth')

    def get_by_natural_key(self, slug):
        """
        Build a profile from its natural key.

        Arguments:

        slug -- The slug of the profile.

        """
        return self.get(slug=slug)


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

    # Feature flags/versions
    class Versions:
        AMETHYST = 1
        BISTRE = 2

    PROJECT_EDITOR_VERSION_CHOICES = (
        (Versions.AMETHYST, "Amethyst"),
        (Versions.BISTRE, "Bistre"),
    )

    project_editor_version = models.PositiveIntegerField(choices=PROJECT_EDITOR_VERSION_CHOICES, default=Versions.BISTRE)

    objects = ProfileManager()

    def __str__(self):
        return self.slug

    def natural_key(self):
        return (self.slug,)


@python_2_unicode_compatible
class Theme (TimeStampedModel):
    name = models.CharField(_('Theme name'), max_length=100, blank=True)
    definition = JSONField(default=dict,
        help_text=('<p><b>The theme definition can consist of the following:</b></p>'
            '<ul>'
                '<li><i>css</i>: A URL or array of URLs for more than one stylesheet</li>'
                '<li><i>js</i>: A URL or array of URLs for more than one script</li>'
                '<li><i>favicon</i>: A URL</li>'
                '<li><i>icons</i>: An array of objects with <code>{"url": (required), "sizes": (optional), "type": (optional)}</li>'
            '</ul>'))

    def __str__(self):
        return self.name or _('Theme %s (No name)') % self.pk


class SectionManager (models.Manager):
    def get_by_natural_key(self, owner, project, index):
        """
        Build a project section from its natural key.

        Arguments:

        owner -- The slug of the section's project's owner.
        project -- The slug of the section's project.
        index -- The index of the section within the project.

        """
        return self.get(project__owner__slug=owner, project__slug=project, index=index)


@python_2_unicode_compatible
class Section (OrderedModelMixin, ModelWithSlugMixin, CloneableModelMixin, TimeStampedModel):
    SECTION_TYPE_CHOICES = (
        ('text', _('Text')),
        ('image', _('Image')),
        ('timeline', _('Timeline')),
        ('shareabouts', _('Shareabouts')),
        ('raw', _('Raw HTML'))
    )

    project = models.ForeignKey('Project', related_name='sections')
    type = models.CharField(max_length=30, choices=SECTION_TYPE_CHOICES)
    label = models.TextField(blank=True)
    menu_label = models.TextField(blank=True)
    slug = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)
    details = JSONField(blank=True, default=dict)
    index = models.PositiveIntegerField(blank=True)

    objects = SectionManager()

    class Meta:
        ordering = ('project', 'index',)
        unique_together = [('project', 'slug')]

    def __str__(self):
        return '%s section (%s)' % (self.type, self.slug)

    def natural_key(self):
        return self.project.natural_key() + (self.index,)

    def get_slug_basis(self):
        return self.menu_label or self.type

    def get_all_slugs(self):
        return [s.slug for s in self.project.sections.all()]

    def get_siblings(self):
        return self.project.sections.aggregate(max_index=models.Max('index'))


class Attachment (OrderedModelMixin, CloneableModelMixin, TimeStampedModel):
    url = models.URLField(max_length=2048)
    thumbnail_url = models.URLField(max_length=2048, blank=True, null=True)
    label = models.TextField(blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=256, blank=True)
    index = models.PositiveIntegerField(blank=True)

    attached_to_type = models.ForeignKey('contenttypes.ContentType')
    attached_to_id = models.PositiveIntegerField()
    attached_to = GenericForeignKey('attached_to_type', 'attached_to_id')

    class Meta:
        ordering = ('attached_to_type', 'attached_to_id', 'index',)

    def get_siblings(self):
        return self.attached_to.attachments.aggregate(max_index=models.Max('index'))
