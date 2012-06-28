from django.test import TestCase
from django.test.client import Client

def load_payload_file(filename):
    return open(filename, 'r').read()
    

class BatchUploadTest(TestCase):
    fixtures = ['initial_data.json']
    
    def setUp(self):
        self.client = Client()
        self.client.login(username='test', password='testpassword')
        
    
    def test_single_trip_upload(self):
        """ Test a batch upload for samples for a single trip with valid data.
        """
        import sys, os.path
        
        dir = sys.path[0]
        filepath = os.path.join(dir, 'api/payloads/valid_request_payload.json')
        
        response = self.client.post('/api/batch_upload/', 
                load_payload_file(filepath),
                content_type="text/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success', status_code=302)
