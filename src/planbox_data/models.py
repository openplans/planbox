from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.timezone import now, timedelta
from django.utils.translation import ugettext as _
from jsonfield import JSONField


# ============================================================
# Mixins, utilities, and base models

class OrderedModelMixin (object):
    """
    Mixin for models that are orderable by the user.

    Required fields
    ---------------
    * index
        The sort order of the instance (it's not necessarily an index)

    Required methods
    ----------------
    * get_siblings()
        Get a queryset of the other instances in the instance's collection

    """
    def get_next_sibling_index(self):
        siblings = self.get_siblings()
        max_index = siblings.aggregate(max_index=models.Max('index'))['max_index']
        return (0) if (max_index is None) else (max_index + 1)

    def save(self, *args, **kwargs):
        if self.index is None:
            self.index = self.get_next_sibling_index()
        return super(OrderedModelMixin, self).save(*args, **kwargs)



clone_pre_save = Signal(providing_args=["orig_inst", "new_inst"])
clone_post_save = Signal(providing_args=["orig_inst", "new_inst"])

class CloneableModelMixin (object):
    """
    Mixin providing a clone method that copies all of a models instance's
    fields to a new instance of the model, allowing overrides.

    """
    def get_ignore_fields(self, ModelClass):
        fields = ModelClass._meta.fields
        pk_name = ModelClass._meta.pk.name

        ignore_field_names = set([pk_name])
        for fld in fields:
            if fld.name == pk_name:
                pk_fld = fld
                break
        else:
            raise Exception('Model %s somehow has no PK field' % (ModelClass,))

        if pk_fld.rel and pk_fld.rel.parent_link:
            parent_ignore_fields = self.get_ignore_fields(pk_fld.rel.to)
            ignore_field_names.update(parent_ignore_fields)

        return ignore_field_names

    def get_clone_save_kwargs(self):
        return {}

    def clone_related(self, onto):
        pass

    def clone(self, overrides=None, commit=True):
        """
        Create a duplicate of the model instance, replacing any properties
        specified as keyword arguments. This is a simple base implementation
        and may need to be extended for specific classes, since it is
        does not address related fields in any way.
        """
        fields = self._meta.fields
        ignore_field_names = self.get_ignore_fields(self.__class__)
        inst_kwargs = {}

        for fld in fields:
            if fld.name not in ignore_field_names:
                fld_value = getattr(self, fld.name)
                inst_kwargs[fld.name] = fld_value

        if overrides:
            inst_kwargs.update(overrides)

        new_inst = self.__class__(**inst_kwargs)
        clone_pre_save.send(sender=self.__class__, orig_inst=self, new_inst=new_inst)

        if commit:
            save_kwargs = self.get_clone_save_kwargs()
            new_inst.save(**save_kwargs)

            # If commit is true, clone the related submissions. Otherwise,
            # you will have to call clone_related manually on the cloned
            # instance once it is saved.
            self.clone_related(onto=new_inst)
            clone_post_save.send(sender=self.__class__, orig_inst=self, new_inst=new_inst)

        return new_inst


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
        if self.slug and not force:
            return self.slug

        basis = basis or self.get_slug_basis()
        if basis:
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
            self.clone_related(onto=new_inst)
        return new_inst


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


# ============================================================
# Profiles

class ProfileQuerySet (models.query.QuerySet):
    def Q_user(self, profile):
        return models.Q(id=profile.id)

    def Q_member(self, profile):
        profile_ids = [team.id for team in profile.teams.all()]
        return models.Q(id__in=profile_ids)

    def filter_by_user_or_member(self, obj):
        UserAuth = auth.get_user_model()
        if isinstance(obj, UserAuth):
            try:
                obj = obj.profile
            except Profile.DoesNotExist:
                return self.empty()

        user_query = self.Q_user(obj)
        member_query = self.Q_member(obj)
        return self.filter(user_query | member_query)


