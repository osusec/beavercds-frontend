from django.utils.timezone import datetime

CTF_EVENT_NAME = 'DamCTF 2026'
CTF_EVENT_START = datetime.fromisoformat('2026-05-09 00:00:00.000+00:00')
CTF_EVENT_END = datetime.fromisoformat('2026-05-11 00:00:00.000+00:00')
CTF_CTFTIME_LINK = 'https://ctftime.org/event/3124/'
THRESHOLD_SOLVES = 20
SPONSORS = [
    {
        'name': 'AWS',
        'link': 'https://aws.amazon.com',
        'logo_link': 'aws-logo-color.png'
    },
    {
        'name': 'DC541',
        'link': 'https://www.dc541.org',
        'logo_link': 'dc541-logo-transparent.png'
    },
    {
        'name': 'RET2',
        'link': 'https://ret2.io',
        'logo_link': 'ret2_logo_bold_white_transparent_bg.png'
    },
        {
        'name': 'SecuringHardware',
        'link': 'https://securinghardware.com',
        'logo_link': 'securinghardware-white.png'
    },
]