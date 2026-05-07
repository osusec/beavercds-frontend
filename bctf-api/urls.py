from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    # API endpoints below
    path("api/checkaccess", CheckAccess.as_view(), name="check-access"),
    path("api/resolvestate", ResolveState.as_view(), name="resolve-state"),
]
