"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


<<<<<<< Local Changes
class BatchUploadTest(TestCase):
    fixtures = ['initial_data.json',]
    
    def test_single_trip_upload(self):
        """ Test a batch upload for samples for a single trip with valid data.
=======
class SimpleTest(TestCase):
    def test_basic_addition(self):
>>>>>>> External Changes
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
