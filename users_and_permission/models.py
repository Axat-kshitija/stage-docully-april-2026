from django.db import models
from userauth.models import User, EndUserType, InvitationStatus
from dataroom.models import Dataroom
from data_documents.models import DataroomFolder, Categories, store_dataroom_files1
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import AllNotifications
from django.utils import timezone

class DataroomGroups(models.Model):
    group_name = models.CharField(null=True, blank=True, max_length=1000)
    dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, null=True, blank=False)
    group_created = models.DateTimeField(auto_now_add=True)
    group_updated = models.DateTimeField(auto_now_add=True)
    group_created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    limited_access = models.BooleanField(default=False)
    end_user = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    access_revoke = models.DateTimeField(null=True, blank=True)
    # is_watermarking = models.BooleanField(default=False)

@receiver(post_save, sender=DataroomGroups)
def create_user_profile1(sender, instance, created, **kwargs):
    if created:
        DataroomGroupPermission.objects.create(dataroom_groups=instance, dataroom_id=instance.dataroom_id,is_q_and_a=True,is_updates=True,is_edit_index=True)
        AllNotifications.objects.create(dataroom_groups_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.group_created_by.id)

class DataroomMembers(models.Model):
    
    dataroom = models.ForeignKey(Dataroom,on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="dataroom_member")
    member_type = models.ForeignKey(EndUserType, on_delete=models.CASCADE, null=True, blank=True)
    member_added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="dataroom_member_added_by")
    is_primary_user = models.BooleanField(default=False)
    is_q_a_user = models.BooleanField(default=False)
    is_q_a_submitter_user = models.BooleanField(default=False)
    is_dataroom_admin = models.BooleanField(default=False)
    is_la_user = models.BooleanField(default=False)
    is_end_user = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    end_user_group = models.ManyToManyField(DataroomGroups, blank=True)
    group_name=models.CharField(max_length=200,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    is_deleted_end = models.BooleanField(default=False)
    is_deleted_la = models.BooleanField(default=False)
    disclaimer_status = models.BooleanField(default=False, blank=True)
    disclaimer_signed_date = models.DateTimeField(blank=True,null=True)
    disclaimer_signed_id = models.CharField(null=True, blank=True, max_length=1000)
    event_timestamp = models.DateTimeField(default=timezone.now)
    memberactivestatus=models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_deleted==True: 

                self.memberactivestatus=False

        super(DataroomMembers, self).save(*args, **kwargs)     

@receiver(post_save, sender=DataroomMembers)
def create_user_profile2(sender, instance, created, **kwargs):
    if created:
        AllNotifications.objects.create(dataroom_member_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.member_added_by.id)


class DataroomGroupPermission(models.Model):
    dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, null=True, blank=True)
    dataroom_groups = models.OneToOneField(DataroomGroups, on_delete=models.CASCADE, null=True, blank=True)
    is_watermarking = models.BooleanField(default=False)
    is_doc_as_pdf = models.BooleanField(default=False)
    is_excel_as_pdf = models.BooleanField(default=False)
    is_drm = models.BooleanField(default=False)
    is_edit_index = models.BooleanField(default=False)
    is_overview = models.BooleanField (default=False)
    is_q_and_a = models.BooleanField(default=False)
    is_users_and_permission = models.BooleanField(default=False)
    is_updates = models.BooleanField(default=False)
    is_reports = models.BooleanField(default=False)
    is_voting = models.BooleanField(default=False)
    is_watermarking_previous = models.BooleanField(default=False)
    is_doc_as_pdf_previous = models.BooleanField(default=False)
    is_excel_as_pdf_previous = models.BooleanField(default=False)
    is_drm_previous = models.BooleanField(default=False)
    is_edit_index_previous = models.BooleanField(default=False)
    is_overview_previous = models.BooleanField(default=False)
    is_q_and_a_previous = models.BooleanField(default=False)
    is_users_and_permission_previous = models.BooleanField(default=False)
    is_updates_previous = models.BooleanField(default=False)
    is_reports_previous = models.BooleanField(default=False)
    is_voting_previous = models.BooleanField(default=False)
    viewer_limit_count=models.CharField(max_length=50,null=True,blank=True)
    upload_ristrict_with_timer = models.BooleanField(default=False)
    is_irm_protected = models.BooleanField(default=False)
    is_irm_active = models.BooleanField(default=False)


