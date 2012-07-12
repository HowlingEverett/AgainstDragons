# Create your views here.
from itertools import chain
from django.contrib.auth.models import User
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GPolyline, GEvent
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.aggregates import Avg, Max, Min
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from dashboard.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import TemplateView
from geosurvey.models import Survey, Trip, GeographicalSample
from datetime import datetime
import csv

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
        datestr = self.request.GET.get('date')
        participant_id = self.request.GET.get('participant')

        trip_set = self.get_object().trip_set.all()
        if datestr:
            date = datetime.strptime(datestr, "%Y-%m-%d").date()
            context['date'] = datestr
            trip_set = trip_set.filter(date__exact=date)
        if participant_id and int(participant_id) != 0:
            pk = int(participant_id)
            context['participant_id'] = participant_id
            trip_set = trip_set.filter(participant__exact=pk)

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
        context['avg_duration'] = all_trips.aggregate(Avg('duration'))[
                                  'duration__avg']
        context['max_duration'] = all_trips.aggregate(Max('duration'))[
                                  'duration__max']
        context['min_duration'] = all_trips.aggregate(Min('duration'))[
                                  'duration__min']

        context['avg_distance'] = all_trips.aggregate(Avg('distance'))[
                                  'distance__avg']
        context['max_distance'] = all_trips.aggregate(Max('distance'))[
                                  'distance__max']
        context['min_distance'] = all_trips.aggregate(Min('distance'))[
                                  'distance__min']

        context['participants'] = User.objects.all()

        return context


class TripDetailView(DetailView):
    template_name = 'dashboard/trip_detail.html'
    model = Trip

    def get_context_data(self, **kwargs):
        context = super(TripDetailView, self).get_context_data(**kwargs)

        sample_set = self.get_object().geographicalsample_set.all().order_by('-timestamp')
        paginator = Paginator(sample_set, 25)
        page = self.request.GET.get('page')
        try:
            samples = paginator.page(page)
        except PageNotAnInteger:
            samples = paginator.page(1)
        except EmptyPage:
            samples = paginator.page(paginator.num_pages)

        context['samples'] = samples
        if self.get_object().path:
            polyline = GPolyline(self.get_object().path)
            v3_polyline = polyline.points.replace("GLatLng", "google.maps.LatLng")
            context['map'] = GoogleMap(
                api_url="http://maps.googleapis"\
                        ".com/maps/api/js?sensor=true&amp;key="
                , polylines=[polyline])
        else:
            context['map'] = GoogleMap(
                api_url="http://maps.googleapis"\
                        ".com/maps/api/js?sensor=true&amp;key=")
            #        event = GEvent('click', )

        return context


class CSVDumpView(ListView):
    def get(self, request, *args, **kwargs):
        super(CSVDumpView, self).get(request, *args, **kwargs)
        response = HttpResponse(mimetype='text/csv')
        response[
        'Content-Disposition'] = 'attachment; filename=sampleexport.csv'

        writer = csv.writer(response)
        writer.writerow((
            "timestamp", "latitude", "longitude", "speed", "heading",
            "location_accuracy", "heading_accuracy", "trip_id",
            "participant_id"))
        for sample in self.object_list:
            writer.writerow((
                sample.timestamp, sample.location.y, sample.location.x,
                sample.speed
                , sample.heading, sample.location_accuracy,
                sample.heading_accuracy,
                sample.trip.pk, sample.participant.pk))

        return response


class TripExportView(CSVDumpView):
    def get_queryset(self):
        trip = Trip.objects.get(pk=self.kwargs['pk'])
        return trip.geographicalsamples_set.all().order_by(
            'participant__pk', 'timestamp')


class SurveyExportView(CSVDumpView):
    def get_queryset(self):
        samples = []
        survey = Survey.objects.get(pk=self.kwargs['pk'])
        trips = survey.trip_set.all()
        if self.request.GET.get('date'):
            date = datetime.strptime(self.request.GET['date'],
                                     "%Y-%m-%d").date()
            trips = trips.filter(date__exact=date)
        for trip in trips:
            sample_set = trip.geographicalsample_set.all().order_by('participant__pk', 'timestamp')
            if len(sample_set) > 0:
                samples = chain(samples, sample_set.order_by(
                    'participant__pk', 'timestamp'))
        return samples