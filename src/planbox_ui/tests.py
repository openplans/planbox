from django.contrib.sessions.backends.cache import SessionStore
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.utils.timezone import datetime, now, timedelta, utc
from nose.tools import assert_equal, assert_raises, assert_in, assert_not_in
from urllib import urlencode
import responses

from django.contrib.auth.models import User as UserAuth, AnonymousUser
from planbox_data.models import Profile, Project, Event, Theme
from planbox_ui.views import (project_editor_view, project_page_view, new_project_view,
    project_payments_success_view, signup_view, signin_view, profile_view)


class PlanBoxUITestCase (TestCase):
    def setUp(self): self.set_up()
    def tearDown(self): self.tear_down()

    def set_up(self):
        self.factory = RequestFactory()

    def tear_down(self):
        UserAuth.objects.all().delete()
        Profile.objects.all().delete()
        Project.objects.all().delete()
        Event.objects.all().delete()


class SignupViewTests (PlanBoxUITestCase):
    def test_user_is_redirected_home_on_successful_signup(self):
        url = reverse('app-signup')

        user_data = {
            'username': 'mjumbewu',
            'password': '123',
            'email': 'mjumbewu@example.com',
            'affiliation': 'OpenPlans',
        }

        request = self.factory.post(url, data=user_data)
        request.user = AnonymousUser()
        request.session = SessionStore('session')
        response = signup_view(request)

        # If you get a 200 here, it's probably because of wrong form data.
        assert_equal(response.status_code, 302)
        assert_equal(response.url, reverse('app-user-profile'))

        user_profile = Profile.objects.get(auth__username='mjumbewu')
        assert_equal(user_profile.affiliation, 'OpenPlans')

    def test_username_is_case_insensitive(self):
        UserAuth.objects.create_user(username='mjumbewu', password='456')

        url = reverse('app-signup')

        user_data = {
            'username': 'MjumbeWU',
            'password': '123',
            'email': 'mjumbewu@example.com',
            'affiliation': 'OpenPlans',
        }

        request = self.factory.post(url, data=user_data)
        request.user = AnonymousUser()
        request.session = SessionStore('session')
        response = signup_view(request)

        assert_equal(response.status_code, 200)
        assert_in('username', response.context_data['form'].errors)

    def test_username_cannot_have_dots(self):
        # We don't want dots in usernames or slugs because then they couldn't
        # be used as subdomains.
        url = reverse('app-signup')

        user_data = {
            'username': 'mjumbe.wu',
            'password': '123',
            'email': 'mjumbewu@example.com',
            'affiliation': 'OpenPlans',
        }

        request = self.factory.post(url, data=user_data)
        request.user = AnonymousUser()
        request.session = SessionStore('session')
        response = signup_view(request)

        assert_equal(response.status_code, 200)
        assert_in('username', response.context_data['form'].errors)

    def test_user_has_team_based_on_affiliation_by_default(self):
        url = reverse('app-signup')

        user_data = {
            'username': 'mjumbewu',
            'password': '123',
            'email': 'mjumbewu@example.com',
            'affiliation': 'OpenPlans',
        }

        request = self.factory.post(url, data=user_data)
        request.user = AnonymousUser()
        request.session = SessionStore('session')
        response = signup_view(request)

        assert_equal(response.status_code, 302)

        teams = UserAuth.objects.get(username=user_data['username']).profile.teams.all()
        assert_equal(teams.count(), 1)
        assert_equal(teams[0].slug, 'openplans')
        assert_equal(teams[0].name, 'OpenPlans')


class SigninViewTests (PlanBoxUITestCase):
    def test_user_is_redirected_home_on_successful_signin(self):
        UserAuth.objects.create_user(username='mjumbewu', password='123')
        url = reverse('app-signin')

        user_data = {
            'username': 'mjumbewu',
            'password': '123',
        }

        request = self.factory.post(url, data=user_data)
        request.user = AnonymousUser()
        request.session = SessionStore('session')
        response = signin_view(request)
        assert_equal(response.status_code, 302)
        assert_equal(response.url, reverse('app-user-profile'))