class ProfileManager (models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).select_related('auth')

    def filter_by_user_or_member(self, obj):
        return self.get_queryset().filter_by_user_or_member(obj)

    def get_by_natural_key(self, slug):
        """
        Build a profile from its natural key.

        Arguments:

        slug -- The slug of the profile.

        """
        return self.get(slug=slug)


@python_2_unicode_compatible
class Profile (ModelWithSlugMixin, TimeStampedModel):
    name = models.CharField(max_length=128, blank=True, help_text=_('The full name of the person or team'))
    slug = models.CharField(max_length=128, unique=True, blank=True, help_text=_('A short name that will be used in URLs for projects owned by this profile'))
    email = models.EmailField(blank=True, help_text=_('Contact email address of the profile holder'))
    description = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, null=True)
    # projects (reverse, Project)

    # User-profile specific
    auth = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', null=True, blank=True, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=256, blank=True, default='')
    teams = models.ManyToManyField('Profile', related_name='members', blank=True, limit_choices_to={'auth__isnull': True})

    # Team-profile specific
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
        return self.slug if self.auth is None else self.auth.username

    def natural_key(self):
        return (self.slug,)

    def get_slug_basis(self):
        return self.name

    def get_all_slugs(self):
        return set([p['slug'] for p in Profile.objects.all().values('slug')])

    def slug_exists(self, slug):
        return Profile.objects.filter(slug__iexact=slug).exists()

    def is_user_profile(self):
        return self.auth is not None

    def is_owned_by(self, user):
        return (user.id == self.auth_id)

    def has_member(self, user):
        members = list(self.members.all())
        if user.id in [profile.auth_id for profile in members]:
            return True
        else:
            return any(profile.has_member(user) for profile in members)

    def is_synced_with_auth(self, auth=None):
        auth = auth or self.auth
        if self.email != auth.email:
            return False
        return True

    def save(self, **kwargs):
        super(Profile, self).save(**kwargs)
        if self.auth and not self.is_synced_with_auth():
            self.auth.username = self.slug
            self.auth.email = self.email
            self.auth.save()

    def authorizes(self, user):
        """
        Test whether a given authenticated user is allowed to perform
        actions on behalf of this profile.
        """
        if user.is_superuser:
            return True

        if self.is_owned_by(user):
            return True

        if self.has_member(user):
            return True

        return False


