from django.db import models

from account.models import CTFTeam


class Challenge(models.Model):
    chal_id = models.CharField(max_length=20, primary_key=True)
    name = models.TextField()
    author = models.TextField()
    category = models.TextField()
    description = models.TextField()
    min_points = models.IntegerField()
    max_points = models.IntegerField()
    flag = models.CharField(max_length=1000)

    active = models.BooleanField()  # only active challenges get solves


class ChallengeFile(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    basename = models.TextField()
    url = models.TextField()


class ChallengeSolve(models.Model):
    challenge = models.ForeignKey(
        Challenge, on_delete=models.CASCADE
    )  # only done when not active
    team = models.ForeignKey(CTFTeam, on_delete=models.CASCADE)
    time_of_solve = models.DateTimeField(auto_now_add=True)
