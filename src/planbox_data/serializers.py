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


class EventSerializer (OrderedSerializerMixin, serializers.ModelSerializer):
    label = CleanedHtmlField()
    description = CleanedHtmlField(required=False)

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


class ProjectSerializer (serializers.ModelSerializer):
    events = EventSerializer(many=True, allow_add_remove=True)
    sections = SectionSerializer(many=True, allow_add_remove=True)
    owner = serializers.SlugRelatedField(slug_field='slug')

    title = CleanedHtmlField()
    location = CleanedHtmlField(required=False)
    description = CleanedHtmlField(required=False)
    contact = CleanedHtmlField(required=False)

    class Meta:
        model = models.Project


class UserSerializer (serializers.ModelSerializer):
    username = serializers.CharField(source='auth.username')

    class Meta:
        model = models.Profile
