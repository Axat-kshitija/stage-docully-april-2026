# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from myteams.models import *

# @receiver(post_save, sender=MyTeams)
# def create_my_team_branding(sender, instance, created, **kwargs):
#     if created:
#         print ("create my team branding called")
#         MyTeamBranding.objects.create(user=instance)

# @receiver(post_save, sender=MyTeams)
# def save_user_my_team_branding(sender, instance, **kwargs):
#     print ("save user my team branding called")
#     instance.save()