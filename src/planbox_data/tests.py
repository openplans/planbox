from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase, RequestFactory
from django_nose.tools import assert_num_queries
from nose.tools import assert_equal, assert_in, assert_raises, ok_
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from django.contrib.auth.models import User as AuthUser, AnonymousUser
from planbox_data.models import User, Project, Event
from planbox_data.permissions import IsOwnerOrReadOnly
from planbox_data.serializers import ProjectSerializer
from planbox_data.views import router


class PlanBoxTestCase (TestCase):
    def setUp(self): self.set_up()
    def tearDown(self): self.tear_down()

    def set_up(self):
        class URLConf:
            urlpatterns = router.urls
        self.urlconf = URLConf
        self.factory = RequestFactory()

    def tear_down(self):
        AuthUser.objects.all().delete()
        User.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()

    def get_view_callback(self, name):
        for urlpattern in self.urlconf.urlpatterns:
            if urlpattern.name == name:
                return urlpattern.callback
        raise ValueError('No pattern named %r. Choices are %r' % (name, [p.name for p in self.urlconf.urlpatterns]))


class ProjectModelTests (TestCase):
    def test_cannot_create_project_with_same_slug_and_owner(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user = User.objects.create(auth=auth)
        project1 = Project.objects.create(slug='test-1', title='x', location='x', description='x', owner=user)
        project2 = Project.objects.create(slug='test-2', title='x', location='x', description='x', owner=user)

        with assert_raises(IntegrityError):
            project2.slug = 'test-1'
            project2.save()

    def test_can_create_project_with_same_slug_and_different_owner(self):
        auth1 = AuthUser.objects.create_user(username='mjumbewu', password='123')
        user1 = User.objects.create(auth=auth1)
        auth2 = AuthUser.objects.create_user(username='atogle', password='456')
        user2 = User.objects.create(auth=auth2)
        project1 = Project.objects.create(slug='test-1', title='x', location='x', description='x', owner=user1)
        project2 = Project.objects.create(slug='test-2', title='x', location='x', description='x', owner=user1)

        project2.slug = 'test-1'
        project2.owner = user2
        project2.save()

        projects = Project.objects.filter(slug='test-1')
        assert_equal(projects.count(), 2)


class UserModelTests (PlanBoxTestCase):
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


class EventModelTests (PlanBoxTestCase):
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


class ProjectSerializerTests (PlanBoxTestCase):
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



class OwnerPermissionTests (PlanBoxTestCase):
    def init_test_assets(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        owner = User.objects.create(auth=auth)
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=owner)
        permission = IsOwnerOrReadOnly()
        return permission, auth, owner, project

    def test_null_auth_data_is_handled(self):
        permission, _, _, project = self.init_test_assets()
        request = self.factory.put('')
        request.user = None
        ok_(not permission.has_object_permission(request, None, project))

    def test_anon_auth_data_is_ok_for_safe_requests(self):
        permission, _, _, project = self.init_test_assets()
        request = self.factory.get('')
        request.user = AnonymousUser()
        ok_(permission.has_object_permission(request, None, project))

    def test_anon_auth_data_not_ok_for_unsafe_requests(self):
        permission, _, _, project = self.init_test_assets()
        request = self.factory.put('')
        request.user = AnonymousUser()
        ok_(not permission.has_object_permission(request, None, project))

    def test_non_owner_auth_data_is_ok_for_safe_requests(self):
        permission, _, _, project = self.init_test_assets()
        auth = AuthUser.objects.create_user(username='atogle', password='456')
        User.objects.create(auth=auth)
        request = self.factory.get('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))

    def test_non_owner_auth_data_not_ok_for_unsafe_requests(self):
        permission, _, _, project = self.init_test_assets()
        auth = AuthUser.objects.create_user(username='atogle', password='456')
        User.objects.create(auth=auth)
        request = self.factory.put('')
        request.user = auth
        ok_(not permission.has_object_permission(request, None, project))

    def test_no_owner_data_is_ok_for_safe_requests(self):
        permission, _, _, project = self.init_test_assets()
        auth = AuthUser.objects.create_user(username='atogle', password='456')
        request = self.factory.get('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))

    def test_no_owner_data_not_ok_for_unsafe_requests(self):
        permission, _, _, project = self.init_test_assets()
        auth = AuthUser.objects.create_user(username='atogle', password='456')
        request = self.factory.put('')
        request.user = auth
        ok_(not permission.has_object_permission(request, None, project))

    def test_owner_auth_data_is_ok_for_safe_requests(self):
        permission, auth, _, project = self.init_test_assets()
        request = self.factory.get('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))

    def test_owner_auth_data_is_ok_for_unsafe_requests(self):
        permission, auth, _, project = self.init_test_assets()
        request = self.factory.put('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))


class ProjectDetailViewAuthenticationTests (PlanBoxTestCase):
    def init_test_assets(self):
        auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
        owner = User.objects.create(auth=auth)
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=owner)

        kwargs = {'pk': project.pk}
        view = self.get_view_callback('project-detail')
        url = reverse('project-detail', kwargs=kwargs)

        return auth, owner, project, kwargs, view, url

    def test_anonymous_can_GET_detail(self):
        url = self.init_test_assets()[-1]
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_anonymous_cannot_PUT_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()
        response = self.client.put(url, data='{"title": "x", "slug": "x", "description": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        # Even though the user is unauthenticated and a 401 seems like it might
        # be in order, we don't want a www-authenticate response header to be
        # sent, so we'll send a 403.
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_DELETE_detail(self):
        url = self.init_test_assets()[-1]
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_non_owner_can_GET_detail(self):
        url = self.init_test_assets()[-1]

        auth = AuthUser.objects.create_user(username='atogle', password='456')
        nonowner = User.objects.create(auth=auth)
        self.client.login(username='atogle', password='456')

        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_non_owner_cannot_PUT_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()

        auth = AuthUser.objects.create_user(username='atogle', password='456')
        nonowner = User.objects.create(auth=auth)
        self.client.login(username='atogle', password='456')

        response = self.client.put(url, data='{"title": "x", "slug": "x", "description": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        assert_equal(response.status_code, HTTP_403_FORBIDDEN, (response.status_code, str(response)))

    def test_non_owner_cannot_DELETE_detail(self):
        url = self.init_test_assets()[-1]

        auth = AuthUser.objects.create_user(username='atogle', password='456')
        nonowner = User.objects.create(auth=auth)
        self.client.login(username='atogle', password='456')

        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_owner_can_GET_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_owner_can_PUT_detail(self):
        auth, owner, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.put(url, data='{"title": "x", "slug": "x", "description": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))

    def test_owner_can_DELETE_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_204_NO_CONTENT)



class ProjectListViewAuthenticationTests (PlanBoxTestCase):
    def init_test_assets(self):
        auths = [
            AuthUser.objects.create_user(username='mjumbewu', password='123'),
            AuthUser.objects.create_user(username='atogle', password='456'),
        ]
        owners = [
            User.objects.create(auth=auths[0]),
            User.objects.create(auth=auths[1]),
        ]
        projects = [
            Project.objects.create(slug='test-1', title='x', location='x', description='x', owner=owners[0]),
            Project.objects.create(slug='test-2', title='x', location='x', description='x', owner=owners[0]),
            Project.objects.create(slug='test-3', title='x', location='x', description='x', owner=owners[0]),
            Project.objects.create(slug='test-4', title='x', location='x', description='x', owner=owners[1]),
        ]

        kwargs = {}
        view = self.get_view_callback('project-list')
        url = reverse('project-list', kwargs=kwargs)

        return auths, owners, projects, kwargs, view, url

    def test_anonymous_can_GET_list_of_public_projects(self):
        pass
        # url = self.init_test_assets()[-1]
        # response = self.client.get(url)
        # assert_equal(response.status_code, HTTP_200_OK)

    def test_anonymous_cannot_POST_new_project(self):
        pass
        # _, owner, _, _, _, url = self.init_test_assets()
        # response = self.client.put(url, data='{"title": "x", "slug": "x", "description": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        # # Even though the user is unauthenticated and a 401 seems like it might
        # # be in order, we don't want a www-authenticate response header to be
        # # sent, so we'll send a 403.
        # assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_authed_user_can_GET_list_of_public_and_all_own_projects(self):
        pass
        # auth, _, _, _, _, url = self.init_test_assets()
        # self.client.login(username=auth.username, password='123')
        # response = self.client.get(url)
        # assert_equal(response.status_code, HTTP_200_OK)

    def test_authed_user_can_POST_new_project(self):
        pass
        # auth, owner, _, _, _, url = self.init_test_assets()
        # self.client.login(username=auth.username, password='123')
        # response = self.client.put(url, data='{"title": "x", "slug": "x", "description": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        # assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))
