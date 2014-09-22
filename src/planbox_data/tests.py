from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase, RequestFactory
from django_nose.tools import assert_num_queries
from nose.tools import assert_equal, assert_in, assert_raises, ok_, assert_not_equal
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from django.contrib.auth.models import User as UserAuth, AnonymousUser
from planbox_data.models import Profile, Project, Event, Attachment
from planbox_data.permissions import OwnerAuthorizesOrReadOnly
from planbox_data.serializers import ProjectSerializer, ProfileSerializer
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
        UserAuth.objects.all().delete()
        Profile.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()
        Attachment.objects.all().delete()

    def get_view_callback(self, name):
        for urlpattern in self.urlconf.urlpatterns:
            if urlpattern.name == name:
                return urlpattern.callback
        raise ValueError('No pattern named %r. Choices are %r' % (name, [p.name for p in self.urlconf.urlpatterns]))


class ProjectModelTests (TestCase):
    def test_cannot_create_project_with_same_slug_and_owner(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project1 = Project.objects.create(slug='test-1', title='x', location='x', owner=user, public=True)
        project2 = Project.objects.create(slug='test-2', title='x', location='x', owner=user, public=True)

        with assert_raises(IntegrityError):
            project2.slug = 'test-1'
            project2.save()

    def test_can_create_project_with_same_slug_and_different_owner(self):
        auth1 = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user1 = auth1.profile
        auth2 = UserAuth.objects.create_user(username='atogle', password='456')
        user2 = auth2.profile
        project1 = Project.objects.create(slug='test-1', title='x', location='x', owner=user1, public=True)
        project2 = Project.objects.create(slug='test-2', title='x', location='x', owner=user1, public=True)

        project2.slug = 'test-1'
        project2.owner = user2
        project2.save()

        projects = Project.objects.filter(slug='test-1')
        assert_equal(projects.count(), 2)

    def test_can_create_a_project_with_auto_generated_slug(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile

        project1 = Project.objects.create(title='My Project', location='x', owner=user, public=True)
        assert_equal(project1.slug, 'my-project')

        # Ensure conflict resolution
        project2 = Project.objects.create(title='My Project', location='x', owner=user, public=True)
        assert_equal(project2.slug, 'my-project-2')

    def test_auto_generated_slug_strips_html_tags(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile

        project1 = Project.objects.create(title='My <br> Project', location='x', owner=user, public=True)
        assert_equal(project1.slug, 'my-project')

    def test_long_titles_generate_truncated_slugs(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile

        project1 = Project.objects.create(title='A B C D E F G H '*16, location='x', owner=user, public=True)
        # The field's max length is 128, and we leave a 16 character buffer
        # for uniquification.
        assert_equal(project1.slug, 'a-b-c-d-e-f-g-h-'*7)

    def test_long_slugs_leave_room_for_uniquification(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile

        project1 = Project.objects.create(title='A B C D E F G H '*16, location='x', owner=user, public=True)
        assert_equal(project1.slug, 'a-b-c-d-e-f-g-h-'*7)

        project2 = Project.objects.create(title='A B C D E F G H '*16, location='x', owner=user, public=True)
        assert_equal(project2.slug, 'a-b-c-d-e-f-g-h-'*7 + '-2')

    def test_owner_owns_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-1', title='x', location='x', owner=user)

        ok_(project.owned_by(auth))
        ok_(project.owned_by(user))

    def test_non_owner_doesnt_own_project(self):
        auth1 = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user1 = auth1.profile
        project = Project.objects.create(slug='test-1', title='x', location='x', owner=user1)

        auth2 = UserAuth.objects.create_user(username='atogle', password='456')
        user2 = auth2.profile

        ok_(not project.owned_by(auth2))
        ok_(not project.owned_by(user2))

    def test_anon_user_doesnt_own_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-1', title='x', location='x', owner=user)

        anon = AnonymousUser()

        ok_(not project.owned_by(anon))

    def test_can_clone_project(self):
        owner = Profile.objects.create(slug='owner')
        project = Project.objects.create(slug='test-1', title='x', location='x', owner=owner)

        events = [
            Event.objects.create(project=project, slug='event-1'),
            Event.objects.create(project=project, slug='event-2')]

        attachments = [
            Attachment.objects.create(attached_to=events[0], url='http://example.com/file-1'),
            Attachment.objects.create(attached_to=events[0], url='http://example.com/file-2')]

        new_project = project.clone()

        # Make sure the projects are different
        assert_not_equal(project.pk, new_project.pk)

        # Make sure the slugs are the same on the events
        assert_equal(
            [e.slug for e in new_project.events.all()],
            [e.slug for e in events])

        # Make sure the original events still belong to the original project
        assert_equal(
            [e.project_id for e in events],
            [project.pk] * len(events))

        # Make sure the attachments were copied appropriately
        first_event = new_project.events.all()[0]
        assert_equal(
            [a.attached_to_id for a in first_event.attachments.all()],
            [first_event.pk] * len(attachments))

        # Make sure the original attachments still belong to th original event
        assert_equal(
            [a.attached_to_id for a in events[0].attachments.all()],
            [events[0].pk] * len(attachments))


class UserModelTests (PlanBoxTestCase):
    def test_str_requires_no_extra_queries(self):
        '''
        We should not have to make any extra queries to get the string
        representation of a user, after querying for the actual user.
        '''

        UserAuth.objects.create_user(username='mjumbewu', password='123')
        UserAuth.objects.create_user(username='atogle', password='456')

        with assert_num_queries(1):
            profiles = Profile.objects.all()
            profile_strings = set([str(p) for p in profiles])

        # NOTE: The templates profile is created via a migration.
        assert_equal(profile_strings, set(['mjumbewu', 'atogle', 'templates']))


class EventModelTests (PlanBoxTestCase):
    def test_event_indicies_are_generated_correctly(self):
        '''
        Event indicies should be calculated as one more than the highest-index
        event for the projects' timeline.
        '''

        # First event should have index 0
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=user)
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


class ProfileModelTests (PlanBoxTestCase):
    def test_profile_authorizes_owner(self):
        user = UserAuth.objects.create_user(username='mjumbewu', password='123')
        ok_(user.profile.authorizes(user))

    def test_profile_authorizes_superusers(self):
        user = UserAuth.objects.create_user(username='mjumbewu', password='123')
        superuser = UserAuth.objects.create_user(username='admin', password='admin')
        superuser.is_superuser = True
        superuser.save()

        ok_(user.profile.authorizes(superuser))
        ok_(not superuser.profile.authorizes(user))

    def test_profile_authorizes_team_members(self):
        user = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = UserAuth.objects.create_user(username='mjumbewu2', password='345')
        user.profile.members.add(member.profile)

        ok_(user.profile.authorizes(member))
        ok_(not member.profile.authorizes(user))


class ProjectSerializerTests (PlanBoxTestCase):
    def test_project_with_empty_title_is_invalid(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=user)

        serializer = ProjectSerializer(project, data={'slug': '', 'title': ''})
        ok_(not serializer.is_valid(), 'Project with empty slug and title should not validate')
        assert_in('title', serializer.errors)

    def test_events_are_nested_in_data(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=user)
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
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile

        serializer = ProjectSerializer(data={
            'slug': 'test-slug',
            'title': 'test title',
            'location': 'test location',
            'events': [
                {'label': 'test label 1'},
                {'label': 'test label 2'},
                {'label': 'test label 3'}
            ],
            'sections': [],
            'owner': {'slug': profile.slug}
        })

        ok_(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        assert_equal([int(e.label.split()[-1]) for e in project.events.all()], [1, 2, 3])

    def test_events_are_updated_from_nested_data(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=profile)
        events = [
            Event.objects.create(label='test label 1', project=project),
            Event.objects.create(label='test label 3', project=project),
        ]

        serializer = ProjectSerializer(project, data={
            'id': project.pk,
            'slug': 'test-slug',
            'title': 'test new title',
            'location': 'test location',
            'events': [
                {'label': 'test label 3', 'id': events[1].pk},
                {'label': 'test label 2'},
                {'label': 'test label 1', 'id': events[0].pk}
            ],
            'sections': [],
            'owner': {'slug': profile.slug}
        })

        ok_(serializer.is_valid(), serializer.errors)
        new_project = serializer.save()
        assert_equal(project.pk, new_project.pk)
        assert_equal(new_project.title, 'test new title')
        assert_equal([int(e.label.split()[-1]) for e in project.events.all()], [3, 2, 1])
        assert_equal(project.events.all()[0].pk, events[1].pk)
        assert_equal(project.events.all()[2].pk, events[0].pk)

    def test_events_attachments_are_created_from_nested_data(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile

        serializer = ProjectSerializer(data={
            'slug': 'test-slug',
            'title': 'test title',
            'location': 'test location',
            'events': [
                {
                    'label': 'test label',
                    'attachments': [
                        {'label': 'attachment 1', 'url': 'http://example.com/1'},
                        {'label': 'attachment 2', 'url': 'http://example.com/1'}
                    ]
                },
            ],
            'sections': [],
            'owner': {'slug': profile.slug}
        })

        ok_(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        assert_equal([int(a.label.split()[-1]) for a in project.events.all()[0].attachments.all()], [1, 2])

    def test_events_attachments_are_updated_from_nested_data(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=profile)
        event = Event.objects.create(label='test label', project=project)
        attachments = [
            Attachment.objects.create(attached_to=event, label='attachment 1'),
            Attachment.objects.create(attached_to=event, label='attachment 2'),
        ]

        serializer = ProjectSerializer(project, data={
            'id': project.pk,
            'slug': 'test-slug',
            'title': 'test new title',
            'location': 'test location',
            'events': [
                {
                    'label': 'test label',
                    'attachments': [
                        {'label': 'attachment 1', 'url': 'http://example.com/1', 'id': attachments[1].pk},
                        {'label': 'attachment 3', 'url': 'http://example.com/2'},
                        {'label': 'attachment 2', 'url': 'http://example.com/3', 'id': attachments[0].pk},
                    ],
                    'id': event.pk,
                },
            ],
            'sections': [],
            'owner': {'slug': profile.slug}
        })

        ok_(serializer.is_valid(), serializer.errors)
        new_project = serializer.save()
        assert_equal(project.pk, new_project.pk)
        assert_equal(new_project.title, 'test new title')
        new_event = new_project.events.all()[0]
        assert_equal([int(a.label.split()[-1]) for a in new_event.attachments.all()], [1, 3, 2])
        assert_equal([int(a.url.split('/')[-1]) for a in new_event.attachments.all()], [1, 2, 3])
        assert_equal(new_event.attachments.all()[0].pk, attachments[1].pk)
        assert_equal(new_event.attachments.all()[2].pk, attachments[0].pk)

    def test_invalid_project_does_not_raise_exception(self):
        serializer = ProjectSerializer(data={
            # Title and owner is required
            'events': [
                {'label': 'test label 1'},
                {'label': 'test label 2'},
                {'label': 'test label 3'}
            ],
        })

        ok_(not serializer.is_valid())

    def test_null_events_are_invalid_for_new_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile

        serializer = ProjectSerializer(data={
            'slug': 'test-slug',
            'title': 'test title',
            'location': 'test location',
            'events': None,
            'owner': {'slug': profile.slug}
        })

        ok_(not serializer.is_valid())
        assert_in('events', serializer.errors)

    def test_null_events_are_invalid_for_existing_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        profile = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=profile)
        Event.objects.create(label='test label 1', project=project),
        Event.objects.create(label='test label 3', project=project),

        serializer = ProjectSerializer(project, data={
            'id': project.pk,
            'slug': 'test-slug',
            'title': 'test new title',
            'location': 'test location',
            'events': None,
            'owner': {'slug': profile.slug}
        })

        ok_(not serializer.is_valid())
        assert_in('events', serializer.errors)

    def test_project_geometry_create(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=user, geometry='POINT(2 3)')

        serializer = ProjectSerializer(project)
        assert_in('geometry', serializer.data)
        assert_equal(serializer.data['geometry'], {u'type': u'Point', u'coordinates': [2.0, 3.0]})

    def test_project_geometry_update(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        user = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=user, geometry='POINT(2 3)')
        serializer = ProjectSerializer(project, data={
            'id': project.pk,
            'slug': 'test-slug',
            'title': 'test new title',
            'location': 'test location',
            'events': [],
            'sections': [],
            'owner': {'slug': user.slug},
            'geometry': {u'type': u'Point', u'coordinates': [4.0, 5.0]}
        })

        ok_(serializer.is_valid(), serializer.errors)

        serializer.save()
        project = serializer.object

        assert_equal(project.geometry.x, 4.0)
        assert_equal(project.geometry.y, 5.0)


class ProfileSerializerTests (PlanBoxTestCase):
    def test_can_create_a_profile(self):
        serializer = ProfileSerializer(data={
            'name': 'test profile'
        })

        ok_(serializer.is_valid(), serializer.errors)

        serializer.save()
        profile = serializer.object

        assert_equal(profile.name, 'test profile')
        assert_equal(profile.slug, 'test-profile')


class OwnerPermissionTests (PlanBoxTestCase):
    def init_test_assets(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner)
        permission = OwnerAuthorizesOrReadOnly()
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
        auth = UserAuth.objects.create_user(username='atogle', password='456')
        request = self.factory.get('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))

    def test_non_owner_auth_data_not_ok_for_unsafe_requests(self):
        permission, _, _, project = self.init_test_assets()
        auth = UserAuth.objects.create_user(username='atogle', password='456')
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

    def test_member_auth_data_is_ok_for_unsafe_requests(self):
        permission, _, owner, project = self.init_test_assets()
        auth = UserAuth.objects.create_user(username='aogle', password='456')
        owner.members.add(auth.profile)
        request = self.factory.put('')
        request.user = auth
        ok_(permission.has_object_permission(request, None, project))


class ProjectDetailViewAuthenticationTests (PlanBoxTestCase):
    def init_test_assets(self, public=True):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=public)

        kwargs = {'pk': project.pk}
        view = self.get_view_callback('project-detail')
        url = reverse('project-detail', kwargs=kwargs)

        return auth, owner, project, kwargs, view, url

    def test_anonymous_can_GET_detail(self):
        url = self.init_test_assets()[-1]
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_anonymous_cannot_GET_unpublished_detail(self):
        url = self.init_test_assets(public=False)[-1]
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_PUT_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()
        response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "location": "x", "owner": "%s"}' % (owner.slug), content_type='application/json')
        # Even though the user is unauthenticated and a 401 seems like it might
        # be in order, we don't want a www-authenticate response header to be
        # sent, so we'll send a 403.
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_anonymous_gets_403_with_duplicate(self):
        _, owner, project, _, _, url = self.init_test_assets()
        response = self.client.put(url, data='{"id": %s, "title": "%s", "slug": "%s", "events": [], "location": "x", "owner": "%s", "public": true}' % (project.pk, project.title, project.slug, owner.slug), content_type='application/json')
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

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_non_owner_cannot_GET_unpublished_detail(self):
        url = self.init_test_assets(public=False)[-1]

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_404_NOT_FOUND)

    def test_non_owner_cannot_PUT_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        assert_equal(response.status_code, HTTP_403_FORBIDDEN, (response.status_code, str(response)))

    def test_non_owner_cannot_DELETE_detail(self):
        url = self.init_test_assets()[-1]

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_owner_can_GET_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_owner_can_GET_unpublished_detail(self):
        auth, _, _, _, _, url = self.init_test_assets(public=False)
        self.client.login(username=auth.username, password='123')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_owner_can_PUT_detail(self):
        auth, owner, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "sections": [], "location": "x", "owner": {"slug": "%s"}}' % (owner.slug), content_type='application/json')
        assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))

    def test_owner_can_DELETE_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_204_NO_CONTENT)

    def test_member_can_GET_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()
        auth = UserAuth.objects.create_user(username='atogle', password='456')
        owner.members.add(auth.profile)
        self.client.login(username=auth.username, password='456')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_member_can_GET_unpublished_detail(self):
        _, owner, _, _, _, url = self.init_test_assets(public=False)
        auth = UserAuth.objects.create_user(username='atogle', password='456')
        owner.members.add(auth.profile)
        self.client.login(username=auth.username, password='456')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_member_can_PUT_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()
        auth = UserAuth.objects.create_user(username='atogle', password='456')
        owner.members.add(auth.profile)
        self.client.login(username=auth.username, password='456')
        response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "sections": [], "location": "x", "owner": {"slug": "%s"}}' % (owner.slug), content_type='application/json')
        assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))

    def test_member_can_DELETE_detail(self):
        _, owner, _, _, _, url = self.init_test_assets()
        auth = UserAuth.objects.create_user(username='atogle', password='456')
        owner.members.add(auth.profile)
        self.client.login(username=auth.username, password='456')
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_204_NO_CONTENT)