def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Update the corresponding profile for a user authentication object with the
    auth object's email address as the profile email. Create the user profile
    object for the authentication object if it doesn't already exist.

    Connect as a post-save signal on the user authentication model, so that
    the above process is done every time a user authentication object is saved.

    Arguments:

    sender -- The user authentication model class.
    instance -- The user authentication model object that has been saved.
    created -- True if called as a result of the authentication model object
        being created; False otherwise.
    """
    user = instance
    try:
        profile = Profile.objects.get(auth=user)
    except Profile.DoesNotExist:
        profile = Profile(auth=user, slug='user-{}'.format(user.id))
    if profile.id is None or not profile.is_synced_with_auth(user):
        profile.email = user.email
        profile.save()
post_save.connect(create_or_update_user_profile, sender=settings.AUTH_USER_MODEL, dispatch_uid="user-profile-create-signal")


def create_roundup_for_new_team(sender, instance, created, **kwargs):
    """
    Create a project roundup for each new team profile.
    """
    if not created:
        return
    team = instance
    Roundup.objects.create(title='%s\'s Plans' % (team.name or team.slug,), owner=team)
post_save.connect(create_roundup_for_new_team, sender=Profile, dispatch_uid="user-team-profile-create-roundup-signal")


# ============================================================
# Projects

class ProjectQuerySet (models.query.QuerySet):
    def Q_owner(self, owner):
        UserAuth = auth.get_user_model()
        if isinstance(owner, UserAuth):
            owner = owner.profile

        return models.Q(owner=owner)

    def filter_by_owner_or_public(self, owner):
        owner_query = self.Q_owner(owner)
        public_query = models.Q(public=True)
        return self.filter(owner_query | public_query)

    def Q_member(self, member):
        UserAuth = auth.get_user_model()
        if isinstance(member, UserAuth):
            member = member.profile
        profile_ids = [member.id] + [team['id'] for team in member.teams.values('id')]

        return models.Q(owner_id__in=profile_ids)

    def filter_by_member_or_public(self, member):
        member_query = self.Q_member(member)
        public_query = models.Q(public=True)
        return self.filter(member_query | public_query)


class ProjectManager (models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def filter_by_owner_or_public(self, owner):
        return self.get_queryset().filter_by_owner_or_public(owner)

    def filter_by_member_or_public(self, owner):
        return self.get_queryset().filter_by_member_or_public(owner)

    def get_by_natural_key(self, owner, slug):
        """
        Build a project from its natural key.

        Arguments:

        owner -- The owner profile's slug.
        slug -- The project's slug.

        """
        return self.get(owner__slug=owner, slug=slug)


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

    LAYOUT_CHOICES = (
        ('generic', _('Default (classic)')),
        ('shareabouts', _('Shareabouts Map')),
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
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='generic')
    cover_img_url = models.URLField(_('Cover Image URL'), blank=True, max_length=2048)
    logo_img_url = models.URLField(_('Logo Image URL'), blank=True, max_length=2048)
    template = models.ForeignKey('Project', help_text=_("The project, if any, that this one is based off of"), null=True, blank=True, on_delete=models.SET_NULL)

    expires_at = models.DateTimeField(null=True, blank=True)
    payment_type = models.CharField(max_length=20, blank=True)
    customer = models.OneToOneField('moonclerk.Customer', blank=True, null=True, related_name='project')
    payments = GenericRelation('moonclerk.Payment',
        content_type_field='item_type', object_id_field='item_id')

    # NOTE: These may belong in a separate model, but are on the project for
    #       now. I think the model would be called a Highlight.
    happening_now_description = models.TextField(blank=True)
    happening_now_link_type = models.CharField(max_length=16, choices=LINK_TYPE_CHOICES, blank=True)
    happening_now_link_url = models.CharField(max_length=2048, blank=True)

    get_involved_description = models.TextField(blank=True)
    get_involved_link_type = models.CharField(max_length=16, choices=LINK_TYPE_CHOICES, blank=True)
    get_involved_link_url = models.CharField(max_length=2048, blank=True)

    # Project activity
    last_opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+')
    last_opened_at = models.DateTimeField(null=True, blank=True)
    last_saved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+')
    last_saved_at = models.DateTimeField(null=True, blank=True)

    objects = ProjectManager()

    class Meta:
        unique_together = [('owner', 'slug')]

    def __str__(self):
        return self.title

    def get_summary(self):
        for section in self.sections.all():
            if section.type == 'text':
                return section.details.get('content', '')

    def mark_opened_by(self, user, opened_at=None):
        # TODO: This could just be done in the cache.
        self.last_opened_at = opened_at or now()
        self.last_opened_by = user if (user and user.is_authenticated()) else None
        self.save()

    def mark_closed(self):
        self.mark_opened_by(None)

    def is_opened_by(self, user):
        two_minutes = timedelta(minutes=2)
        return self.last_opened_by == user and (now() - self.last_opened_at) < two_minutes

    def get_opened_by(self):
        two_minutes = timedelta(minutes=2)
        if self.last_opened_at and (now() - self.last_opened_at) < two_minutes:
            return self.last_opened_by
        else:
            return None

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

    def slug_exists(self, slug):
        return self.owner.projects.filter(slug__iexact=slug).exists()

    def clone_related(self, onto):
        kwargs = dict(project=onto)
        for e in self.events.all(): e.clone(overrides=kwargs)
        for s in self.sections.all(): s.clone(overrides=kwargs)

        # TODO: This should be handled by signals in shareabouts_integration.
        # Maybe a pre_clone_related signal.
        from django.core.exceptions import ObjectDoesNotExist
        try:
            self.shareabouts_preauthorization.clone(overrides=kwargs)
        except ObjectDoesNotExist:
            pass

    def owned_by(self, obj):
        UserAuth = auth.get_user_model()
        if isinstance(obj, UserAuth):
            try: obj = obj.profile
            except Profile.DoesNotExist: return False
        return (self.owner == obj)

    def editable_by(self, obj):
        UserAuth = auth.get_user_model()
        if hasattr(obj, 'is_authenticated') and not obj.is_authenticated():
            return False

        if isinstance(obj, UserAuth):
            try: obj = obj.profile
            except Profile.DoesNotExist: return False

        if obj.auth.is_superuser:
            return True

        return self.owned_by(obj) or (obj in self.owner.members.all())

    def reset_trial_period(self):
        if hasattr(settings, 'TRIAL_DURATION'):
            duration = settings.TRIAL_DURATION
            if not isinstance(duration, timedelta):
                duration = timedelta(seconds=duration)
            self.expires_at = now() + duration

    def save(self, *args, **kwargs):
        if self.pk is None:  # Creating...
            if self.expires_at is None:
                self.reset_trial_period()
        return super(Project, self).save(*args, **kwargs)


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
    details = JSONField(blank=True, default=dict)

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

    def slug_exists(self, slug):
        return self.project.events.filter(slug__iexact=slug).exists()

    def get_siblings(self):
        return self.project.events.all()

    def clone_related(self, onto):
        kwargs = dict(attached_to=onto)
        for a in self.attachments.all(): a.clone(overrides=kwargs)


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
        return self.attached_to.attachments.all()


# ============================================================
# Project pages

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

    def slug_exists(self, slug):
        return self.project.sections.filter(slug__iexact=slug).exists()

    def get_siblings(self):
        return self.project.sections.all()


# ============================================================
# Project templates

@python_2_unicode_compatible
class ProfileProjectTemplate(OrderedModelMixin, TimeStampedModel):
    profile = models.ForeignKey('Profile', related_name='project_templates')
    project = models.ForeignKey('Project')
    index = models.PositiveIntegerField(blank=True)

    label = models.TextField(default='', blank=True)
    short_description = models.TextField(default='', blank=True)
    long_description = models.TextField(default='', blank=True)
    image_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ('index',)

    def __str__(self):
        return self.label or _('(No label)')

    def get_siblings(self):
        return self.profile.project_templates.exclude(pk=self.pk)


def add_project_template(sender, instance, created, **kwargs):
    """
    Create a profile project template for each project added to the template
    profile.
    """
    if not created:
        return
    if instance.owner.slug != settings.TEMPLATES_PROFILE:
        return
    ProfileProjectTemplate.objects.create(profile=instance.owner, project=instance, label=instance.title)
post_save.connect(add_project_template, sender=Project, dispatch_uid="add-project-template-signal")


# ============================================================
# Roundup pages

@python_2_unicode_compatible
class Roundup (ModelWithSlugMixin, CloneableModelMixin, TimeStampedModel):
    title = models.TextField(blank=True)
    slug = models.CharField(max_length=128, blank=True)
    owner = models.ForeignKey('Profile', related_name='roundups')
    details = JSONField(blank=True, default=dict)
    theme = models.ForeignKey('Theme', related_name='roundups', null=True, blank=True, on_delete=models.SET_NULL)
    template = models.ForeignKey('Roundup', help_text=_("The roundup, if any, that this one is based off of"), null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def get_slug_basis(self):
        return self.title

    def get_all_slugs(self):
        return [r.slug for r in self.owner.roundups.all()]

    def slug_exists(self, slug):
        return self.owner.roundups.filter(slug__iexact=slug).exists()
