from urllib.parse import unquote
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get ("timezone")
        try:
            timezone.activate(zoneinfo.ZoneInfo(unquote(tzname)))
        except:
            timezone.deactivate()
            
        return self.get_response(request)
