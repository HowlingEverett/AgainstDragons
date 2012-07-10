# Create your views here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.aggregates import Avg, Max, Min
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from dashboard.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import TemplateView
from geosurvey.models import Survey, Trip
from datetime import date, datetime

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


class SurveyDetailView(DetailView):
    template_name = 'dashboard/survey_detail.html'
    model = Survey

    def get_context_data(self, **kwargs):
        context = super(SurveyDetailView, self).get_context_data(**kwargs)
        datestr = self.kwargs.get('date')

        if datestr:
            date = datetime.strptime(datestr, "%Y-%m-%d")
            trip_set = self.get_object().trip_set.filter(date__exact=date)
        else:
            trip_set = self.get_object().trip_set.all()

        paginator = Paginator(trip_set, 10)
        page = self.request.GET.get('page')
        try:
            trips = paginator.page(page)
        except PageNotAnInteger:
            trips = paginator.page(1)
        except EmptyPage:
            trips = paginator.page(paginator.num_pages)

        context['trips'] = trips

        all_trips = Trip.objects.filter(survey__exact=self.get_object())
        context['avg_duration'] = all_trips.aggregate(Avg('duration'))['duration__avg']
        context['max_duration'] = all_trips.aggregate(Max('duration'))['duration__max']
        context['min_duration'] = all_trips.aggregate(Min('duration'))['duration__min']

        context['avg_distance'] = all_trips.aggregate(Avg('distance'))['distance__avg']
        context['max_distance'] = all_trips.aggregate(Max('distance'))['distance__max']
        context['min_distance'] = all_trips.aggregate(Min('distance'))['distance__min']

        return context
