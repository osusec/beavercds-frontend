from django.conf import settings

def ctf_event (request):
    return {
        "event_name": settings.CTF_EVENT_NAME,
        "event_date": settings.CTF_EVENT_DATE,
        "ctftime_link": settings.CTF_CTFTIME_LINK,
    }
    