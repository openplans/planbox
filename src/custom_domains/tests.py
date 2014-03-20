from django.http import Http404
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from custom_domains.context_processors import StaticContextProcessor
from custom_domains.middleware import CustomDomainResolvingMiddleware
from custom_domains.models import DomainMapping, DefaultDomainMapping


class StaticContextProcessorTests (TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(STATIC_URL='/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_canonical_root_if_supplied(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')
        request.META['HTTP_HOST'] = 'www.unknownserver.com'

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '//myserver.com/static/'})

    @override_settings(STATIC_URL='/static/', CANONICAL_ROOT='')
    def test_uses_default_if_canonical_url_not_specified(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')
        request.META['HTTP_HOST'] = 'www.unknownserver.com'

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '/static/'})

    @override_settings(STATIC_URL='http://bucket.s3.aws.com/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_default_if_default_is_absolute(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')
        request.META['HTTP_HOST'] = 'www.unknownserver.com'

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': 'http://bucket.s3.aws.com/static/'})

    @override_settings(STATIC_URL='//bucket.s3.aws.com/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_default_if_default_is_absolute_and_schemeless(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')
        request.META['HTTP_HOST'] = 'www.unknownserver.com'

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '//bucket.s3.aws.com/static/'})


@override_settings(KNOWN_HOSTS=['example.com', 'www.example.com'])
class CustomDomainMiddlewareTests (TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        DomainMapping.objects.all().delete()

    def test_default_mapping_is_used_for_known_host(self):
        request = self.factory.get('/root/path')
        request.META['HTTP_HOST'] = 'www.example.com'
        middleware = CustomDomainResolvingMiddleware()

        middleware.process_request(request)
        self.assertEqual(request.domain_mapping.domain, request.META['HTTP_HOST'])
        self.assertTrue(isinstance(request.domain_mapping, DefaultDomainMapping))

    @override_settings()
    def test_mapping_is_used_for_registered_host(self):
        DomainMapping.objects.create(domain='www.registeredserver.com', root_path='/root')
        request = self.factory.get('/path')
        request.META['HTTP_HOST'] = 'www.registeredserver.com'
        middleware = CustomDomainResolvingMiddleware()

        middleware.process_request(request)
        self.assertEqual(request.domain_mapping.domain, request.META['HTTP_HOST'])
        self.assertTrue(isinstance(request.domain_mapping, DomainMapping))
        self.assertEqual(request.path_info, '/root/path')
        self.assertEqual(request.actual_path_info, '/path')

    @override_settings()
    def test_404_is_raised_for_unknown_host(self):
        request = self.factory.get('/root/path')
        request.META['HTTP_HOST'] = 'www.unknownserver.com'
        middleware = CustomDomainResolvingMiddleware()

        with self.assertRaises(Http404):
            middleware.process_request(request)
