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
from django.utils.text import slugify
from django.http import HttpResponse, JsonResponse
import openpyxl
from .models import Session, Schedule, AdminControl, Event, Presence, PresenceData, UserData

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'war/login.html'
    redirect_authenticated_user = True
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_on'] = AdminControl.objects.filter(name="register").first()
        return context

@login_required
def home(request):
    session = Session.objects.filter(active=True, open_time__lt=timezone.now())
    return render(request, "war/home.html", {
        "session"       : session,
        })

@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse("war:login"))

def index(request):
    return redirect(reverse("war:login"))

def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("war:home"))
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user) # Auto login after register
                return redirect(reverse("war:home"))
            except Exception as e:
                messages.error(request, f"Gagal mendaftar: {e}")
        else:
                messages.error(request, "Gagal mendaftar. Periksa input anda.")
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
                if command == "accept_schedule":
                    slug = request.POST.get('target_session_slug')
                    # New inputs from 3-column preview
                    days = request.POST.getlist('days')
                    times = request.POST.getlist('final_times')
                    quotas = request.POST.getlist('quotas')
                    
                    if not slug or not days or not times:
                        messages.error(request, "Error: Missing session or schedule data.")
                    else:
                        _ses = Session.objects.get(slug=slug)
                        # Clear existing
                        _ses.schedule_set.all().delete()
                        
                        group_number = 0
                        # Iterate through the parallel lists
                        for i in range(len(days)):
                            day = days[i]
                            time = times[i]
                            quota = int(quotas[i]) if i < len(quotas) and quotas[i] else 30
                            
                            sch_name = f"{day} {time}"
                            
                            if sch_name.strip():
                                # Removed duplication loop
                                group_number += 1
                                sch = Schedule(session=_ses, name=sch_name)
                                sch.group_number = group_number
                                sch.max_enrolled = quota
                                sch.available = quota # Initially available = max
                                sch.save()
                        messages.success(request, f"Schedule for {_ses.name} updated successfully with custom quotas.")
                
                elif command.startswith("empty_schedule:"):
                    session_id = command.split(":")[1]
                    _ses = Session.objects.get(pk=int(session_id))
                    for sch in _ses.schedule_set.all():
                        sch.users_enrolled.clear()
                        sch.available = sch.max_enrolled
                        sch.save()
                    messages.success(request, f"Schedule emptied for {_ses.name}.")

                elif command.startswith("admin_remove_schedule:"):
                    parts = command.split(":")
                    if len(parts) >= 3:
                        user_id = parts[1]
                        sch_id = parts[2]
                        try:
                            ud = UserData.objects.get(pk=user_id)
                            sch = Schedule.objects.get(pk=sch_id)
                            if sch in ud.schedules.all():
                                ud.schedules.remove(sch)
                                sch.available += 1
                                sch.save()
                                msg = f"Removed {sch.name} for {ud.name}."
                                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                                    return JsonResponse({'status': 'success', 'message': msg})
                                messages.success(request, msg)
                            else:
                                msg = "Student not enrolled in that schedule."
                                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                                    return JsonResponse({'status': 'error', 'message': msg})
                                messages.info(request, msg)
                        except Exception as e:
                            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                                return JsonResponse({'status': 'error', 'message': str(e)})
                            messages.error(request, f"Error removing schedule: {e}")
                
                elif command == "create_session":
                    name = request.POST.get('session_name')
                    open_time = request.POST.get('session_open_time')
                    if name and open_time:
                        slug = slugify(name)
                        Session.objects.create(name=name, slug=slug, open_time=open_time)
                        messages.success(request, f"Session {name} created.")
                    else:
                        messages.error(request, "Name and Open Time required.")

                elif command.startswith("delete_session:"):
                    session_id = command.split(":")[1]
                    Session.objects.filter(pk=int(session_id)).delete()
                    messages.success(request, "Session deleted.")

                elif command.startswith("update_session:"):
                    session_id = command.split(":")[1]
                    open_time = request.POST.get(f'update_time_{session_id}')
                    if open_time:
                        _ses = Session.objects.get(pk=int(session_id))
                        _ses.open_time = open_time
                        _ses.save()
                        messages.success(request, f"Time updated for {_ses.name}.")

                elif command.startswith("toggle_control:"):
                    control_name = command.split(":")[1]
                    ctrl = AdminControl.objects.filter(name=control_name).first()
                    if ctrl:
                        ctrl.active = not ctrl.active
                        ctrl.save()

                elif command.startswith("toggle_session:"):
                    session_slug = command.split(":")[1]
                    ses = Session.objects.filter(slug=session_slug).first()
                    if ses:
                        ses.active = not ses.active
                        ses.save()

                elif command.startswith("download_session_data:"):
                    session_id = command.split(":")[1]
                    _ses = Session.objects.get(pk=int(session_id))
                    
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="{_ses.slug}_students.xlsx"'
                    
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "Students"
                    
                    # Header
                    ws.append(['Name', 'NIM', 'Phone', 'Schedule', 'Group'])
                    
                    # Data
                    for sch in _ses.schedule_set.all():
                        for ud in sch.users_enrolled.all():
                            ws.append([ud.name, ud.nim, ud.handphone, sch.name, sch.group_number])
                            
                    wb.save(response)
                    return response
                


                
                elif command.startswith("admin_reset_password:"):
                    user_id = command.split(":")[1]
                    new_pass = request.POST.get(f"new_password_{user_id}")
                    if new_pass:
                        u = User.objects.get(pk=user_id)
                        u.set_password(new_pass)
                        u.save()
                        msg = f"Password for {u.username} reset successfully."
                        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                             return JsonResponse({'status': 'success', 'message': msg})
                        messages.success(request, msg)
                    else:
                        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                             return JsonResponse({'status': 'error', 'message': "Password cannot be empty."})
                        messages.error(request, "Password cannot be empty.")

                elif command.startswith("admin_change_schedule:"):
                    userdata_id = command.split(":")[1]
                    new_sch_id = request.POST.get(f"new_schedule_id_{userdata_id}")
                    
                    ud = UserData.objects.get(pk=userdata_id)

                    if new_sch_id == "none":
                        # Ambiguous in M2M context from this view (which session?). 
                        # To be safe, we might skip or require session context.
                        # For now, disabling "remove from global view" or inferring if we can.
                        # We will just show an info message that this is clearer in the Session Data tab (Phase 2).
                        # Or iteration: check which session this dropdown belonged to?
                        # The dropdown in HTML has optgroups by Session.
                        # But the "none" value is generic.
                        messages.warning(request, "Please use the 'Session Data' tab to unset a schedule for a specific session.")
                    else:
                        target_sch = Schedule.objects.get(pk=int(new_sch_id))
                        
                        # Check quota
                        if target_sch.available <= 0:
                            messages.error(request, f"Schedule {target_sch.name} is FULL.")
                        else:
                            # 1. Identify Session
                            session = target_sch.session
                            
                            # 2. Find old schedule in this session
                            old_sch = ud.get_schedule_for_session(session)
                            
                            if old_sch:
                                old_sch.available += 1
                                old_sch.save()
                                ud.schedules.remove(old_sch)
                            
                            # 3. Occupy new spot
                            target_sch.available -= 1
                            target_sch.save()
                            
                            ud.schedules.add(target_sch)
                            ud.save()
                            msg = f"Schedule for {ud.name} changed to {target_sch.name}."
                            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                                current_schedules = []
                                for s in ud.schedules.all():
                                    current_schedules.append({
                                        'id': s.id,
                                        'name': s.name,
                                        'session_name': s.session.name
                                    })
                                return JsonResponse({
                                    'status': 'success', 
                                    'message': msg,
                                    'current_schedules': current_schedules
                                })
                            messages.success(request, msg)

                elif command.startswith("create_session"):
                    # ... [Existing code] ... (Wait, I replaced create_session block? No, I need to INSERT before the matching block or APPEND to list)
                    # I will insert new commands before the "messages.info" fallback.
                    pass

                elif command == "get_session_data":
                    session_id = request.POST.get('session_id')
                    try:
                        _ses = Session.objects.get(pk=session_id)
                        schedules = []
                        for sch in _ses.schedule_set.all().order_by('group_number'):
                            students = []
                            for u in sch.users_enrolled.all():
                                students.append({
                                    'id': u.pk,
                                    'name': u.name,
                                    'nim': u.nim
                                })
                            schedules.append({
                                'id': sch.pk,
                                'name': sch.name,
                                'quota': sch.max_enrolled,
                                'available': sch.available,
                                'group': sch.group_number,
                                'students': students
                            })
                        return JsonResponse({'status': 'success', 'schedules': schedules})
                    except Session.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': "Session not found"})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': str(e)})

                elif command == "update_schedule_meta":
                    sch_id = request.POST.get('schedule_id')
                    name = request.POST.get('name')
                    quota = request.POST.get('quota')
                    try:
                        sch = Schedule.objects.get(pk=sch_id)
                        if name: sch.name = name
                        if quota: 
                            sch.max_enrolled = int(quota)
                            sch.available = sch.max_enrolled - sch.users_enrolled.count()
                        sch.save()
                        return JsonResponse({'status': 'success', 'message': 'Saved'})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': str(e)})

                elif command == "move_student":
                    user_id = request.POST.get('user_id')
                    target_sch_id = request.POST.get('target_schedule_id')
                    try:
                        ud = UserData.objects.get(pk=user_id)
                        target_sch = Schedule.objects.get(pk=target_sch_id)
                        session = target_sch.session
                        
                        # Remove from old schedule in this session
                        old_sch = ud.get_schedule_for_session(session)
                        if old_sch:
                            old_sch.available += 1
                            old_sch.save()
                            ud.schedules.remove(old_sch)
                        
                        # Add to new
                        if target_sch.available > 0:
                            target_sch.available -= 1
                            target_sch.save()
                            ud.schedules.add(target_sch)
                            ud.save()
                            return JsonResponse({'status': 'success'})
                        else:
                             return JsonResponse({'status': 'error', 'message': 'Target schedule full'})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': str(e)})

                messages.info(request, f"{command} success")
            except Exception as ex:
                messages.info(request, ex)

    return render(request, 'war/admin_control.html', {
        "controller" : AdminControl.objects.all(),
        "session" : Session.objects.all(),
        "controller" : AdminControl.objects.all(),
        "users"   : UserData.objects.all().order_by('name')
    })

@login_required
def schedule_list_view(request):
    sessions = Session.objects.filter(active=True)
    return render(request, "war/schedule_view.html", {
        "sessions": sessions
    })