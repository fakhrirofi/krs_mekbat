from django.contrib import admin
from .actions import export_as_xls
from ..models import Session, Schedule, UserData, AdminControl, Event, Presence, PresenceData

class ModelAdmin(admin.ModelAdmin):
    actions = [export_as_xls]


class SessionInline(admin.TabularInline):
    model = Schedule
    extra = 1

class SessionAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'schedule', 'open_time', 'registered', 'active']
    inlines = [SessionInline]

    def schedule(self, obj):
        return obj.schedule_set.count()

    def registered(self, obj):
        return sum(schedule.users_enrolled.count() for schedule in obj.schedule_set.all())

admin.site.register(Session, SessionAdmin)


class ScheduleInline(admin.TabularInline):
    model = UserData.schedules.through
    extra = 1

class ScheduleAdmin(ModelAdmin):
    list_display = ['name', 'group_number', 'max_enrolled', 'enrolled', 'available']
    ordering = ['session__pk', 'group_number']
    list_filter = ['session']
    inlines = [
        # ScheduleInline # M2M inline is tricky without through model displayed nicely
    ]

    def enrolled(self, obj):
        obj.available = obj.max_enrolled - obj.users_enrolled.count()
        obj.save()
        return obj.users_enrolled.count()

    def session(self, obj):
        return self.session.name

admin.site.register(Schedule, ScheduleAdmin)


class UserDataAdmin(ModelAdmin):
    list_display = ['show_schedules', 'nim', 'name', 'handphone']
    search_fields = ['name', 'nim']
    list_filter = ['schedules__session']
    ordering = ['nim']
    list_per_page = 400

    def show_schedules(self, obj):
        return ", ".join([str(s) for s in obj.schedules.all()])

    # def session(self, obj):
    #     if obj.schedule:
    #         return obj.schedule.session
    #     else:
    #         "-"

    # def group_number(self, obj):
    #     if obj.schedule:
    #         return obj.schedule.group_number
    #     else:
    #         return "-"

admin.site.register(UserData, UserDataAdmin)

class AdminControlAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']

admin.site.register(AdminControl, AdminControlAdmin)


###################
# PRESENCE MODELS #
###################

class EventInline(admin.TabularInline):
    model = Presence
    extra = 1

class EventAdmin(ModelAdmin):
    list_display = ['session', 'name', 'active', 'presence_count']
    list_filter = ['session']
    inlines = [EventInline]

    def presence_count(self, obj):
        return obj.presence_set.count()

admin.site.register(Event, EventAdmin)


class PresenceInline(admin.TabularInline):
    model = PresenceData
    extra = 1

class PresenceAdmin(ModelAdmin):
    list_display = ['event', 'name', 'user_count']
    list_filter = ['event__session', 'event']
    ordering = ['event__session__pk', 'event__pk', 'pk']
    inlines = [PresenceInline]

    def session(self, obj):
        return obj.event.session.name

    def user_count(self, obj):
        return obj.presencedata_set.count()

    def attended(self, obj):
        return obj.presencedata_set.filter(attendance=True).count()

admin.site.register(Presence, PresenceAdmin)


class PresenceDataAdmin(ModelAdmin):
    search_fields = ['name', 'nim']
    list_display = ['schedule', 'group_number', 'nim', 'name', 'attendance', 'datetime']
    list_filter = ['presence__event__session', 'presence__event']
    ordering = ['presence__pk', 'user__userdata__nim']
    list_per_page = 300

    def session(self, obj):
        return obj.presence.event.session.name

    def nim(self, obj):
        return obj.user.userdata.nim
    
    def event(self, obj):
        return obj.presence.event.name

    def schedule(self, obj):
        return obj.presence.name

    def group_number(self, obj):
        # Trying to find schedule matching the session of the presence
        session = obj.presence.event.session
        sch = obj.user.userdata.get_schedule_for_session(session)
        if sch:
            return sch.group_number
        else:
            return "-"
    
    def name(self, obj):
        return obj.user.userdata.name

admin.site.register(PresenceData, PresenceDataAdmin)

