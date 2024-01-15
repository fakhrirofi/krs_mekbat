from django.db import models
from django.contrib.auth.models import User

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Session(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=20)
    active = models.BooleanField(default=True)
    open_time = models.DateTimeField()

    def __str__(self):
        return self.name

class Schedule(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    max_enrolled = models.IntegerField(default=7)
    available = models.IntegerField(default=7)

    def __str__(self):
        return self.name

    def add_person(self, userdata, changed):
        if self.userdata_set.count() >= self.max_enrolled:
            logger.warning(f"{userdata.name} Schedule Count >= max_enrolled. target={self.name}")
            return "limit"
        if changed:
            sch = userdata.schedule
            sch.available += 1
            sch.save()
            logger.warning(f"{userdata.name} Changed. from={sch.name} target={self.name}")
        userdata.schedule = self
        userdata.save()
        self.available = self.max_enrolled - self.userdata_set.count()
        self.save()
        return "success"

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    nim = models.IntegerField()
    name = models.CharField(max_length=50)
    handphone = models.CharField(max_length=15)

    def __str__(self):
        return str(self.user.username)

class AdminControl(models.Model):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=False)
    



