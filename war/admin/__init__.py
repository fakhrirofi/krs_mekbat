from django.contrib import admin
from .actions import export_as_xls
from ..models import Session, Schedule, UserData

class ModelAdmin(admin.ModelAdmin):
    actions = [export_as_xls]


class SessionInline(admin.TabularInline):
    model = Schedule
    extra = 1

class SessionAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'total', 'active']
    inlines = [SessionInline]

    def total(self, obj):
        return obj.schedule_set.count()

admin.site.register(Session, SessionAdmin)


class ScheduleInline(admin.TabularInline):
    model = UserData
    extra = 1

class ScheduleAdmin(ModelAdmin):
    list_display = ['session', 'name', 'max_enrolled', 'enrolled', 'available']
    ordering = ['pk']
    list_filter = ['session']
    inlines = [ScheduleInline]

    def enrolled(self, obj):
        obj.available = obj.max_enrolled - obj.userdata_set.count()
        obj.save()
        return obj.userdata_set.count()

    def session(self, obj):
        return self.session.name

admin.site.register(Schedule, ScheduleAdmin)


class UserDataAdmin(ModelAdmin):
    list_display_links = ['nim']
    list_display = ['schedule', 'nim', 'name', 'handphone']
    search_fields = ['name', 'nim']
    list_filter = ['schedule']
    ordering = ['schedule']

    def schedule(self, obj):
        if obj.schedule:
            return obj.schedule.name
        else:
            return "-"

admin.site.register(UserData, UserDataAdmin)
