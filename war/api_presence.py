from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# from .admin import send_certificate
from .user_qr_code import decrypt
from .models import Presence, attend, get_events, get_presences

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

def is_valid(request):
    api_key = request.POST.get("API_KEY", "")
    return settings.API_KEY == api_key

def authentication_error(request):
    return JsonResponse({
        "status_code"    : 401,
        "message"   : "authentication error"
    }, status=401)

def api_attend(request):
    # this will return 404 if the user_id not found
    if not is_valid(request):
        return authentication_error(request)

    try:
        if not request.POST.get("presence_id") or not request.POST.get("enc"):
             return JsonResponse({
                "status_code"   : 400,
                "message"       : "missing presence_id or enc"
            }, status=400)

        enc = request.POST.get("enc", "")
        user_id = decrypt(enc)
        presence_id = int(request.POST.get("presence_id", "0"))
    except ValueError:
        return JsonResponse({
            "status_code"   : 400,
            "message"       : "invalid data format"
        }, status=400)

    # check qr code validation
    if user_id == "invalid":
        return JsonResponse({
            "status_code"   : 400,
            "message"       : "qr_code is invalid"
        }, status=400)

    # check payment of the registration
    attend_data = attend(int(presence_id), int(user_id))

    # user id or presence id is wrong
    if attend_data['message'] == "not_found":
        return JsonResponse({
            "status_code"   : 404,
            "message"       : "user id or presence id not found"
        }, status=404)

    attend_data["status_code"] = 200
    
    # automate send email when qrcode scanned
    # try:
    #     send_certificate(user)
    # except Exception as ex:
    #     logger.warning(ex)
    #     logger.warning(f"Sending Certificate error, id={user.id}, name={user.name}")
    
    return JsonResponse(attend_data, status=200, safe=False)

def api_get_events(request):
    if not is_valid(request):
        return authentication_error(request)
    data = get_events()
    return JsonResponse(data, safe=False)

def api_get_presences(request):
    # return 404 if event_id not found
    if not is_valid(request):
        return authentication_error(request)
    
    event_id = int(request.POST.get("event_id", "0"))
    data = get_presences(event_id)
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_handler(request, api_type):
    if api_type == "attend":
        return api_attend(request)
    elif api_type == "get_events":
        return api_get_events(request)
    elif api_type == "get_presences":
         return api_get_presences(request)
    else:
        return JsonResponse({
            "status_code"      : 404,
            "message"   : "not found"
        }, status=404)