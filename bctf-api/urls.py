from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    # API endpoints below
    # Note the lack of trailing slashes in contrast to their rest of the website;
    #  this is following API convention
    path("api/checkaccess", CheckAccess.as_view(), name="check-access"),
    path("api/resolvestate", ResolveState.as_view(), name="resolve-state"),
    path("api/updatebrackets", UpdateBrackets.as_view(), name="update-brackets"),
]
