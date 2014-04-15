from django.conf import settings
from django.test import TestCase, Client
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.utils.timezone import now
from password_reset.models import PasswordResetRequest


UserAuth = auth.get_user_model()


class TestPasswordResetViewRedirect (TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserAuth.objects.create_user(
            username='abc',
            password='123',
            email='user@example.com')
        self.reset = PasswordResetRequest.objects.create(
            token='12345678',
            auth=self.user)

    def tearDown(self):
        UserAuth.objects.all().delete()
        PasswordResetRequest.objects.all().delete()

    def test_valid_reset_redirects_to_profile_view(self):
        reset_url = reverse('password-reset', kwargs={'token': self.reset.token})
        profile_url = resolve_url(settings.LOGIN_REDIRECT_URL)
        response = self.client.post(reset_url, data={'password': 'new_pa$$w0rd', 'password_confirm': 'new_pa$$w0rd'})
        self.assertRedirects(response, profile_url, target_status_code=302)


class TestPasswordResetViewProtection (TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserAuth.objects.create_user(
            username='abc',
            password='123',
            email='user@example.com')
        self.reset = PasswordResetRequest.objects.create(
            token='12345678',
            auth=self.user)

    def tearDown(self):
        UserAuth.objects.all().delete()
        PasswordResetRequest.objects.all().delete()

    def test_valid_reset_is_expired_after_use(self):
        reset_url = reverse('password-reset', kwargs={'token': self.reset.token})
        self.client.post(reset_url, data={'password': 'new_pa$$w0rd', 'password_confirm': 'new_pa$$w0rd'})
        reset = PasswordResetRequest.objects.get(token=self.reset.token)
        self.assertTrue(reset.is_expired())

    def test_GET_with_expired_reset_causes_404(self):
        self.reset.expires_at = now()
        self.reset.save()
        self.assertTrue(self.reset.is_expired())

        reset_url = reverse('password-reset', kwargs={'token': self.reset.token})
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 404)

    def test_POST_with_expired_reset_causes_404(self):
        self.reset.expires_at = now()
        self.reset.save()
        self.assertTrue(self.reset.is_expired())

        reset_url = reverse('password-reset', kwargs={'token': self.reset.token})
        response = self.client.post(reset_url, data={'password': 'new_pa$$w0rd', 'password_confirm': 'new_pa$$w0rd'})
        self.assertEqual(response.status_code, 404)
