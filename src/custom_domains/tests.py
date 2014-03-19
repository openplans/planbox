from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from custom_domains.models import DomainMapping
from custom_domains.context_processors import static


class StaticContextProcessorTests (TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(STATIC_URL='/static/')
    def test_stubbing_path_info_has_no_request(self):
        request = self.factory.get('/root1/path')
        request.path_info = '/root2/path'

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': 'http://testserver/static/'})
