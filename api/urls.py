from django.conf.urls import patterns, url
from api.views import *

urlpatterns = patterns('',
    
    url(r'^$', ApiIndexView.as_view(), name="api_docs"),
    url(r'^login/$', APILoginView.as_view(), name='api_login'),
    url(r'^batch_upload/$', BatchSampleUploadView.as_view(), name='batch_upload'),
    url(r'^surveys/$', SurveyListView.as_view(), name='surveys')
)
