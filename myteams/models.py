from django.db import models
from userauth.models import * 

def user_directory_path_for_my_teams_logo(instance, filename): 
    type_of_pic = "logo"
    u_id = instance.user.id
    m_id = instance.id
    return 'user_{0}/my_team_{1}/{2}/{3}'.format(u_id, m_id, type_of_pic, filename)

def user_directory_path_for_my_chanel_logo(instance, filename): 
    type_of_pic = "logo"
    u_id = instance.user.id
    m_id = instance.id
    return 'user_{0}/my_chanel_{1}/{2}/{3}'.format(u_id, m_id, type_of_pic, filename)

def user_directory_path_for_my_teams_branding_logo(instance, filename): 
    type_of_pic = "branding"
    u_id = instance.my_team_branding_done_by.id
    m_id = instance.my_team_branding.id
    return 'user_{0}/my_team_{1}/{2}/{3}'.format(u_id, m_id, type_of_pic, filename)

def user_directory_path_for_my_teams_email_header_logo(instance, filename): 
    type_of_pic = "email_header"
    u_id = instance.my_team_branding_done_by.id
    m_id = instance.my_team_branding.id
    return 'user_{0}/my_team_{1}/{2}/{3}'.format(u_id, m_id, type_of_pic, filename)

def user_directory_path_for_my_teams_favicon_icon(instance, filename): 
    type_of_pic = "favicon_icon"
    u_id = instance.my_team_branding_done_by.id
    m_id = instance.my_team_branding.id
    return 'user_{0}/my_team_{1}/{2}/{3}'.format(u_id, m_id, type_of_pic, filename)


class Mychanels(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	chanel_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="chanel_created_by")
	chanel_created_at = models.DateTimeField(auto_now_add=True)
	chanel_updated_at = models.DateTimeField(auto_now_add=True)
	chanel_name = models.CharField(max_length=100, blank=True, null=True)
	dataroom_allowed = models.IntegerField(default=0)
	dataroom_admin_allowed = models.IntegerField(default=0)
	chanel_logo = models.FileField(blank=True, null=True, upload_to=user_directory_path_for_my_chanel_logo, default="default_images/my_team/myteam-default.png")
	dataroom_storage_allowed = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True, default=0.00)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	usage_alertemail=models.CharField(max_length=100, blank=True, null=True)
	usage_alertemailtwo=models.CharField(max_length=100, blank=True, null=True)
	storage_exceed=models.BooleanField(default=False)
	is_deleted=models.BooleanField(default=False)
	is_deleted_request=models.BooleanField(default=False)
	is_deleted_requestat=models.DateTimeField(blank=True, null=True)
	is_deleted_deletedat=models.DateTimeField(blank=True, null=True)

class chanelMembers(models.Model):
	member = models.ForeignKey(User, on_delete=models.CASCADE,related_name="chanelmember")
	member_added = models.DateTimeField(auto_now_add=True)
	member_updated = models.DateTimeField(auto_now_add=True)
	chanel = models.ForeignKey(Mychanels, on_delete=models.CASCADE ,blank=True, null=True)
	member_added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,related_name="chanelmemberaddedby")
	accesstodataroomusers=models.BooleanField(default=False)
	allowtoaddnewmember=models.BooleanField(default=False)
	allowtoaddnewteam=models.BooleanField(default=False)

class chanelMemberInvitation(models.Model):
	chanel_members = models.ForeignKey(chanelMembers, on_delete=models.CASCADE)
	inviatation_sent =   models.DateTimeField(auto_now_add=True)
	invitation_expiry = models.DateTimeField(auto_now_add=True)
	invitation_status = models.ForeignKey(InvitationStatus, on_delete=models.CASCADE, blank=True, null=True)
	is_invitation_expired = models.BooleanField(default=False)

# Create your models here.
class MyTeams(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	team_created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="team_created_by")
	team_created_at = models.DateTimeField(auto_now_add=True)
	team_updated_at = models.DateTimeField(auto_now_add=True)
	team_name = models.CharField(max_length=100, blank=True, null=True)
	dataroom_allowed = models.IntegerField(default=0)
	dataroom_admin_allowed = models.IntegerField(default=0)
	my_team_logo = models.FileField(blank=True, null=True, upload_to=user_directory_path_for_my_teams_logo, default="default_images/my_team/myteam-default.png")
	dataroom_storage_allowed = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True, default=0.00)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	onlinesubscriber=models.BooleanField(default=False)
	usage_alertemail=models.CharField(max_length=100, blank=True, null=True)
	usage_alertemailtwo=models.CharField(max_length=100, blank=True, null=True)
	storage_exceed=models.BooleanField(default=False)
	chanel=models.ForeignKey(Mychanels, on_delete=models.CASCADE, blank=True, null=True)
	is_deleted=models.BooleanField(default=False)
	is_deleted_request=models.BooleanField(default=False)
	is_deleted_requestat=models.DateTimeField(blank=True, null=True)
	is_deleted_deletedat=models.DateTimeField(blank=True, null=True)

class TeamMembers(models.Model):
	member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member')
	member_added = models.DateTimeField(auto_now_add=True)
	member_updated = models.DateTimeField(auto_now_add=True)
	myteam = models.ForeignKey(MyTeams, related_name="myteam", on_delete=models.CASCADE ,blank=True, null=True)
	member_added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member_added_by", blank=True, null=True)
	accesstodataroomusers=models.BooleanField(default=False)
	allowtoaddnewmember=models.BooleanField(default=False)
	allowtoaddnewdataroom=models.BooleanField(default=False)

class TeamMemberInvitation(models.Model):
	team_members = models.ForeignKey(TeamMembers, on_delete=models.CASCADE, related_name='team_members')
	inviatation_sent =   models.DateTimeField(auto_now_add=True)
	invitation_expiry = models.DateTimeField(auto_now_add=True)
	invitation_status = models.ForeignKey(InvitationStatus, on_delete=models.CASCADE, blank=True, null=True)
	is_invitation_expired = models.BooleanField(default=False)

class MyTeamBranding(models.Model):
	my_team_branding_done_by = models.ForeignKey(User, models.CASCADE, related_name="my_teams_branding_done")
	my_team_branding = models.ForeignKey(MyTeams, models.CASCADE, related_name="MyTeams")
	background_color = models.CharField(max_length=1000, blank=True, null=True, default="#f200bd")
	email_background_color = models.CharField(max_length=1000, blank=True, null=True, default="#f200bd")
	custom_login_border_color = models.CharField(max_length=1000, blank=True, null=True, default="#f200bd")
	border_top_color = models.CharField(max_length=1000, blank=True, null=True, default="#f200bd")
	branding_logo = models.ImageField(blank=True, null=True, upload_to= user_directory_path_for_my_teams_branding_logo, default="default_images/my_team/branding_logo.png")
	email_header = models.ImageField(blank=True, null=True, upload_to = user_directory_path_for_my_teams_email_header_logo, default="default_images/my_team/email_header.png")
	favicon_icon = models.ImageField(blank=True, null=True, upload_to = user_directory_path_for_my_teams_favicon_icon, default="default_images/my_team/favicon_icon.ico")
	