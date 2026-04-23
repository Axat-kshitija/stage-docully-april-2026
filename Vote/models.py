from django.db import models
from userauth.models import User, EndUserType, InvitationStatus
from dataroom.models import Dataroom
from data_documents.models import DataroomFolder, Categories, store_dataroom_files1
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import AllNotifications
from users_and_permission.models import DataroomMembers
from dms.custom_azure import AzureMediaStorage,AzureMediaStorage1



def vote_directory_path_for_dataroom(instance, filename):
	type_of_pic = "vote"
	d_id = instance.id
	return 'voting/{0}/{1}'.format(type_of_pic, filename)


class Vote(models.Model):	
	title = models.CharField(null=True, blank=True, max_length=1000)
	dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, null=True, blank=False)
	vote_created = models.DateTimeField(auto_now_add=True)
	vote_updated = models.DateTimeField(auto_now_add=True)
	vote_created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
	is_deleted = models.BooleanField(default=False)
	status = models.BooleanField(default=True)
	description = models.CharField(null=True, blank=True, max_length=1000)
	start = models.DateTimeField(auto_now_add=True)
	end = models.DateTimeField(auto_now_add=False)
	path = models.FileField(blank= True,storage=AzureMediaStorage(), upload_to=vote_directory_path_for_dataroom, null=True, default="")
	pages=models.IntegerField(blank=True,null=True,max_length=100)
	file_size = models.FloatField(blank=True, null=True)
	file_size_mb = models.FloatField(blank=True, null=True)
	document_file_name = models.CharField(max_length=100, blank=True, null=True)
	dataroomfile = models.ForeignKey(DataroomFolder, blank=True, null=True,on_delete=models.CASCADE)	
	# text1 = models.CharField(max_length=100)

	def save(self, *args, **kwargs):
		if self.file_size: 
			# print(self.file_size,'check ghgjghjhgjh 1')
			self.file_size_mb = round(self.file_size/1024/1024, 3)
			# print(self.file_size_mb,'check ghgjghjhgjh 2')

		if self.path:
			# print(str(self.path),'rushikesh path')
			self.document_file_name=str(self.path)
		# if self.dataroomfile:
		# 	self.document_file_name=self.dataroomfile.name
		# 	self.file_size=0
		# 	self.file_size_mb=0

		super(Vote, self).save(*args, **kwargs)

class VoterGroup(models.Model):
	title = models.CharField(null=True, blank=True, max_length=1000)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
	is_deleted = models.BooleanField(default=False)
	status = models.BooleanField(default=True)
	description = models.CharField(null=True, blank=True, max_length=1000)
	dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, blank=False, null=True)

class VoterGroupMember(models.Model):
	votergroup = models.ForeignKey(VoterGroup, on_delete=models.CASCADE, blank=False, null=True)
	member = models.ForeignKey(DataroomMembers, on_delete=models.CASCADE, blank=False, null=True)
	created_date = models.DateTimeField(auto_now_add=True, blank=False,null=False)
	status = models.BooleanField(default=True)

class VotingResult(models.Model):
	created = models.DateTimeField(auto_now_add=True, blank=True,null=True)
	vote = models.ForeignKey(Vote, on_delete=models.CASCADE, blank=False, null=True)
	member = models.ForeignKey(DataroomMembers, on_delete=models.CASCADE, blank=False, null=True)
	result = models.CharField(null=True, blank=True, max_length=1000)
	description = models.CharField(null=True, blank=True, max_length=1000)
	dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, blank=False, null=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
	vote_date = models.DateTimeField(auto_now_add=True, blank=True,null=True)
	status = models.BooleanField(default=True)
