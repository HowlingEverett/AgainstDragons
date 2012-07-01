# Create your views here.
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from dashboard.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import TemplateView

class RegistrationView(FormView):
    form_class = RegistrationForm
    template_name = 'dashboard/participant_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        return HttpResponseRedirect(self.get_success_url())

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'dashboard/participant_login.html'

    def get_success_url(self):
        if self.request.user.is_superuser():
            return reverse('survey_list')
        else:
            return reverse('participant_page')

class ParticipantPageView(TemplateView):
    template_name = 'participant_index.html'

    def get_context_data(self, **kwargs):
        pass
