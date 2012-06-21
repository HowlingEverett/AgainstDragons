# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from datetime import datetime, date

from django.contrib.gis

from geosurvey.models import *



class BaseAPIResponseMixin(object):
    pass
    
class JSONAPIResponseMixin(BaseAPIResponseMixin):
    
    def error_response(self, request_errors, field_errors=None):
        """ Returns a JSON-formatted error response with a 402 Bad Request
            response code. 
            
            error_response(['error description', ...], {'field_name':'error description'})
                -> "{'request_errors': ['error1', 'error2', ...], 
                     'field_errors': {'field1':'error desc', 'field2': 'error_desc}}"
        """
        error_dict = {'request_errors':None}
        return HttpResponseBadRequest(json.dumps(error_dict), content_type="text/json")
        
    def success_response(self, success_dict):
        """ Returns a JSON-formattted success response with a 200 response code.
            
        """
        return HttpResponse(json.dumps(success_dict), content_type="text/json")
    
class BatchSampleUploadView(JSONAPIResponseMixin, View):
    """ Performs a batch create of GeographicalSamples for a single trip
    
    """
    
    @login_required
    @user_passes_test(lambda u: u.has_perm('geosurvey.create_geographical_sample'))
    def dispatch(request, *args, **kwargs):
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
                return self.error_response(['No trip description included in your trips.'])
            if not samples_list:
                return self.error_response(['No samples included for trip {0}.'.format(trip_dict['date'])])
            
            trip = self._create_trip(trip_dict)
            samples += self._create_samples(samples_list, trip)
        
        GeographicalSample.objects.bulk_create(samples)
        
        return self.success_response({'success': 'Trips successfully uploaded to survey.'})
        
    def _create_trip(self, trip_dict):
        trip = Trip(
            date=datetime.strptime(trip_dict['date'], '%Y-%m-%d').date(),
            duration=float(trip_dict['duration']),
            participant=request.user,
            survey=Survey.objects.get(pk=trip_dict['survey_id'])
        ).save()
        for mode in trip_dict['transport_modes']:
            trip.transport_modes.create(
                mode=mode
            )
        return trip
    
    def _create_samples(self, samples_list, trip):
        samples = []
        for sample in samples_list:
            geosample = GeographicalSample(
                location=Point(sample['longitude'], sample['latitude'], srid=4326),
                timestamp=datetime.strptime(sample['timestamp'], '%Y-%m-%d %H:%M:%S'),
                speed=sample.get('speed', None),
                heading=sample.get('heading', None),
                location_accuracy=sample.get('location_accuracy', None),
                heading_accuracy=sample.get('heading_accuracy', None),
                trip=trip,
                participant=request.user
            )
            samples.append(geosample)
        return samples
        
    