class DataroomGroupFolderSpecificPermissions(models.Model):
    is_no_access = models.BooleanField(default=True)
    is_access = models.BooleanField(default=False)
    is_view_only = models.BooleanField(default=False)
    is_view_and_print = models.BooleanField(default=False)
    is_view_and_print_and_download = models.BooleanField(default=False)
    is_upload = models.BooleanField(default=False)
    is_watermarking = models.BooleanField(default=False)
    is_drm = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_shortcut = models.BooleanField(default=False)
    folder = models.ForeignKey(DataroomFolder, on_delete=models.CASCADE, null=True, blank=True)
    dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, null=True, blank=True)
    dataroom_groups = models.ForeignKey(DataroomGroups, on_delete=models.CASCADE, null=True, blank=True)
    permission_given_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="Created")
    permission_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="Updated")
    watermarking_file = models.FileField(blank=True, null=True)
    access_revoke = models.DateTimeField(null=True, blank=True)
    folder_timer_upload_ristrict = models.BooleanField(default=False)
    folder_timer_upload_ristrict_date = models.DateTimeField(null=True, blank=True)
    is_irm_protected = models.BooleanField(default=False)


class DataroomMemberInvitation(models.Model):
    dataroom_member = models.ForeignKey(DataroomMembers, on_delete=models.CASCADE, null=True, blank=True)
    invitation_sent = models.DateTimeField(auto_now_add=True)
    invitation_expiry = models.DateTimeField(auto_now_add=True)
    invitation_status = models.ForeignKey(InvitationStatus, on_delete=models.CASCADE, null=True, blank=True)

from django.db import transaction

class RcentUpdate(models.Model):
    """docstring for RcentUpdate"""
    user = models.ForeignKey(User, models.CASCADE, related_name="recent_update_admin_user")
    member = models.ManyToManyField(User, blank=True)
    group = models.ManyToManyField(DataroomGroups, blank=True)
    categories = models.ManyToManyField(Categories, blank=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE,)
    subject = models.CharField(max_length=100,)
    message = models.TextField()
    send_update_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    document = models.FileField(blank= True, upload_to=store_dataroom_files1, null=True, default="")
    document_file_name = models.CharField(max_length=100, blank=True, null=True)
    file = models.ForeignKey(DataroomFolder, blank=True, null=True,on_delete=models.CASCADE)
    # text1 =models.CharField(max_length=100)
    
# @receiver(post_save, sender=RcentUpdate)
# def create_user_profile1(sender, instance, created, **kwargs):
#     if created:
#         # if instance.member:
#         #     for i in instance.member.all():
#                 print(instance.member.all(),'rushikesh')
#                 for i in instance.member.all():
#                     print(i,'__ddddd')
#                 AllNotifications.objects.create(dataroom_updates_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.user.id)
#         # if instance.group:
#         #     for i in instance.group.all():
#         #         print(i)
#         #         AllNotifications.objects.create(dataroom_updates_id=instance.id, dataroom_id=instance.dataroom_id, user_id=instance.user.id,dataroom_groups=i)
    # def save(self , *args, **kwargs):
    #     super(RcentUpdate, self).save( *args, **kwargs) 
    #     print('working ___________')
    #     transaction.on_commit(self.notificationsave)

    # def notificationsave(self):
    #     print(self.member.all())
    #     if self.member.all():
    #             for i in self.member.all():
    #                 print(i,'rushikesh')
    #                 AllNotifications.objects.create(dataroom_updates_id=self.id, dataroom_id=self.dataroom_id, user_id=self.user.id,dataroom_member=i)
    #     if self.group.all():
    #             for i in self.group.all():
    #                 print(i)
    #                 AllNotifications.objects.create(dataroom_updates_id=self.id, dataroom_id=self.dataroom_id, user_id=self.user.id,dataroom_groups=i)

            


class Doc_view_limit(models.Model):
    dataroom_folder=models.ForeignKey(DataroomFolder,models.CASCADE)
    member=models.ForeignKey(DataroomMembers,models.CASCADE)
    count=models.CharField(null=True,blank=True,max_length=50)





class Irm_group_protection_details(models.Model):
    dataroom_groups = models.ForeignKey(DataroomGroups, on_delete=models.CASCADE, null=True, blank=True)
    label_name=models.CharField(null=True,blank=True,max_length=100)
    label_id=models.CharField(null=True,blank=True,max_length=100)
    group_id = models.CharField(null=True,blank=True,max_length=500)
    group_name = models.CharField(null=True,blank=True,max_length=500)
    label_policy_name = models.CharField(null=True,blank=True,max_length=500)
    label_policy_id = models.CharField(null=True,blank=True,max_length=500)
    expiry_days = models.CharField(null=True,blank=True,max_length=50)
