from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from custom_domains.models import DomainMapping
from custom_domains.context_processors import StaticContextProcessor


class StaticContextProcessorTests (TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(STATIC_URL='/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_canonical_root_if_supplied(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '//myserver.com/static/'})

    @override_settings(STATIC_URL='/static/', CANONICAL_ROOT='')
    def test_uses_default_if_canonical_url_not_specified(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '/static/'})

    @override_settings(STATIC_URL='http://bucket.s3.aws.com/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_default_if_default_is_absolute(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': 'http://bucket.s3.aws.com/static/'})

    @override_settings(STATIC_URL='//bucket.s3.aws.com/static/', CANONICAL_ROOT='//myserver.com/')
    def test_uses_default_if_default_is_absolute_and_schemeless(self):
        static = StaticContextProcessor()
        request = self.factory.get('/root1/path')

        context = static(request)
        self.assertEqual(context, {'STATIC_URL': '//bucket.s3.aws.com/static/'})
