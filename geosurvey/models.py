from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class GeographicalSample(models.Model):
    """ Represents a single geographical point sample in a survey, retrieved
    from a GPS device such as a navigator or smartphone.

    """
    location = models.PointField()
    timestamp = models.DateTimeField()
    speed = models.FloatField(null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(180.0)])
    heading = models.FloatField(null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)])
    location_accuracy = models.FloatField()
    heading_accuracy = models.FloatField(null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)])
    leg = models.ForeignKey('Leg', null=True, blank=True)
    participant = models.ForeignKey(User)
    objects = models.GeoManager()
    
    class Meta:
        unique_together = (('timestamp', 'participant'),)

    def __unicode__(self):
        return "Point({0}, {1}) at {2}".format(
            self.location.y, self.location.x, self.timestamp)

    def clean_heading(self):
        if not self.heading_accuracy:
            raise ValidationError('If you have a heading, you must have an ' +
                'accuracy in degrees error for that heading.')

    def clean(self):
        if self.heading:
            self.clean_heading()
        super(GeographicalSample, self).clean()


class Leg(models.Model):
    """ Represents a collection of samples that make up a single leg in a single
    
    """
    TRANSPORT_CHOICES = (
        ('C', 'Private Vehicle'),
        ('P', 'Walking'),
        ('Cy', 'Cycling'),
        ('PT', 'Public Transport'),
        ('T', 'Taxi')
    )
    
    timestamp = models.DateTimeField()
    duration = models.FloatField(validators=[MinValueValidator(0.01)])
    path = models.LineStringField()
    transport = models.CharField(max_length=2, choices=TRANSPORT_CHOICES)
    participant = models.ForeignKey(User)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "{0} leg starting at {1} with a {0} minute duration".format(
            self.get_transport_display(), self.timestamp, self.duration
        )

# Model tests
from django.test import TestCase
from django.contrib.gis.geos import Point, LineString
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.timezone import utc

class GeoSurveyModelTests(TestCase):
    def setUp(self):
        self.participant = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword'
        )
        
        
    def test_duplicate_samples(self):
        """Can't have a sample for the same user at the same timestamp."""
        sample1 = GeographicalSample.objects.create(
            location = Point(30.236045, 51.261926, srid=4326),
            timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
            location_accuracy = 35.5,
            participant = self.participant
        )
        with self.assertRaises(IntegrityError):
            sample2 = GeographicalSample.objects.create(
                location = Point(30.236045, 51.261926, srid=4326),
                timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
                location_accuracy = 35.5,
                participant = self.participant
            )
    
    def test_heading_accuracy_constraint(self):
        """If you have a heading value, you must also have an accuracy value."""
        sample = sample = GeographicalSample.objects.create(
            location = Point(30.236045, 51.261926, srid=4326),
            timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
            location_accuracy = 35.5,
            heading = 95.3,
            participant = self.participant
        )
        with self.assertRaises(ValidationError):
            sample.clean()
        
        # Shouldn't raise the validation error if we're ok.
        sample2 = sample = GeographicalSample.objects.create(
            location = Point(30.236045, 51.261926, srid=4326),
            timestamp = datetime(2012, 2, 25, 9, 15).replace(tzinfo=utc),
            location_accuracy = 35.5,
            heading = 95.3,
            heading_accuracy = 15.5,
            participant = self.participant
        )
        try:
            sample2.clean()
        except ValidationError:
            self.fail()
    
    
        
        
