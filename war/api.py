from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Session, Schedule
import json

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def krs_war(request, slug):
    if request.method == "GET":
        session = get_object_or_404(Session, slug=slug)
        schedule = list()
        for sch in session.schedule_set.all():
            schedule.append({
                "pk"    : sch.pk,
                "name"  : sch.name,
                "max_enrolled"  : sch.max_enrolled,
                "available" : sch.available,
            })
        
        selected_pk = -1
        schedule_name = None
        if request.user.userdata.schedule:
            selected_pk = request.user.userdata.schedule.pk
            schedule_name = request.user.userdata.schedule.name

        return JsonResponse({
            "selected_pk" : selected_pk,
            "schedule_name" : schedule_name,
            "schedule" : schedule,
        })

    if request.method == "POST":
        user = request.user
        pk = int(json.load(request)['pk']) #Get data from POST request
        if pk == -1:
            userdata = user.userdata
            sch = userdata.schedule
            if sch:
                logger.warning(f"{userdata.name} blank. from={sch.name}")
                sch.available += 1
                sch.save()
            userdata.schedule = None
            userdata.save()
            status = "success"
            message = "Berhasil menghapus Sesi Praktikum"
        else:
            changed = False
            if user.userdata.schedule:
                changed = True
            if pk != -1:
                schedule = Schedule.objects.get(pk=pk)
                logger.info(f"{user.userdata.name} checked target={schedule.name}")
                status = schedule.add_person(user.userdata, changed)
                if status == "limit":
                    message = "Sesi yang anda pilih telah penuh, silakan pilih sesi lainnya!"
                else:
                    message = f"Berhasil memilih jadwal praktikum Sesi {schedule.name}"

        if user.userdata.schedule:
            info_selected = user.userdata.schedule.name
        else:
            info_selected = None

        #If sending data back to the view, create the data dictionary
        data = {
            'status':status,
            'message':message,
            'info_selected':info_selected
        }
        return JsonResponse(data)