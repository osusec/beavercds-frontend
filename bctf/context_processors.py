from django.conf import settings


def ctf_event(request):
    return {
        "event_name": settings.CTF_EVENT_NAME,
        "event_start": settings.CTF_EVENT_START,
        "event_end": settings.CTF_EVENT_END,
        "ctftime_link": settings.CTF_CTFTIME_LINK,
        "sponsors": settings.SPONSORS,
    }
