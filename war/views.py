from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Session, Schedule, AdminControl
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
            nim = form.cleaned_data['nim']
            if User.objects.filter(username=nim):
                messages.info(request, "NIM telah didaftarkan, hubungi asisten Laboratorium jika ingin mengganti password!")
            else:
                user = form.save()
                return redirect("login")
    form = RegistrationForm()
    return render(request=request, template_name="war/register.html",
            context={"form":form})

@login_required
def krs_war(request, slug):
    return render(request, 'war/krs_war.html')

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
                if command == "empty_schedule":
                    for ses in session:
                        _ses = Session.objects.get(name=ses)
                        for sch in _ses.schedule_set.all():
                            sch.userdata_set.clear()
                            sch.available = sch.max_enrolled - sch.userdata_set.count()
                            sch.save()
                messages.info(request, f"{command} success")
            except Exception as ex:
                messages.info(request, ex)

    return render(request, 'war/admin_control.html', {
        "controller" : AdminControl.objects.all(),
        "session" : Session.objects.all()
    })