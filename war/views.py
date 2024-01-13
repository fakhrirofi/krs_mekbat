from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

class CustomLoginView(LoginView):
	template_name = 'war/login.html'
	redirect_authenticated_user = True

@login_required
def home(request):
    return render(request=request, template_name="war/home.html")

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
