from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from . import choices


class User(AbstractUser):
    pass

class Image(models.Model):
    image = models.ImageField()
    
class Event(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    time = models.TimeField()
    department = models.CharField(
        max_length=6, choices=choices.DEPARTMENT, default="COMPS"
    )
    expert_name = models.CharField(max_length=256)
    description = models.TextField()
    organizer = models.CharField(max_length=256)
    photograph = models.ForeignKey(Image, on_delete=models.CASCADE)
