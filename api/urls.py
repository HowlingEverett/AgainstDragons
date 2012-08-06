from django.conf.urls import patterns, url
from api.views import *

urlpatterns = patterns('',
    
    url(r'^$', ApiIndexView.as_view(), name="api_docs"),
    url(r'^login/$', APILoginView.as_view(), name='api_login'),
    url(r'^register/$', APIRegisterView.as_view(), name='api_register'),
    url(r'^logout/$', APILogoutView.as_view(), name='api_logout'),
    url(r'^batch_upload/$', BatchSampleUploadView.as_view(), name='batch_upload'),
    url(r'^surveys/$', SurveyListView.as_view(), name='surveys'),
    url(r'^submit_survey/$', SurveyResponseUploadView.as_view(), name='submit_survey'),
)
