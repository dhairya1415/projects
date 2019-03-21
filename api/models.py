from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from . import choices


class User(AbstractUser):
    department = models.CharField(
        max_length=6, choices=choices.DEPARTMENT, default="COMPS"
    )


# department
# Amogh's part


class Event(models.Model):
    name = models.CharField(max_length=128)
    start = models.DateTimeField()
    end = models.DateTimeField()
    allDay = models.BooleanField(default=False)
    department = models.CharField(
        max_length=6, choices=choices.DEPARTMENT, default="COMPS"
    )
    expert_name = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    organizer = models.TextField(null=True, blank=True)


class Report(models.Model):
    event = models.OneToOneField(Event, related_name = 'events',on_delete=models.CASCADE)
    venue = models.CharField(max_length=256)
    number_of_participation = models.IntegerField()
    attendance = models.FileField()


class Image(models.Model):
    image = models.ImageField()
    report = models.ForeignKey(Report, related_name="image", on_delete=models.CASCADE)

#

# Connect model Event to Model User one event many users#
# The Report part will take place in 3 steps
# 1. User will enter all the fields of the report model and click submit
# 2. User will then upload the images where the report model just created will be referenced from the frontend
# 3. User will get the option to send the email of the report