class NewProjectViewTests (PlanBoxUITestCase):
    def test_user_gets_redirected_to_own_new_project_page(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner)

        user = UserAuth.objects.create_user(username='atogle', password='456')

        url1_kwargs = {'owner_slug': owner.slug}
        url1 = reverse('app-new-project', kwargs=url1_kwargs)
        url2_kwargs = {}
        url2 = reverse('app-user-profile', kwargs=url2_kwargs)

        request = self.factory.get(url1)
        request.user = user
        response = new_project_view(request, **url1_kwargs)
        assert_equal(response.status_code, 302)
        assert_equal(response.url, url2)

    def test_anon_user_gets_redirected_to_login(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')

        url_kwargs = {'owner_slug': auth.username}
        url = reverse('app-new-project', kwargs=url_kwargs)
        login_url = reverse('app-signin')

        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = new_project_view(request, **url_kwargs)
        assert_equal(response.status_code, 302)
        assert_equal(response.url, login_url + '?next=' + url)


class ProjectEditorViewTests (PlanBoxUITestCase):
    def test_anon_gets_302_to_signin(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_editor_view(request, **kwargs)

        signin_url = reverse('app-signin') + '?next=' + url
        assert_equal(response.status_code, 302)
        assert_equal(response.url, signin_url)

    def test_non_owner_gets_404(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        auth2 = UserAuth.objects.create_user(username='atogle', password='456')
        owner2 = auth2.profile

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth2

        with assert_raises(Http404):
            response = project_editor_view(request, **kwargs)

    def test_owner_gets_editable_details(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_editor_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), True)

    def test_anon_gets_redirect_to_signin_non_public_project(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_editor_view(request, **kwargs)

        signin_url = reverse('app-signin') + '?next=' + url
        assert_equal(response.status_code, 302)
        assert_equal(response.url, signin_url)

    def test_non_owner_gets_404_on_non_public_project(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        auth2 = UserAuth.objects.create_user(username='atogle', password='456')

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth2

        with assert_raises(Http404):
            response = project_editor_view(request, **kwargs)

    def test_owner_gets_editable_details_on_non_public_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_editor_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), True)

    def test_team_member_gets_editable_details_on_non_public_project(self):
        owner = Profile.objects.create(slug='test-slug')
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = auth.profile
        owner.members.add(member)

        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_editor_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), True)

    def test_owner_gets_402_on_expired_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False, expires_at=datetime(1970, 1, 1, tzinfo=utc))

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-editor', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_editor_view(request, **kwargs)

        assert_equal(response.status_code, 402)


