from django.conf import settings

def ctf_event (request):
    return {
        "event_name": settings.CTF_EVENT_NAME,
        "event_start": settings.CTF_EVENT_START,
        "event_end": settings.CTF_EVENT_END,
        "ctftime_link": settings.CTF_CTFTIME_LINK,
        "gitlab_link": settings.CTF_GITLAB_LINK,
        "discord_link": settings.CTF_DISCORD_LINK,
        "email_link": settings.CTF_EMAIL_LINK,
        "bluesky_link": settings.CTF_BSKY_LINK,
        'sponsors': settings.SPONSORS
    }
    