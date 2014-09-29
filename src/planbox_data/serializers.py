from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from planbox_data import models, fields
import bleach, re, json


class CleanedHtmlField (serializers.CharField):
    ALLOWED_TAGS = [
        'a',
        'abbr',
        'acronym',
        'b',
        'blockquote',
        'code',
        'em',
        'i',
        'li',
        'ol',
        'strong',
        'ul',

        'p',
        'br'
    ]

    def __init__(self, allowed_tags=ALLOWED_TAGS, *args, **kwargs):
        self.allowed_tags = allowed_tags
        super(CleanedHtmlField, self).__init__(*args, **kwargs)

    def from_native(self, data):
        data = re.sub('<div[^>]*>', '<br>', data)
        data = data.replace('</div>', '')
        data = bleach.clean(data, tags=self.allowed_tags, strip=True)
        return super(CleanedHtmlField, self).from_native(data)


class OrderedSerializerMixin (object):
    def field_from_native(self, data, files, field_name, into):
        super(OrderedSerializerMixin, self).field_from_native(data, files, field_name, into)

        # If this is being used as a field, respect the order of the items.
        # Renumber the index values to reflect the incoming order.
        if self.many and field_name in into:
            if not isinstance(into.get(field_name), (list, tuple)):
                raise serializers.ValidationError("must be an array")

            for index, obj in enumerate(into[field_name]):
                obj.index = index


class AddRemoveModelSerializer (serializers.ModelSerializer):
    """
    An unfortunate subclass of ModelSerializer with the "correct" order for
    deleting and updating nested models.

    See https://github.com/tomchristie/django-rest-framework/pull/1902 for
    more information.

    TODO: This mixin may be unnecessary after DRF3.

    """
    def save_object(self, obj, **kwargs):
        """
        Save the deserialized object.
        """
        from rest_framework.serializers import RelationsList

        if getattr(obj, '_nested_forward_relations', None):
            # Nested relationships need to be saved before we can save the
            # parent instance.
            for field_name, sub_object in obj._nested_forward_relations.items():
                if sub_object:
                    self.save_object(sub_object)
                setattr(obj, field_name, sub_object)

        obj.save(**kwargs)

        if getattr(obj, '_m2m_data', None):
            for accessor_name, object_list in obj._m2m_data.items():
                setattr(obj, accessor_name, object_list)
            del(obj._m2m_data)

        if getattr(obj, '_related_data', None):
            related_fields = dict([
                (field.get_accessor_name(), field)
                for field, model
                in obj._meta.get_all_related_objects_with_model()
            ])
            for accessor_name, related in obj._related_data.items():
                if isinstance(related, RelationsList):
                    # Delete any removed objects
                    if related._deleted:
                        [self.delete_object(item) for item in related._deleted]

                    # Nested reverse fk relationship
                    for related_item in related:
                        fk_field = related_fields[accessor_name].field.name
                        setattr(related_item, fk_field, obj)
                        self.save_object(related_item)

                elif isinstance(related, models.Model):
                    # Nested reverse one-one relationship
                    fk_field = obj._meta.get_field_by_name(accessor_name)[0].field.name
                    setattr(related, fk_field, obj)
                    self.save_object(related)
                else:
                    # Reverse FK or reverse one-one
                    setattr(obj, accessor_name, related)
            del(obj._related_data)


class SlugValidationMixin (object):
    def validate_slug(self, attrs, source):
        slug = attrs.get(source)

        # If the slug is empty, we're just going to generate one.
        if not slug:
            return attrs

        if self.object:
            # If the slug is not changing, then all is well.
            if slug == self.object.slug:
                return attrs
            # If we're changing the slug, and it's already in use, then we
            # have a problem.
            if self.object.slug_exists(slug):
                raise serializers.ValidationError('This slug is already in use.')

        # Letters, numbers, and dashes.
        pattern = r'^[A-Za-z0-9-]*$'
        if not re.match(pattern, slug):
            raise serializers.ValidationError('Use only numbers, letters, and dashes in slugs.')

        return attrs


class FlexibleFields (object):
    """
    Allow a serializer's field set to be overridden at instantiation time.
    """
    def __init__(self, *args, **kwargs):
        self.override_fields = kwargs.pop('fields', None)
        self.include_fields = kwargs.pop('include', None)
        self.exclude_fields = kwargs.pop('exclude', None)
        super(FlexibleFields, self).__init__(*args, **kwargs)

    def _options_class(self, *args, **kwargs):
        opts = super(FlexibleFields, self)._options_class(*args, **kwargs)
        if self.override_fields is not None:
            opts.fields = self.override_fields
        if self.include_fields is not None:
            opts.fields = opts.fields or []
            iter_type = type(opts.fields)
            opts.fields += iter_type(self.include_fields)
        if self.exclude_fields is not None:
            opts.exclude = opts.exclude or []
            iter_type = type(opts.exclude)
            opts.exclude += iter_type(self.exclude_fields)
        return opts


# ============================================================
# Profile serializers

