from django.db import models
from userauth.models import User
from dataroom.models import Dataroom
from data_documents.models import DataroomFolder, Categories
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import AllNotifications

# Create your models here.
class QuestionAnswer(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, blank=True, null=True)
	question = models.CharField(max_length=1000, blank=True, null=True)
	answer  = models.CharField(max_length=10485760, blank=True, null=True)
	qna = models.ForeignKey('self',blank=True, null=True,on_delete=models.CASCADE)
	folder = models.ForeignKey(DataroomFolder, blank=True, null=True,on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)
	updated_date = models.DateTimeField(auto_now=True)
	category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="question")
	acc = models.BooleanField(default=False)
	reg = models.BooleanField(default=False)
	final = models.BooleanField(default=False)
	is_faq = models.BooleanField(default=False)

	def __str__(self):
		return self.question


class FAQ(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, blank=True, null=True)
	question = models.CharField(max_length=1000, blank=True, null=True)
	answer  = models.CharField(max_length=10485760, blank=True, null=True)
	qna = models.ForeignKey('self',blank=True, null=True,on_delete=models.CASCADE)
	folder = models.ForeignKey(DataroomFolder, blank=True, null=True,on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='created_by')
	updated_date = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, default=None, related_name='updated_by')
	status = models.BooleanField(default=True)
	acc = models.BooleanField(default=False)
	reg = models.BooleanField(default=False)
	final = models.BooleanField(default=False)
	is_faq = models.BooleanField(default=False)
	file_flag = models.BooleanField(default=False)


@receiver(post_save, sender=QuestionAnswer)
def AddedNotification(sender, instance, **kwargs):
	all_noti = AllNotifications.objects.filter(qna_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.user.id)
	if not all_noti:
		AllNotifications.objects.create(qna_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.user.id)
	

class UserBasedCategories(models.Model):
	"""docstring for UserBasedCategories"""
	category = models.ForeignKey(Categories, on_delete=models.CASCADE)
	assign_user = models.ForeignKey(User, on_delete=models.CASCADE)
		
