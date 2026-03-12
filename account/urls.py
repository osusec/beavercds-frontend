#
# Account urls.py
#

from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

# TODO: remove
'''django.contrib.auth.urls
login/ [name='login']
logout/ [name='logout']
password_change/ [name='password_change']
password_change/done/ [name='password_change_done']
password_reset/ [name='password_reset']
password_reset/done/ [name='password_reset_done']
reset/<uidb64>/<token>/ [name='password_reset_confirm']
reset/done/ [name='password_reset_complete']
'''

urlpatterns = [
    path ('', login_required(ProfilePage), name='profile-home'),
    path ('register/', SignUpView.as_view(), name='profile-signup'),
    path ('oauth/', oauth_step1, name='oauth-step1'),
    path ('', include ('django.contrib.auth.urls')),
    #path ('ctftime/callback', auth, name='auth') # TODO
]
