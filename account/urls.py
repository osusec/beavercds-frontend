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
    path ('profile/', login_required(ProfilePage), name='profile-home'),
    path ('register/', SignUpView.as_view(), name='profile-signup'),
    path ('oauth/', oauth_step1, name='oauth-step1'),
    path ('token/', TokenAuth.as_view(), name='token_auth'),
    path ('token/create', CreateToken.as_view(), name='create_token'),
    path ('token/delete', DeleteToken.as_view(), name='delete_token'),
    path ('', include ('django.contrib.auth.urls')),
    #path ('ctftime/callback', auth, name='auth') # TODO
]
