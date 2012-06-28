from django.conf.urls import patterns, url
from api.views import *

urlpatterns = patterns('',
    
    url(r'^$', ApiIndexView.as_view(), name="api_docs"),
    url(r'^batch_upload/$', BatchSampleUploadView.as_view(), name='batch_upload'),
)
