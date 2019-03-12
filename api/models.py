from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from . import choices

# Create your models here.


class User(AbstractUser):
    pass


class Event(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=128)
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    time = models.TimeField()
    department = models.CharField(
        max_length=6, choices=choices.DEPARTMENT, default="COMPS"
    )
    expert_name = models.CharField()
    description = models.TextField()
    organizer = models.CharField()
    photograph = models.ImageField()
