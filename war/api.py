from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Session, Schedule
from django.utils import timezone
import json
from django.urls import reverse

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def krs_war(request, slug):
    session = get_object_or_404(Session, slug=slug)
    if (not session.active) or (timezone.now() < session.open_time):
        return redirect(reverse('war:home'))
    if request.method == "GET":
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
        
        # Get schedule for THIS session
        user_sch = request.user.userdata.get_schedule_for_session(session)
        if user_sch:
            selected_pk = user_sch.pk
            schedule_name = user_sch.name

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
            # Determine which schedule to remove based on SESSION logic
            sch = userdata.get_schedule_for_session(session)
            if sch:
                logger.warning(f"{userdata.name} blank. from={sch.name}")
                sch.available += 1
                sch.save()
                userdata.schedules.remove(sch)
            
            userdata.save()
            status = "success"
            message = "Berhasil menghapus Sesi Praktikum"
        else:
            changed = False
            if user.userdata.get_schedule_for_session(session):
                changed = True
            if pk != -1:
                schedule = Schedule.objects.get(pk=pk)
                logger.info(f"{user.userdata.name} checked target={schedule.name}")
                status = schedule.add_person(user.userdata, changed)
                if status == "limit":
                    message = "Sesi yang anda pilih telah penuh, silakan pilih sesi lainnya!"
                else:
                    message = f"Berhasil memilih jadwal praktikum Sesi {schedule.name}"

        info_sch = user.userdata.get_schedule_for_session(session)
        if info_sch:
            info_selected = info_sch.name
        else:
            info_selected = None

        #If sending data back to the view, create the data dictionary
        data = {
            'status':status,
            'message':message,
            'info_selected':info_selected
        }
        return JsonResponse(data)