class ProjectPaymentsViewsTests (PlanBoxUITestCase):
    def test_anon_user_redirects_to_login_before_payment_success(self):
        owner = Profile.objects.create(slug='openplans')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'pk': project.pk
        }

        url = reverse('app-project-payments-success', kwargs=kwargs) + '?customer_id=12345'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_payments_success_view(request, **kwargs)

        signin_url = reverse('app-signin') + '?next=' + url.replace('?', '%3F').replace('=', '%3D')
        assert_equal(response.status_code, 302)
        assert_equal(response.url, signin_url)

    @responses.activate
    def test_success_from_a_recurring_moonclerk_form(self):
        owner = Profile.objects.create(slug='openplans')
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = auth.profile
        owner.members.add(member)

        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'pk': project.pk
        }

        responses.add(responses.GET, "https://api.moonclerk.com/customers/12345",
                  body='''{"customer":{"id":523425,"account_balance":0,"name":"Ryan Wood","email":"ryan@moonclerk.com","card_last4":"4242","card_type":"Visa","card_exp_month":12,"card_exp_year":2018,"customer_reference":"cus_4SOZuEc4cxP5L7","discount":{"coupon":{"code":"10off","duration":"once","amount_off":1000,"currency":"USD","percent_off":null,"duration_in_months":null,"max_redemptions":null,"redeem_by":null },"starts_at":"2013-04-12T20:05:37Z","ends_at":"2013-05-12T20:05:37Z"},"delinquent":false,"custom_fields":{"shirt_size":{"type":"string","response":"XL"},"shipping_address":{"type":"address","response":{"id":32,"line1":"123 Main St.","line2":"Ste. 153","city":"Greenville","state":"SC","postal_code":"29651","country":"United States"}}},"form_id":101,"checkout":{"date":"2014-07-23T13:44:12Z","subtotal":1000,"fee":200,"upfront_amount":500,"total":1700,"coupon_amount":0,"amount_due":1700,"trial_period_days":null },"subscription":{"id":98,"subscription_reference":"sub_3oLgqlp4MgTZC3","status":"active","start":"2014-07-23T13:44:16Z","first_payment_attempt":"2014-07-23T13:44:16Z","next_payment_attempt":"2014-08-23T13:44:16Z","current_period_start":"2014-07-23T13:44:16Z","current_period_end":"2014-08-23T13:44:16Z","trial_start":null,"trial_end":null,"trial_period_days":null,"expires_at":null,"canceled_at":null,"ended_at":null,"plan":{"id":131,"plan_reference":"131","amount":1200,"currency":"USD","interval":"month","interval_count":1 }}}}''',
                  content_type="application/json")

        url = reverse('app-project-payments-success', kwargs=kwargs) + '?customer_id=12345'
        request = self.factory.get(url)
        request.user = auth
        response = project_payments_success_view(request, **kwargs)

        project_editor_url = reverse('app-project-editor', kwargs={'owner_slug': owner.slug, 'project_slug': project.slug})
        assert_equal(response.status_code, 302)
        assert_equal(response.url, project_editor_url)

        project = Project.objects.get(slug='test-slug', owner=owner)
        customer = project.customer
        assert_equal(customer.customer_id, 12345)
        assert_equal(customer.reference, 'cus_4SOZuEc4cxP5L7')
        assert_equal(customer.user, auth)

    @responses.activate
    def test_success_from_a_onetime_moonclerk_form(self):
        owner = Profile.objects.create(slug='openplans')
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = auth.profile
        owner.members.add(member)

        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'pk': project.pk
        }

        responses.add(responses.GET, "https://api.moonclerk.com/payments/12345",
                  body='''{"payment":{"id":1348394,"date":"2014-04-08T18:57:26Z","status":"successful","currency":"USD","amount":1000,"fee":59,"amount_refunded":0,"name":"Jim Customer","email":"customer@example.com","card_last4":"4242","card_type":"Visa","card_exp_month":12,"card_exp_year":2018,"charge_reference":"ch_3ohpsF8ra5rqjj","customer_reference":null,"invoice_reference":"in_1La8pLqS2UnhPZ","custom_fields":{"shirt_size":{"type":"string","response":"XL"},"shipping_address":{"type":"address","response":{"id":32,"line1":"123 Main St.","line2":"Ste. 153","city":"Greenville","state":"SC","postal_code":"29651","country":"United States"}}},"form_id":112,"coupon":{"code":"10off","duration":"once","amount_off":1000,"currency":"USD","percent_off":null,"duration_in_months":null,"max_redemptions":null,"redeem_by":null}}}''',
                  content_type="application/json")

        url = reverse('app-project-payments-success', kwargs=kwargs) + '?payment_id=12345'
        request = self.factory.get(url)
        request.user = auth
        response = project_payments_success_view(request, **kwargs)

        project_editor_url = reverse('app-project-editor', kwargs={'owner_slug': owner.slug, 'project_slug': project.slug})
        assert_equal(response.status_code, 302)
        assert_equal(response.url, project_editor_url)

        project = Project.objects.get(slug='test-slug', owner=owner)
        assert_equal(project.payments.all().count(), 1)
        payment = project.payments.all()[0]
        assert_equal(payment.payment_id, 12345)
        assert_equal(payment.user, auth)

    @responses.activate
    def test_empty_payment_and_customer_id_is_allowed(self):
        # NOTE: This test should be obsoleted once the MoonClerkk customer_id
        # issues are resolved.
        owner = Profile.objects.create(slug='openplans')
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = auth.profile
        owner.members.add(member)

        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'pk': project.pk
        }

        url = reverse('app-project-payments-success', kwargs=kwargs) + '?customer_id='
        request = self.factory.get(url)
        request.user = auth
        response = project_payments_success_view(request, **kwargs)

        project_editor_url = reverse('app-project-editor', kwargs={'owner_slug': owner.slug, 'project_slug': project.slug})
        assert_equal(response.status_code, 302)
        assert_equal(response.url, project_editor_url)

        project = Project.objects.get(slug='test-slug', owner=owner)
        assert_equal(project.expires_at, None)


