from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Session, UserData, Schedule, AdminControl
from django.contrib import messages

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
	template_name = 'war/login.html'
	redirect_authenticated_user = True

@login_required
def home(request):
    session = Session.objects.filter(active=True)
    return render(request=request, template_name="war/home.html", context={"session":session})

@login_required
def logout_user(request):
    logout(request)
    return redirect("login")

def index(request):
    return redirect("login")

def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("index")
        else:
            HttpResponse("form invalid", 400)
    form = RegistrationForm()
    return render(request=request, template_name="war/register.html",
            context={"form":form})

@login_required
def krs_war(request, slug):
    user = request.user
    session = get_object_or_404(Session, slug=slug)
    if not session.active:
        return redirect('home')
    if request.method == "POST":
        pk = request.POST.getlist('pk')
        if len(pk) == 0:
            userdata = user.userdata
            sch = userdata.schedule
            if sch:
                logger.warning(f"{userdata.name} blank. from={sch.name}")
                sch.available += 1
                sch.save()
            userdata.schedule = None
            userdata.save()
        else:
            changed = False
            if user.userdata.schedule:
                pk.remove(str(user.userdata.schedule.pk))
                changed = True
            if len(pk):
                pk = int(pk[0])
                schedule = Schedule.objects.get(pk=pk)
                logger.info(f"{user.userdata.name} checked target={schedule.name}")
                status = schedule.add_person(user.userdata, changed)
                if status == "limit":
                    messages.info(request, "Sesi yang anda pilih telah penuh, silakan pilih sesi lainnya!")
    return render(request, 'war/krs_war.html', {
        "schedule": session.schedule_set.all(),
        "session": session,
    })

@login_required
def admin_control(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == "POST":
        commands = request.POST.getlist('command')
        session = request.POST.getlist('session')
        print(commands)
        for command in commands:
            try:
                if command == "regenerate_schedule":
                    for ses in session:
                        _ses = Session.objects.get(name=ses)
                        for sch in _ses.schedule_set.all():
                            sch.delete()
                        for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]:
                            for time in ["7.00 - 9.00", "10.00 - 12.00", "13.00 - 15.00"]:
                                for section in ["A", "B"]:
                                    sch = Schedule(session=_ses, name=f"{day} {time} | {section}")
                                    sch.save()
                messages.info(request, f"{command} success")
            except Exception as ex:
                messages.info(request, ex)

    return render(request, 'war/admin_control.html', {
        "controller" : AdminControl.objects.all(),
        "session" : Session.objects.all()
    })