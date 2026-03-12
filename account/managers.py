from django.contrib.auth.models import BaseUserManager


class CTFTeamManager(BaseUserManager):
    def _create (self, team_name, password=None, ctftime_bool=False):
        if not team_name:
            raise ValueError('Missing team name.')
        if ctftime_bool and password:
            raise ValueError('CTFTime teams cannot set a password')
        new_team = self.model(
            team_name=team_name,
            ctftime_bool=ctftime_bool
        )
        new_team.set_password(password)
        return new_team


    def create_user (self, team_name, password=None, ctftime_bool=False):
        new_team = self._create (team_name, password, ctftime_bool)
        new_team.save(using=self._db)
        return new_team


    def create_superuser (self, team_name, password=None, ctftime_bool=False):
        new_team  = self._create (team_name, password, ctftime_bool)
        new_team.is_admin = True
        new_team.save(using=self._db)
        return new_team

    # get_by_natural_key() is implemented by BaseUserManager
