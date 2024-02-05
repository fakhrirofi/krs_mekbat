from django.urls import path
    
from . import views, api, api_presence

app_name = 'war'
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("home/", views.home, name="home"),
    path('logout/', views.logout_user, name='logout'),
    path('krs_war/<slug>', views.krs_war, name='krs_war'),
    path('admin_control/', views.admin_control, name='admin_control'),
    path('show_qr/', views.show_qr, name="show_qr"),

    path('api/krs_war/<slug>', api.krs_war, name='api_krs_war'),
    path('api/presence/<api_type>', api_presence.api_handler, name="api_presence")
]