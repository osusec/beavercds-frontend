from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CTFTeam (AbstractUser):
    name = models.TextField()



'''
TODO: Team
- CTFTime (oauth through individual user)
- NormalRegistration
    - Email (username + password for now)

- all others join through token
'''


