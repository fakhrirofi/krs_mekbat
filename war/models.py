from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    max_enrolled = models.IntegerField(default=7)

    def __str__(self):
        return self.name

    def add_person(self, person):
        if self.userdata_set.count() >= self.max_enrolled:
            raise Exception("The session you selected is Full")
        person.schedule = self
        person.save()

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    nim = models.IntegerField()
    name = models.CharField(max_length=50)
    handphone = models.CharField(max_length=15)

    def __str__(self):
        return str(self.user.username)




