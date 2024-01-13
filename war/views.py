from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Session, UserData, Schedule
from django.contrib import messages

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
                status = schedule.add_person(user.userdata, changed)
                if status == "limit":
                    messages.info(request, "Sesi yang anda pilih telah penuh, silakan pilih sesi lainnya!")
    return render(request, 'war/krs_war.html', {
        "schedule": session.schedule_set.all(),
        "session": session,
    })