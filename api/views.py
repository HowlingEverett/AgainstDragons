# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.views.generic.base import View
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from datetime import datetime, date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt

from django.contrib.gis.geos import Point

from geosurvey.models import *


class BaseAPIResponseMixin(object):
    pass


class JSONAPIResponseMixin(BaseAPIResponseMixin):
    def error_response(self, request_errors, field_errors=None):
        """ Returns a JSON-formatted error response with a 402 Bad Request
            response code. 
            
            error_response(['error description', ...],
            {'field_name':'error description'})
                -> "{'request_errors': ['error1', 'error2', ...], 
                     'field_errors': {'field1':'error desc',
                     'field2': 'error_desc}}"
        """
        error_dict = {'request_errors': None}
        return HttpResponseBadRequest(json.dumps(error_dict),
                                      content_type="text/json")

    def success_response(self, success_dict):
        """ Returns a JSON-formattted success response with a 200 response code.
            
        """
        return HttpResponse(json.dumps(success_dict), content_type="text/json")


class APILoginView(JSONAPIResponseMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return self.success_response({'success': {'message': 'User logged in.', 'fields': {'username': username, 'email': user.email}}})
        else:
            return HttpResponse
            return self.error_response(
                    {'error': 'Incorrect username or password.'})


class APIRegisterView(JSONAPIResponseMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        existing = User.objects.filter(username__iexact=username)
        if len(existing) > 0:
            return self.error_response(
                    {'error': 'User with that username already exists.'})
        if len(password) == 0 or len(email) == 0:
            return self.error_response({
                'error': 'You must enter a valid password and email address.'})

        User.objects.create_user(username, email, password)
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)

        return self.success_response({'success': {'message': 'User created and logged in successfully', 'fields': {'username': username, 'email': email}}})


class BatchSampleUploadView(JSONAPIResponseMixin, View):
    """ Performs a batch create of GeographicalSamples for a single trip
    
    """

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """ Performs a bulk create of Geographical Samples based on the json 
            included in the POST body.
            
            Expects a JSON payload in the request body in the format:
            {'trips': [
                {'trip':{
                    'date': 'yyyy-MM-dd hh:mm:ss',
                    'duration': float,
                    'transport_modes': ['PT', 'P', ...],
                    'survey_id': int
                },
                'samples': [sample1, sample2, sample3, ...]
                }
            ]}
            And a sample format of
            {
                'timestamp': 'yyyy-MM-dd hh:mm:ss',
                'latitude': double,
                'longitude': double,
                '
            }
        """
        payload = json.loads(request.body)
        trips = payload.get('trips')
        if not trips:
            return self.error_response(['No trips included in request body.'])

        samples = []
        for trip_data in trips:
            trip_dict = trip_data.get('trip')
            samples_list = trip_data.get('samples')
            if not trip_dict:
                return self.error_response(
                    ['No trip description included in your trips.'])
            if not samples_list:
                return self.error_response([
                    'No samples included for trip {0}.'.format(
                        trip_dict['date'])])

            trip = self._create_trip(trip_dict, request)
            samples += self._create_samples(samples_list, trip, request)

        GeographicalSample.objects.bulk_create(samples)

        return self.success_response(
                {'success': 'Trips successfully uploaded to survey.'})

    def _create_trip(self, trip_dict, request):
        trip = Trip(
            date=datetime.strptime(trip_dict['date'], '%Y-%m-%d').date(),
            duration=float(trip_dict['duration']),
            description=trip_dict['description'],
            participant=request.user,
            survey=Survey.objects.get(pk=trip_dict['survey_id'])
        )
        trip.save()
        for mode in trip_dict['transport_modes']:
            trip.transport_modes.create(
                mode=mode
            )
        return trip

    def _create_samples(self, samples_list, trip, request):
        samples = []
        for sample in samples_list:
            geosample = GeographicalSample(
                location=Point(float(sample['longitude']),
                               float(sample['latitude']), srid=4326),
                timestamp=datetime.strptime(sample['timestamp'],
                                            '%Y-%m-%d %H:%M:%S'),
                speed=sample.get('speed', None),
                heading=sample.get('heading', None),
                location_accuracy=sample.get('location_accuracy', None),
                heading_accuracy=sample.get('heading_accuracy', None),
                trip=trip,
                participant=request.user
            )
            samples.append(geosample)

        # Set trip's path and duration based on newly created samples
        if len(samples) > 0:
            first_timestamp = samples[0].timestamp
            last_timestamp = samples[-1].timestamp
            duration = last_timestamp - first_timestamp
            trip.duration = duration.total_seconds() / 60
        else:
            trip.duration = 0.0

        linepoints = [s.location for s in samples]
        trip.path = LineString(linepoints)
        trip.distance = trip.path.length
        trip.save()

        return samples


class ApiIndexView(TemplateView):
    template_name = 'api/index.html'


class SurveyListView(View):
    @method_decorator(require_GET)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        surveys = Survey.objects.filter(
            end_date__gte=datetime.today()).order_by('end_date')
        return HttpResponse(serializers.serialize('json', surveys),
                            content_type='text/json')

