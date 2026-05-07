from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import *

urlpatterns = [
    path("", ListChal.as_view(), name="chals-list"),
    path("submit", SubmitFlag.as_view(), name="submit-flag"),
]
