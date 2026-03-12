"""
URL configuration for bctf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
from django.views.decorators.csrf import csrf_exempt
from account.views import oauth_step2


urlpatterns = [
    path ('', FrontPage, name='bctf-home'),
    path ('admin/', admin.site.urls),
    path ('scores/', Scores, name='scoreboard'),
    path ('account/', include ('account.urls')),
    path ('chals/', include ('chals.urls')),
    # API endpoints below
    path ('api/checkaccess/', CheckAccess, name='check-access'),
    path ('api/resolvestate/', csrf_exempt(ResolveState.as_view()), name='resolve-state'), # TODO: DO NOT CSRF_EXEMPT :)
    # TODO: hardcoded for ctftime for now:
    path ('integrations/ctftime/callback', oauth_step2, name='oauth-step2'),
]
