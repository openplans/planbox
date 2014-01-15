from django.test import TestCase
from nose.tools import assert_equal, assert_in, ok_
from django_nose.tools import assert_num_queries

from django.contrib.auth.models import User as AuthUser
from planbox_data.models import User, Project, Event
from planbox_data.serializers import ProjectSerializer

class UserModelTests (TestCase):
    def tear_down(self):
        AuthUser.objects.all().delete()
        User.objects.all().delete()

    def test_str_requires_no_extra_queries(self):
        '''
        We should not have to make any extra queries to get the string
        representation of a user, after querying for the actual user.
        '''

        auth1 = AuthUser.objects.create_user(username='mjumbewu', password='123')
        auth2 = AuthUser.objects.create_user(username='atogle', password='456')
        User.objects.create(auth=auth1)
        User.objects.create(auth=auth2)

        with assert_num_queries(1):
            users = User.objects.all()
            user_strings = [str(u) for u in users]

        assert_equal(user_strings, ['mjumbewu', 'atogle'])


class EventModelTests (TestCase):
    def tear_down(self):
        AuthUser.objects.all().delete()
        User.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()

    def test_event_indicies_are_generated_correctly(self):
        '''
        Event indicies should be calculated as one more than the highest-index
        event for the projects' timeline.
        '''

        # First event should have index 0
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user = User.objects.create(auth=auth)
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=user)
        event_0 = Event.objects.create(label='test label 0', project=project)
        assert_equal(event_0.index, 0)

        # Next events should be consecutive indexes
        next_events = [
            Event.objects.create(label='test label 1', project=project),
            Event.objects.create(label='test label 2', project=project),
            Event.objects.create(label='test label 3', project=project),
        ]
        assert_equal([e.index for e in next_events], [1, 2, 3])

        # Events for other projects should not affect the order
        unrelated_project = Project.objects.create(slug='test-unrelated-slug', title='test unrelated title', location='test unrelated location', owner=user)
        Event.objects.create(label='test unrelated label', project=unrelated_project)
        event_4 = Event.objects.create(label='test label 4', project_id=project.pk)
        assert_equal(event_4.index, 4)


class ProjectSerializerTests (TestCase):
    def tear_down(self):
        AuthUser.objects.all().delete()
        User.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()

    def test_events_are_nested_in_data(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user = User.objects.create(auth=auth)
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=user)
        events = [
            Event.objects.create(label='test label 1', project=project),
            Event.objects.create(label='test label 2', project=project),
            Event.objects.create(label='test label 3', project=project),
        ]

        serializer = ProjectSerializer(project)
        data = serializer.data

        assert_in('events', data)
        assert_equal(len(data['events']), 3)
        assert_equal([int(e['label'].split()[-1]) for e in data['events']], [1, 2, 3])

    def test_events_are_created_from_nested_data(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user = User.objects.create(auth=auth)

        serializer = ProjectSerializer(data={
            'slug': 'test-slug',
            'title': 'test title',
            'location': 'test location',
            'description': 'test description',
            'events': [
                {'label': 'test label 1'},
                {'label': 'test label 2'},
                {'label': 'test label 3'}
            ],
            'owner_type': 'user',
            'owner_id': user.pk
        })

        ok_(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        assert_equal([int(e.label.split()[-1]) for e in project.events.all()], [1, 2, 3])

    def test_events_are_updated_from_nested_data(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user = User.objects.create(auth=auth)
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=user)
        events = [
            Event.objects.create(label='test label 1', project=project),
            Event.objects.create(label='test label 3', project=project),
        ]

        serializer = ProjectSerializer(project, data={
            'id': project.pk,
            'slug': 'test-slug',
            'title': 'test new title',
            'location': 'test location',
            'description': 'test description',
            'events': [
                {'label': 'test label 3', 'id': events[1].pk},
                {'label': 'test label 2'},
                {'label': 'test label 1', 'id': events[0].pk}
            ],
            'owner_type': 'user',
            'owner_id': user.pk
        })

        ok_(serializer.is_valid(), serializer.errors)
        new_project = serializer.save()
        assert_equal(project.pk, new_project.pk)
        assert_equal(new_project.title, 'test new title')
        assert_equal([int(e.label.split()[-1]) for e in project.events.all()], [3, 2, 1])
        assert_equal(project.events.all()[0].pk, events[1].pk)
        assert_equal(project.events.all()[2].pk, events[0].pk)

    def test_invalid_project_does_not_raise_exception(self):
        serializer = ProjectSerializer(data={
            'events': [
                {'label': 'test label 1'},
                {'label': 'test label 2'},
                {'label': 'test label 3'}
            ],
        })

        ok_(not serializer.is_valid())
