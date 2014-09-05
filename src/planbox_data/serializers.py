from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from planbox_data import models
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
            existing_slugs = self.object.get_all_slugs()
            if slug in existing_slugs:
                raise serializers.ValidationError('This slug is already in use.')

        # Letters, numbers, and dashes.
        pattern = r'^[A-Za-z0-9-]*$'
        if not re.match(pattern, slug):
            raise serializers.ValidationError('Use only numbers, letters, and dashes in slugs.')

        return attrs


# ============================================================
# Profile serializers

class AssociatedProfileSerializer (serializers.ModelSerializer):
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


class OwnedProjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'slug', 'title',)


class UserSerializer (serializers.ModelSerializer):
    username = serializers.CharField(source='auth.username')
    teams = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)

    class Meta:
        model = models.Profile


class ProfileSerializer (SlugValidationMixin, serializers.ModelSerializer):
    members = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)
    teams = AssociatedProfileSerializer(required=False, many=True, allow_add_remove=True)
    projects = OwnedProjectSerializer(many=True, read_only=True)

    class Meta:
        model = models.Profile
        exclude = ('project_editor_version',)

    def validate(self, attrs):
        if not attrs.get('name') and not attrs.get('slug'):
            raise serializers.ValidationError('You must specify either a name or a slug.')
        return attrs


# ============================================================
# Project-related serializers

class AttachmentSerializer (OrderedSerializerMixin, serializers.ModelSerializer):
    label = CleanedHtmlField()
    description = CleanedHtmlField(required=False)

    class Meta:
        model = models.Attachment
        exclude = ('attached_to_type', 'attached_to_id', 'index')


class EventSerializer (OrderedSerializerMixin, serializers.ModelSerializer):
    label = CleanedHtmlField()
    description = CleanedHtmlField(required=False)
    attachments = AttachmentSerializer(many=True, required=False, allow_add_remove=True)

    class Meta:
        model = models.Event
        exclude = ('project', 'index')


class SectionSerializer (OrderedSerializerMixin, serializers.ModelSerializer):
    # DRF makes the wrong default decision for the details field, chosing a
    # CharField. We want something more direct.
    details = serializers.WritableField(required=False)

    class Meta:
        model = models.Section
        exclude = ('project', 'index')


class ProjectSerializer (SlugValidationMixin, serializers.ModelSerializer):
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

    class Meta:
        model = models.Project
        exclude = ('last_opened_at', 'last_opened_by', 'last_saved_at', 'last_saved_by')


class ProjectActivitySerializer (serializers.ModelSerializer):
    last_opened_by = AssociatedProfileSerializer(source='last_opened_by.profile')
    last_saved_by = AssociatedProfileSerializer(source='last_saved_by.profile')

    class Meta:
        model = models.Project
        fields = ('last_opened_at', 'last_opened_by', 'last_saved_at', 'last_saved_by')


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
