from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

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
    trip = models.ForeignKey('Trip')
    participant = models.ForeignKey(User)
    objects = models.GeoManager()
    
    class Meta:
#        unique_together = (('timestamp', 'participant', 'location'),)
        get_latest_by = 'timestamp'

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

    def speed_in_kilometres_per_hour(self):
        return self.speed * 3.6

class Transport(models.Model):
    """ Model representing a mode of transport applicable to a trip. Each trip can
        have multiple modes of transport, so this is a many-to-many relationship.
    """
    TRANSPORT_CHOICES = (
        ('C', 'Private Vehicle'),
        ('P', 'Walking'),
        ('Cy', 'Cycling'),
        ('PT', 'Public Transport'),
        ('T', 'Taxi')
    )
    mode = models.CharField(max_length=2, choices=TRANSPORT_CHOICES)
    
    def __unicode__(self):
        return self.get_mode_display()


class Trip(models.Model):
    """ Represents a collection of samples that make up a single leg in a single
    
    """
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.CharField(max_length=100)
    duration = models.FloatField(validators=[MinValueValidator(0.01)])
    path = models.LineStringField(null=True,blank=True)
    distance = models.FloatField(null=True, blank=True)
    transport_modes = models.ManyToManyField('Transport')
    participant = models.ForeignKey(User)
    survey = models.ForeignKey('Survey')
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "Leg starting at {1} with a {0} minute duration".format(
                self.timestamp, self.duration)
                
    class Meta:
        get_latest_by = 'timestamp'
        permissions = (
            ('view_trip', "Can view the trip"),
        )

    def distance_in_km(self):
        return self.distance / 1000.0

    def formatted_duration(self):
        dur = (self.end_time - self.start_time).total_seconds()
        hours = int(dur) / 60 / 60
        mins = int(dur - (hours * 60 * 60)) / 60
        seconds = int(dur - (hours * 60 * 60) - (mins * 60))
        return "{0}h {1}m {2}s".format(hours, mins, seconds)
        
class Survey(models.Model):
    """ Represents a geographical survey, with a defined 
    
    """
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=144)
    managed_by = models.ForeignKey(User)

    class Admin:
        list_display = ('',)
        search_fields = ('',)
    
    class Meta:
        permissions = (
            ("view_survey", "Can see this survey"),
            ("cancel_survey", "Can deactivate this survey"),
        )


    def __unicode__(self):
        return u"{0}. Managed by {1} {2}.".format(self.title, 
                self.managed_by.first_name, self.managed_by.last_name)
                
class Researchers(Group):
    """ Holds the permis
    
    """
    pass

class SurveyResponse(models.Model):
    """
    Represents a response to a multiple choice survey question.
    """

    question = models.CharField(max_length=144)
    response = models.CharField(max_length=144)
    question_group = models.CharField(max_length=40)
    participant = models.ForeignKey(User)
    answered_on = models.DateTimeField(default=datetime.now())



# Model tests
from django.test import TestCase
from django.contrib.gis.geos import Point
from django.db import IntegrityError
from django.utils.timezone import utc

class GeoSurveyModelTests(TestCase):
    fixtures = ['initial_data.json']
    
    def setUp(self):
        self.participant = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword'
        )
        self.survey = Survey.objects.latest('end_date')
        self.trip = Trip.objects.create(
            date=datetime.today().date(),
            description="Test trip",
            duration=31.5,
            participant=self.participant,
            survey=self.survey
        )
        
        
    def test_duplicate_samples(self):
        """Can't have a sample for the same user at the same timestamp."""
        sample1 = GeographicalSample.objects.create(
            location = Point(30.236045, 51.261926, srid=4326),
            timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
            location_accuracy = 35.5,
            participant = self.participant,
            trip = self.trip
        )
        with self.assertRaises(IntegrityError):
            sample2 = GeographicalSample.objects.create(
                location = Point(30.236045, 51.261926, srid=4326),
                timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
                location_accuracy = 35.5,
                participant = self.participant,
                trip = self.trip
            )
    
    def test_heading_accuracy_constraint(self):
        """If you have a heading value, you must also have an accuracy value."""
        sample = sample = GeographicalSample.objects.create(
            location = Point(30.236045, 51.261926, srid=4326),
            timestamp = datetime(2012, 2, 25, 9, 0).replace(tzinfo=utc),
            location_accuracy = 35.5,
            heading = 95.3,
            participant = self.participant,
            trip=self.trip
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
            participant = self.participant,
            trip = self.trip
        )
        try:
            sample2.clean()
        except ValidationError:
            self.fail()
    
    
        
        
