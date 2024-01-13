from django.contrib import admin

from .models import Session, Schedule, UserData

admin.site.register((Session, Schedule, UserData))
