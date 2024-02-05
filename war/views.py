from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Session, Schedule, AdminControl, Event, Presence, PresenceData
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .user_qr_code import encrypt, decrypt, get_event_ticket
import base64

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'war/login.html'
    redirect_authenticated_user = True
    extra_context = {"register_on" : AdminControl.objects.filter(name="register").first()}

@login_required
def home(request):
    session = Session.objects.filter(active=True, open_time__lt=timezone.now())
    return render(request, "war/home.html", {
        "session"       : session,
        })

@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse("blog:index"))

def index(request):
    return redirect(reverse("war:login"))

def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("war:home"))
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            nim = form.cleaned_data['nim']
            if User.objects.filter(username=nim):
                messages.info(request, "NIM telah didaftarkan, hubungi asisten Laboratorium jika ingin mengganti password!")
            else:
                user = form.save()
                return redirect(reverse("war:login"))
    form = RegistrationForm()
    return render(request=request, template_name="war/register.html",
            context={"form":form})

@login_required
def krs_war(request, slug):
    session = get_object_or_404(Session, slug=slug)
    if (not session.active) or (timezone.now() < session.open_time) :
        return redirect(reverse("war:home"))
    return render(request, 'war/krs_war.html')

@login_required
def show_qr(request):
    enc = encrypt(str(request.user.pk))
    print(enc)
    qr_code = get_event_ticket(enc, request.user.userdata)
    return render(request, 'war/show_qr.html', {
        'qr_code' : base64.b64encode(qr_code).decode(),
        'filename' : str(request.user.userdata.nim) + "_" + request.user.userdata.name
    })

@login_required
def admin_control(request):
    if not request.user.is_staff:
        return redirect(reverse("war:home"))
    if request.method == "POST":
        commands = request.POST.getlist('command')
        selection = request.POST.getlist('selection')
        for command in commands:
            try:
                if command == "regenerate_schedule":
                    for ses in selection:
                        _ses = Session.objects.get(name=ses)
                        for sch in _ses.schedule_set.all():
                            sch.delete()
                        group_number = 0
                        for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]:
                            if day == "Jumat":
                                times = ["7.00 - 9.00", "13.00 - 15.00", "15.30 - 17.30"]
                            else:
                                times = ["7.00 - 9.00", "10.00 - 12.00", "13.00 - 15.00"]
                            for time in times:
                                for _ in range(2):
                                    group_number += 1
                                    sch = Schedule(session=_ses, name=f"{day} {time}")
                                    sch.group_number = group_number
                                    sch.save()
                
                elif command == "empty_schedule":
                    for ses in selection:
                        _ses = Session.objects.get(name=ses)
                        for sch in _ses.schedule_set.all():
                            sch.userdata_set.clear()
                            sch.available = sch.max_enrolled - sch.userdata_set.count()
                            sch.save()
                
                elif command == "generate_presence":
                    for eve in selection:
                        event = Event.objects.get(name=eve)
                        _temp_sch_name = None
                        for sch in event.session.schedule_set.all():
                            if sch.name != _temp_sch_name:
                                presence = Presence(name=sch.name, event=event)
                                presence.save()
                                _temp_sch_name = sch.name
                            for userdata in sch.userdata_set.all():
                                presencedata = PresenceData(user=userdata.user, presence=presence)
                                presencedata.save()

                messages.info(request, f"{command} success")
            except Exception as ex:
                messages.info(request, ex)

    return render(request, 'war/admin_control.html', {
        "controller" : AdminControl.objects.all(),
        "session" : Session.objects.all(),
        "event"   : Event.objects.all()
    })