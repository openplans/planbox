from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from planbox_data import models


class EventSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Event
        exclude = ('project', 'index')

    def field_from_native(self, data, files, field_name, into):
        super(EventSerializer, self).field_from_native(data, files, field_name, into)

        # If this is being used as a field, respect the order of the items.
        # Renumber the index values to reflect the incoming order.
        if self.many and field_name in into:
            for index, event in enumerate(into[field_name]):
                event.index = index


class ProjectSerializer (serializers.ModelSerializer):
    events = EventSerializer(many=True, allow_add_remove=True)
    owner_type = serializers.SlugRelatedField(slug_field='model', queryset=ContentType.objects.filter(models.Project.OWNER_MODEL_CHOICES))

    class Meta:
        model = models.Project
