# from django.apps import AppConfig
# #from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.utils.translation import ugettext_lazy as _
# from myteams.signals import create_my_team_branding, save_user_my_team_branding
# from .models import *

# class MyteamsConfig(AppConfig):
#     name = 'myteams'
#     verbose_name = _('myteams')

#     def ready(self):
#     	post_save.connect(create_my_team_branding, sender=MyTeams)
#     	post_save.connect(save_user_my_team_branding, sender=MyTeams)