from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required

from geosurvey.models import *
from dashboard.views import *

urlpatterns = patterns('',
    url(r'^$', login_required(ListView.as_view(
        model=Survey,
        template_name='dashboard/survey_list.html',
        context_object_name='surveys'
    )), name="survey_list"),

    # Survey CRUD
    url(r'^survey/create/$', permission_required('geosurvey.can_create_survey')(CreateView.as_view(
        model=Survey,
        template_name='dashboard/survey_form.html',
        success_url=reverse_lazy('survey_list'),
    )), name="survey_create"),
    url(r'^survey/(?P<pk>\d+)/edit/$', permission_required('geosurvey.can_update_survey')(UpdateView.as_view(
        model=Survey,
        template_name='dashboard/survey_form.html',
        success_url=reverse_lazy('survey_list'),
    )), name="survey_edit"),
    url(r'^survey/(?P<pk>\d+)/delete/$', permission_required('geosurvey.can_delete_survey')(DeleteView.as_view(
        model=Survey,
        success_url=reverse_lazy('survey_list'),
    )), name="survey_delete"),

    # Survey Detail URLs
    url(r'^survey/(?P<pk>\d+)/$', login_required(SurveyDetailView.as_view(
            model=Survey,
            template_name='dashboard/survey_detail.html'
        )), name="survey_detail"),
    url(r'^trip/(?P<pk>\d+)/', login_required(DetailView.as_view(
        model=Trip,
        template_name="dashboard/trip_detail.html"
    )), name="trip_detail"),

    url(r'^participant/$', login_required(ParticipantPageView.as_view()), name='participant_page'),


)
