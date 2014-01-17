from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import assert_equal

from django.contrib.auth.models import User as AuthUser, AnonymousUser
from planbox_data.models import User, Project, Event


class PlanBoxUITestCase (TestCase):
    def setUp(self): self.set_up()
    def tearDown(self): self.tear_down()

    def set_up(self):
        pass

    def tear_down(self):
        AuthUser.objects.all().delete()
        User.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()


# class ProjectDetailsTests (PlanBoxUITestCase):
#     def test_anon_gets_non_editable_details(self):
#         auth = AuthUser.objects.create_user(username='mjumbewu', password='123')
#         owner = User.objects.create(auth=auth)
#         project = Project.objects.create(slug='test-slug', title='test title', location='test location', description='test description', owner=owner)

#         kwargs = {
#             'owner_name': 'mjumbewu',
#             'slug': 'test-slug'
#         }

#         url = reverse('app-project', kwargs=kwargs)
#         response = self.client.get(url)

#         assert_equal(response.status_code, 200)
