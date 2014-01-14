from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from planbox_data import models


class EventSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Event
        exclude = ('project', 'index')


class ProjectSerializer (serializers.ModelSerializer):
    events = EventSerializer(many=True)
    owner_type = serializers.SlugRelatedField(slug_field='model', queryset=ContentType.objects.filter(models.Project.OWNER_MODEL_CHOICES))

    class Meta:
        model = models.Project

    def from_native(self, data, files):
        project = super(ProjectSerializer, self).from_native(data, files)

        if data and project:
            events_data = data.get('events', [])
            events_serializer = EventSerializer(data=events_data, many=True)

            if not events_serializer.is_valid():
                raise serializers.ValidationError({'events': events_serializer.errors})

            events = events_serializer.object
            for index, event in enumerate(events):
                event.project = project
                event.index = index

        return project