class NonPublicProjectDetailViewAuthenticationTests (PlanBoxTestCase):
    def init_test_assets(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {'pk': project.pk}
        view = self.get_view_callback('project-detail')
        url = reverse('project-detail', kwargs=kwargs)

        return auth, owner, project, kwargs, view, url

    def test_anonymous_cannot_GET_detail(self):
        url = self.init_test_assets()[-1]
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_PUT_detail(self):
        _, owner, project, _, _, url = self.init_test_assets()
        response = self.client.put(url, data='{"id": %s, "title": "%s", "slug": "%s", "events": [], "location": "x", "owner": "%s", "public": false}' % (project.pk, project.title, project.slug, owner.slug), content_type='application/json')
        assert_equal(response.status_code, HTTP_403_FORBIDDEN, response.content)

    def test_anonymous_cannot_DELETE_detail(self):
        url = self.init_test_assets()[-1]
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_403_FORBIDDEN)

    def test_non_owner_cannot_GET_detail(self):
        url = self.init_test_assets()[-1]

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_404_NOT_FOUND)

    def test_non_owner_cannot_PUT_detail(self):
        _, owner, project, _, _, url = self.init_test_assets()

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.put(url, data='{"id": %s, "title": "%s", "slug": "%s", "events": [], "location": "x", "owner": "%s", "public": false}' % (project.pk, project.title, project.slug, owner.slug), content_type='application/json')
        assert_equal(response.status_code, HTTP_403_FORBIDDEN, (response.status_code, str(response)))

    def test_non_owner_cannot_assign_detail_to_themselves(self):
        _, owner, project, _, _, url = self.init_test_assets()

        nonowner = UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.put(url, data='{"id": %s, "title": "%s", "slug": "%s", "events": [], "location": "x", "owner": "%s", "public": false}' % (project.pk, project.title, project.slug, nonowner.username), content_type='application/json')
        assert_equal(response.status_code, HTTP_403_FORBIDDEN, (response.status_code, str(response)))

    def test_non_owner_cannot_DELETE_detail(self):
        url = self.init_test_assets()[-1]

        UserAuth.objects.create_user(username='atogle', password='456')
        self.client.login(username='atogle', password='456')

        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_404_NOT_FOUND)

    def test_owner_can_GET_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.get(url)
        assert_equal(response.status_code, HTTP_200_OK)

    def test_owner_can_PUT_detail(self):
        auth, owner, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "sections": [], "location": "x", "public": false, "owner": {"slug": "%s"}}' % (owner.slug), content_type='application/json')
        assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))

    def test_owner_can_DELETE_detail(self):
        auth, _, _, _, _, url = self.init_test_assets()
        self.client.login(username=auth.username, password='123')
        response = self.client.delete(url)
        assert_equal(response.status_code, HTTP_204_NO_CONTENT)


class ProjectListViewAuthenticationTests (PlanBoxTestCase):
    def init_test_assets(self):
        auths = [
            UserAuth.objects.create_user(username='mjumbewu', password='123'),
            UserAuth.objects.create_user(username='atogle', password='456'),
        ]
        owners = [auth.profile for auth in auths]
        projects = [
            Project.objects.create(slug='test-1', title='x', location='x', owner=owners[0], public=True),
            Project.objects.create(slug='test-2', title='x', location='x', owner=owners[0], public=False),
            Project.objects.create(slug='test-3', title='x', location='x', owner=owners[0], public=True),
            Project.objects.create(slug='test-4', title='x', location='x', owner=owners[1], public=True),
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
        # response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
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
        # response = self.client.put(url, data='{"title": "x", "slug": "x", "events": [], "location": "x", "owner_type": "user", "owner_id": %s}' % (owner.pk), content_type='application/json')
        # assert_equal(response.status_code, HTTP_200_OK, (response.status_code, str(response)))