class ProjectPageViewTests (PlanBoxUITestCase):
    def test_anon_gets_public_page_with_future_expires(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True, expires_at=(now() + timedelta(days=1)))

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)

    def test_anon_gets_public_page_with_no_expires(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)
        project.expires_at = None
        project.save()

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)

    def test_anon_gets_404_for_non_public_project(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()

        with assert_raises(Http404):
            response = project_page_view(request, **kwargs)

    def test_non_owner_gets_404_on_non_public_project(self):
        owner = Profile.objects.create(slug='mjumbewu')
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        auth2 = UserAuth.objects.create_user(username='atogle', password='456')

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth2

        with assert_raises(Http404):
            response = project_page_view(request, **kwargs)

    def test_owner_gets_uneditable_details_on_non_public_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)

    def test_team_member_gets_uneditable_details_on_non_public_project(self):
        owner = Profile.objects.create(slug='test-slug')
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        member = auth.profile
        owner.members.add(member)

        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)

    def test_owner_gets_404_on_expired_project(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=False, expires_at=datetime(1970, 1, 1, tzinfo=utc))

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth

        with assert_raises(Http404):
            response = project_page_view(request, **kwargs)


class ProjectThemeTests (PlanBoxUITestCase):
    def test_can_render_project_with_theme(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        theme = Theme.objects.create(definition={'css': 'http://example.com/style.css'})
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, theme=theme, public=True)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)
        response.render()
        assert_in('<link rel="stylesheet" href="http://example.com/style.css">', response.content.decode('utf-8'))

    def test_can_render_project_without_theme(self):
        auth = UserAuth.objects.create_user(username='mjumbewu', password='123')
        owner = auth.profile
        project = Project.objects.create(slug='test-slug', title='test title', location='test location', owner=owner, public=True)

        kwargs = {
            'owner_slug': owner.slug,
            'project_slug': project.slug
        }

        url = reverse('app-project-page', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = project_page_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_equal(response.context_data.get('is_editable'), False)
        response.render()
        assert_not_in('<link rel="stylesheet" href="http://example.com/style.css">', response.content.decode('utf-8'))



class ProfileAdminTests (PlanBoxUITestCase):
    def test_anon_gets_redirect_to_signin(self):
        profile = Profile.objects.create(slug='mjumbewu')

        kwargs = {
            'profile_slug': profile.slug,
        }

        url = reverse('app-profile', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = profile_view(request, **kwargs)

        signin_url = reverse('app-signin') + '?next=' + url
        assert_equal(response.status_code, 302)
        assert_equal(response.url, signin_url)

    def test_non_member_gets_redirect_to_home(self):
        profile = Profile.objects.create(slug='mjumbewu')

        kwargs = {
            'profile_slug': profile.slug,
        }

        auth = UserAuth.objects.create_user(username='atogle', password='456')

        url = reverse('app-profile', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = profile_view(request, **kwargs)

        home_url = reverse('app-index')
        assert_equal(response.status_code, 302)
        assert_equal(response.url, home_url)

    def test_member_gets_profile_admin(self):
        profile = Profile.objects.create(slug='mjumbewu')

        kwargs = {
            'profile_slug': profile.slug,
        }

        auth = UserAuth.objects.create_user(username='atogle', password='456')
        member = auth.profile
        profile.members.add(member)

        url = reverse('app-profile', kwargs=kwargs)
        request = self.factory.get(url)
        request.user = auth
        response = profile_view(request, **kwargs)

        assert_equal(response.status_code, 200)
        assert_in('profile_data', response.context_data)
        assert_equal(response.context_data['profile_data']['slug'], profile.slug)

