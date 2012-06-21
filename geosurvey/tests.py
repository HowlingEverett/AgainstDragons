"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.

def load_payload_file(filename):
    return open(filename, 'r').read()
    
    

class BatchUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    
    def test_single_trip_upload(self):
        """ Test a batch upload for samples for a single trip with valid data.
        """
        try:
            payload = load_payload_file('fixtures/valid_request_payload.json')
        except IOError:
            self.fail("Couldn't load payload data for test request - is the path correct?")
        
        response = self.client.post('/batch_upload/', 
                load_payload_file('fixtures/valid_request_payload.json'),
                content_type="text/json")
        
        self.assertEqual(response.status_code, 200)
        