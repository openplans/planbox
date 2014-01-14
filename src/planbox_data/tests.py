from django.test import TestCase
from nose.tools import assert_equal
from django_nose.tools import assert_num_queries

from django.contrib.auth.models import User as AuthUser
from planbox_data.models import User, Project, Event


class UserTests (TestCase):
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


class EventTests (TestCase):
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
