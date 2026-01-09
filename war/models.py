from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    available = models.IntegerField(default=0)
    max_enrolled = models.IntegerField(default=30)
    group_number = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def add_person(self, userdata, changed):
        if self.users_enrolled.count() >= self.max_enrolled:
            logger.warning(f"{userdata.name} Schedule Count >= max_enrolled. target={self.name}")
            return "limit"
        if changed:
            # Find and remove old schedule for this session
            sch = userdata.get_schedule_for_session(self.session)
            if sch:
                sch.available += 1
                sch.save()
                userdata.schedules.remove(sch)
                logger.warning(f"{userdata.name} Changed. from={sch.name} target={self.name}")
        
        userdata.schedules.add(self)
        userdata.save()
        self.available = self.max_enrolled - self.users_enrolled.count()
        self.save()
        return "success"

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    schedules = models.ManyToManyField(Schedule, blank=True, related_name='users_enrolled')
    # FUTURE SCHEDULE UPDATE: MANY TO MANY

    def get_schedule_for_session(self, session):
        return self.schedules.filter(session=session).first()

    # FUTURE SCHEDULE UPDATE: MANY TO MANY
    nim = models.IntegerField()
    name = models.CharField(max_length=50)
    handphone = models.CharField(max_length=15)

    def __str__(self):
        return str(self.user.username)

class AdminControl(models.Model):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

###################
# PRESENCE MODELS #
###################

class Event(models.Model):
    name = models.CharField(max_length=30)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Presence(models.Model):
    # auto generate in admin control
    name = models.CharField(max_length=30)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class PresenceData(models.Model):
    # auto generate in admin control. (display original presence)
    presence = models.ForeignKey(Presence, on_delete=models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    attendance = models.BooleanField(default=False)
    datetime = models.DateTimeField("attendance time", blank=True, null=True)

    def __str__(self):
        return self.presence.event.name + " | " + self.presence.name + " | " + str(self.user.username)


def attend(presence_id: int, user_id: int):
    presence = Presence.objects.filter(pk=presence_id).first()
    user = User.objects.filter(pk=user_id).first()
    if (not presence) or (not user):
        return {"message" : "not_found"}
    # check whether user pk already created for selected presence (generated in admin control)
    obj = PresenceData.objects.filter(presence=presence, user=user).first()
    message = str()
    if not obj: # for those who cant attend on their presence (inhale)
        obj = PresenceData(user=user, presence=presence, attendance=True, datetime=timezone.now())
        obj.save()
        message = "different_presence"
    elif obj.attendance == True:
        message =  "already_scanned"
    else:
        obj.attendance = True
        obj.datetime = timezone.now()
        obj.save()
        message = "success"
    
    return {
        "message"    : message,
        "name"      : user.userdata.name,
        "nim"       : user.userdata.nim,
    }

def get_events():
    data = list()
    for event in Event.objects.filter(active=True).all():
        data.append({
            "event_id"  : event.pk,
            "session"   : event.session.name,
            "name"      : event.name,
        })
    return data

def get_presences(event_id: int):
    event = Event.objects.filter(pk=event_id).first()
    if not event:
        return [{
            "presence_id"   : 0,
            "name"          : "event_id not found"
        }]
    data = list()
    for presence in event.presence_set.all():
        data.append({
            "presence_id"   : presence.pk,
            "name"          : presence.name
        })
    return data