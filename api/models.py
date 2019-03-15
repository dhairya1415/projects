from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from . import choices


class User(AbstractUser):
    pass

#department
# Amogh's part


class Event(models.Model):
    name = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    department = models.CharField(
        max_length=6, choices=choices.DEPARTMENT, default="COMPS"
    )
    expert_name = models.CharField(max_length=256)
    description = models.TextField()
    organizer = models.TextField()


class Report(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    venue = models.CharField(max_length=256)
    number_of_participation = models.IntegerField()
    # image_1 = models.ImageField()
    # image_2 = models.ImageField()
    # image_3 = models.ImageField()
    attendance = models.FileField()


class Image(models.Model):
    image = models.ImageField()
    report = models.ForeignKey(Report, related_name="image", on_delete=models.CASCADE)


#

# Connect model Event to Model User one event many users#
