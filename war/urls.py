from django.urls import path
    
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("home/", views.home, name="home"),
    path('logout/', views.logout_user, name='logout'),
    path('krs_war/<slug>', views.krs_war, name='krs_war'),
    path('admin_control/', views.admin_control, name='admin_control'),
]