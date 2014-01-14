from django.views.generic import TemplateView


# App
class IndexView (TemplateView):
    template_name = 'index.html'


class SignupView (TemplateView):
    template_name = 'signup.html'


class PasswordResetView (TemplateView):
    template_name = 'password-reset.html'


class SigninView (TemplateView):
    template_name = 'signin.html'


class ProjectView (TemplateView):
    template_name = 'project.html'

# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
