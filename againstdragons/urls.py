from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from dashboard.views import RegistrationView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'againstdragons.views.home', name='home'),
    # url(r'^againstdragons/', include('againstdragons.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^api/', include('api.urls')),
    url(r'^', include('dashboard.urls')),

    url(r'^accounts/register/$', RegistrationView.as_view(), name='register'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {
        'template_name': 'dashboard/participant_login.html',
    }, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),
)

# Development serving of static files
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )