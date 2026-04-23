from django.db import models
from userauth.models import User
from dataroom.models import Dataroom, ContactGroup, Contacts
from django.db.models.signals import post_save
from django.dispatch import receiver
# from qna.models import *
# from users_and_permission.models import DataroomMembers
from datetime import datetime

# Create your models here.
class Notifications(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE) #1 to 1 link with Django User
    logo = models.ImageField()
    send_notification_members = models.BooleanField(default=False,)
    use_file_workshop_home = models.BooleanField(default=False,)
    hide_file_index_admin = models.BooleanField(default=False,)
    workspace_name = models.CharField(max_length=100,)
    heading = models.CharField(max_length=200,)
    description = models.CharField(max_length=2000)
    dataroom = models.OneToOneField(Dataroom, on_delete=models.CASCADE)


# Create your models here.
class Message(models.Model):
    user_rec = models.ForeignKey(User, related_name="message_rec",on_delete=models.CASCADE)
    user_send = models.ForeignKey(User, related_name="message_sender",on_delete=models.CASCADE)
    latestsender = models.ForeignKey(User, related_name="latestmessage_sender",blank=True, null=True,on_delete=models.CASCADE)
    send_message = models.CharField(max_length=2000)
    dataroom = models.ForeignKey(Dataroom, blank=True, null=True,on_delete=models.CASCADE)
    received_at = models.DateTimeField(auto_now_add = True)
    latestmessage_at = models.DateTimeField(null=True,blank = True)
    read = models.BooleanField(default=False)
    subject = models.CharField(max_length=1000, default="")
    msg = models.ForeignKey('self', on_delete=models.CASCADE,blank=True, null=True)
    main = models.BooleanField(default=False)

# method for updating
@receiver(post_save, sender=Message)
def after_message(sender, instance, **kwargs):
    if not instance.msg_id:
        instance.msg_id=instance.id
        print('coming herer jfjfjfjfjfj')
    if instance.id == instance.msg_id:
        instance.main = True
    elif instance.subject == 'Message':
        instance.main = True
    else:
        instance.main = False
    instance.latestmessage_at=datetime.now()
    post_save.disconnect(after_message, sender=Message)
    instance.save()
    post_save.connect(after_message, sender=Message)



# Create your models here.
from data_documents.models import Bulkuploadstatus

class AllNotifications(models.Model):
    user = models.ForeignKey(User, blank=True, null=True,on_delete=models.CASCADE)
    dataroom = models.ForeignKey(Dataroom, blank=True, null=True,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    dataroom_member = models.ForeignKey('users_and_permission.DataroomMembers', blank=True, null=True,on_delete=models.CASCADE)
    dataroom_groups = models.ForeignKey('users_and_permission.DataroomGroups', blank=True, null=True,on_delete=models.CASCADE)
    dataroom_folder = models.ForeignKey('data_documents.DataroomFolder', blank=True, null=True,on_delete=models.CASCADE)
    dataroom_updates = models.ForeignKey('users_and_permission.RcentUpdate', blank=True, null=True,on_delete=models.CASCADE)
    qna = models.ForeignKey('qna.QuestionAnswer', blank=True, null=True,on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    # bulkuploadid=models.ForeignKey(Bulkuploadstatus,blank=True,null=True)
    bulkuploadd=models.ForeignKey(Bulkuploadstatus,models.CASCADE,related_name="bulkuploddataishere",blank=True,null=True)
    dataroom_member_invitation_accept = models.ForeignKey('userauth.InviteUser', blank=True, null=True,on_delete=models.CASCADE)
    # bulkupload = models.ForeignKey(User, models.CASCADE, related_name="permanent_deleted_by",  blank=True, null=True) 
    # dataroom_folder = models.ForeignKey(DataroomFolder, blank=True, null=True)
    # dataroom_view_image = models.ForeignKey(DataroomViewerImage, blank=True, null=True)
    # dataroom_index_down = models.ForeignKey(IndexDownload, blank=True, null=True)
    # dataroom_folder_view = models.ForeignKey(FolderView, blank=True, null=True)
    # dataroom_folder_down = models.ForeignKey(FolderDownload, blank=True, null=True)
    # dataroom_folder_print = models.ForeignKey(FolderPrint, blank=True, null=True)
    # dataroom_contact_group = models.ForeignKey(ContactGroup, blank=True, null=True)
    # dataroom_contact = models.ForeignKey(Contacts, blank=True, null=True)
    # dataroom_que_ans = models.ForeignKey(QuestionAnswer, blank=True, null=True)
    # dataroom_group = models.CharField(max_length=10, blank=True, null=True)
    # 
    # dataroom_recent_update = models.ForeignKey(RcentUpdate, blank=True, null=True)
    # is_user_created = models.BooleanField(default=False)
    # is_dataroom_created = models.BooleanField(default=False)
    # is_deleted = models.BooleanField(default=False)
