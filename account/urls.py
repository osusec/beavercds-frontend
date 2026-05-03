#
# Account urls.py
#

from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path ('profile/', ProfilePage.as_view(), name='profile-home'),
    path ('register/', SignUpView.as_view(), name='profile-signup'),
    path ('oauth/', OAuth_Step1.as_view(), name='oauth-step1'),
    path ('oauth/callback/', OAuth_Step2.as_view(), name='oauth-step2'),
    path ('quick/', TokenAuth.as_view(), name='token_auth'),
    path ('token/create', CreateToken.as_view(), name='create_token'),
    path ('token/delete', DeleteToken.as_view(), name='delete_token'),
    path ('email/create', AddContactEmail.as_view(), name='create_email'),
    path ('email/delete', DeleteContactEmail.as_view(), name='delete_email'),
    # path ('', include ('django.contrib.auth.urls')),
    path ('login/', auth_views.LoginView.as_view(), name='login'),
    path ('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
