from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path ('', ListChal.as_view(), name='chals-list'),
    path ('submit', SubmitFlag.as_view(), name='submit-flag')
]