class AssociatedProfileSerializer (FlexibleFields, AddRemoveModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('id', 'slug', 'name', 'avatar_url',)

    def get_default_fields(self):
        fields = super(AssociatedProfileSerializer, self).get_default_fields()

        # Modify the fields
        # - remove read_only so that they're available in restore_objects
        # - remove required since only one of id or slug is required
        fields['id'].read_only = False
        for field in fields.values():
            field.required = False

        return fields

    def to_native(self, obj):
        data = super(AssociatedProfileSerializer, self).to_native(obj)
        # Add the username field if it's a user profile
        if obj.is_user_profile():
            data['username'] = obj.auth.username
        return data

    def restore_object(self, attrs, instance=None):
        """
        Only restore objects that already exist; don't create or delete.
        """
        Model = self.opts.model

        # First try to get the model's PK
        try:
            id_arg_name = Model._meta.pk.name
            id_arg_value = attrs[Model._meta.pk.name]
        except KeyError:
            # Failing that, try the slug
            try:
                id_arg_name = 'slug'
                id_arg_value = attrs['slug']
            except KeyError:
                raise serializers.ValidationError(
                    'You must specify one of the fields "%s" or "slug".' % (Model._meta.pk.name,))

        # Find the model (Profile) corresponding to the id or slug.
        try:
            id_kwargs = {id_arg_name: id_arg_value}
            instance = Model.objects.get(**id_kwargs)
        except Model.DoesNotExist:
            raise serializers.ValidationError(
                'No %s found with %s=%s' % (Model._meta.verbose_name, id_arg_name, id_arg_value))

        return instance


class OwnedProjectSerializer (AddRemoveModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'slug', 'title',)


class UserSerializer (AddRemoveModelSerializer):
    username = serializers.CharField(source='auth.username')
    teams = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)

    class Meta:
        model = models.Profile


class ProfileSerializer (SlugValidationMixin, AddRemoveModelSerializer):
    members = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)
    teams = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)
    projects = OwnedProjectSerializer(many=True, read_only=True)

    class Meta:
        model = models.Profile
        exclude = ('project_editor_version',)

    def get_default_fields(self):
        fields = super(ProfileSerializer, self).get_default_fields()
        # Add the username field if it's a user profile
        if self.object.is_user_profile():
            fields['username'] = serializers.CharField(source='auth.username', read_only=True)
        return fields

    def validate(self, attrs):
        if not attrs.get('name') and not attrs.get('slug'):
            raise serializers.ValidationError('You must specify either a name or a slug.')
        return attrs


# ============================================================
# Project-related serializers

class AttachmentSerializer (OrderedSerializerMixin, AddRemoveModelSerializer):
    label = CleanedHtmlField()
    description = CleanedHtmlField(required=False)

    class Meta:
        model = models.Attachment
        exclude = ('attached_to_type', 'attached_to_id', 'index')


class EventSerializer (OrderedSerializerMixin, AddRemoveModelSerializer):
    label = CleanedHtmlField()
    description = CleanedHtmlField(required=False)
    attachments = AttachmentSerializer(many=True, required=False, allow_add_remove=True)

    class Meta:
        model = models.Event
        exclude = ('project', 'index')


class SectionSerializer (OrderedSerializerMixin, AddRemoveModelSerializer):
    # DRF makes the wrong default decision for the details field, chosing a
    # CharField. We want something more direct.
    details = serializers.WritableField(required=False)

    class Meta:
        model = models.Section
        exclude = ('project', 'index')


class ProjectSerializer (SlugValidationMixin, AddRemoveModelSerializer):
    events = EventSerializer(many=True, allow_add_remove=True)
    sections = SectionSerializer(many=True, allow_add_remove=True)
    owner = AssociatedProfileSerializer(required=True)

    title = CleanedHtmlField(required=True)
    location = CleanedHtmlField(required=False)
    contact = CleanedHtmlField(required=False)
    # DRF makes the wrong default decision for the details field, chosing a
    # CharField. We want something more direct.
    details = serializers.WritableField(required=False)

    happening_now_description = CleanedHtmlField(required=False)
    get_involved_description = CleanedHtmlField(required=False)

    geometry = fields.GeometryField(required=False)

    class Meta:
        model = models.Project
        exclude = ('last_opened_at', 'last_opened_by', 'last_saved_at', 'last_saved_by')


class ProjectActivitySerializer (AddRemoveModelSerializer):
    last_opened_by = AssociatedProfileSerializer(source='last_opened_by.profile')
    last_saved_by = AssociatedProfileSerializer(source='last_saved_by.profile')

    class Meta:
        model = models.Project
        fields = ('last_opened_at', 'last_opened_by', 'last_saved_at', 'last_saved_by')


# ============================================================
# Roundup-related serializers

class ProjectSummarySerializer (AddRemoveModelSerializer):
    owner = AssociatedProfileSerializer(required=True)
    summary = serializers.SerializerMethodField('get_project_summary')
    geometry = fields.GeometryField(required=False)
    details = serializers.WritableField()

    class Meta:
        model = models.Project
        fields = ('id', 'slug', 'title', 'summary', 'owner', 'geometry', 'location', 'details')

    def get_project_summary(self, project):
        return project.get_summary()


class RoundupSerializer (AddRemoveModelSerializer):
    projects = serializers.SerializerMethodField('get_project_summaries')
    owner = AssociatedProfileSerializer(include=['description'])

    class Meta:
        model = models.Roundup

    def get_project_summaries(self, roundup):
        # For now, we just serialize the complete set of projects owned by the
        # roundup owner.
        qs = roundup.owner.projects.all().filter(public=True)

        serializer = ProjectSummarySerializer(qs, many=True)
        return serializer.data


# ============================================================
# Template serializers, which render objects without their identifying
# information (ids, slugs, etc.). These are output only.

class TemplateEventSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Event
        exclude = ('project', 'index', 'id')


class TemplateSectionSerializer (serializers.ModelSerializer):
    # DRF makes the wrong default decision for the details field, chosing a
    # CharField. We want something more direct.
    #
    # TODO: This will have to clean the HTML on all the attributes, or
    #       something, when applicable.
    details = serializers.WritableField()

    class Meta:
        model = models.Section
        exclude = ('project', 'index', 'id')


class TemplateProjectSerializer (serializers.ModelSerializer):
    events = TemplateEventSerializer(many=True)
    sections = TemplateSectionSerializer(many=True)

    class Meta:
        model = models.Project
        exclude = ('owner', 'slug', 'id', 'public')
