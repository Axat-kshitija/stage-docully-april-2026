from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid
from userauth.models import *
from userauth import constants, utils
from myteams.models import MyTeams
from dms.settings import *
from django.utils import timezone
from dms.custom_azure import AzureMediaStorage,AzureMediaStorage1


import datetime
import posixpath







def select_storage(instance):
    print('--------inwtqbqqqq',instance)
    return AzureMediaStorage1() if instance.dataroom.is_usa_blob == True else AzureMediaStorage()



def user_directory_path_for_dataroom(instance, filename):
    type_of_pic = "logo"
    u_id = instance.user.id
    d_id = instance.id
    # print('user_{0}/dataroom_{1}/{2}/{3}'.format(u_id, d_id, type_of_pic, filename))
    return 'user_{0}/dataroom_{1}/{2}/{3}'.format(u_id, d_id, type_of_pic, filename)

def user_directory_path_for_dataroom_overview(instance, filename):
    type_of_pic = "overview_video"
    u_id = instance.user.id
    d_id = instance.dataroom.id
    return 'user_{0}/dataroom_{1}/{2}/{3}'.format(u_id, d_id,  type_of_pic, filename)

def user_directory_path_for_dataroom_disclaimer(instance, filename):
    type_of_pic = "disclaimer"
    u_id = instance.user.id
    d_id = instance.dataroom.id
    return 'user_{0}/dataroom_{1}/{2}/{3}'.format(u_id, d_id,  type_of_pic, filename)


class DataroomModules(models.Model):
    is_watermarking = models.BooleanField(default=False)
    is_drm = models.BooleanField(default=False)
    is_question_and_answers = models.BooleanField(default=False)
    is_collabration = models.BooleanField(default=False)
    is_ocr = models.BooleanField(default = False)
    is_editor = models.BooleanField(default = False)

class DataroomStage(models.Model):
    dataroom_stage = models.CharField(max_length=1000, null=False, blank=True)

# class TrialDays(models.Model):
#     """docstring for TrialDays"""
#     days = models.IntegerField(blank=True)


class Dataroom(models.Model):
    EVENT_CHOICES = ( 
    ("1", "Updated recently"), 
    ("2", "Copy File"),
    ("3", "Move Folder"),
    ("4", "Move File"),
    ("5", "Delete Folder"),
    ("6", "Delete File"),
    ("7", "None"),)

    trial_days = models.IntegerField(default=15)
    trial_expired = models.BooleanField(default=False)
    trial_expiry_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    user = models.ForeignKey(User, models.CASCADE) #1 to 1 link with Django User
    dataroom_name = models.CharField(max_length=1000, null=False, blank=True)
    dataroom_nameFront = models.CharField(max_length=1000, null=False, blank=True)

    dataroom_logo = models.ImageField(blank=True,storage=AzureMediaStorage(), upload_to=user_directory_path_for_dataroom,default="images/dataroom-icon.png",max_length=500)#change default image 
    # dataroom_logo = models.ImageField(blank=True, upload_to=user_directory_path_for_dataroom, default="https://docullystorage.blob.core.windows.net/quickstartblobs/dataroom-icon.png",max_length=500)#change default image 

    dataroom_users_permitted=models.IntegerField(default=10000)
    deleterequestactivityby = models.ForeignKey(User, models.CASCADE,null=True,blank=True,related_name='deletedactivityby')
    archiveequestactivityby = models.ForeignKey(User, models.CASCADE,null=True,blank=True,related_name='archiveactivityby')
    account_level_branding = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    dataroom_modules = models.OneToOneField(DataroomModules, models.CASCADE, null=True)
    is_dataroom_on_live = models.BooleanField(default=False)
    is_dataroom_cloned = models.BooleanField(default=False)
    is_request_for_deletion = models.BooleanField(default=False)
    is_request_for_archive = models.BooleanField(default=False)
    dataroom_cloned_from = models.ForeignKey('self', models.CASCADE, null=True, blank=True)
    my_team = models.ForeignKey(MyTeams, models.CASCADE , null=True, blank=True)
    dataroom_storage_allocated = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True, default=0.00)
    dataroom_uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    dataroom_id = models.CharField(max_length=100, default="")
    event = models.CharField(max_length = 50, choices = EVENT_CHOICES, default = '7')
    event_timestamp = models.DateTimeField(default=timezone.now)
    notify = models.BooleanField(default=True)
    addon_payment_overdue=models.BooleanField(default=False)
    plan_payment_overdue=models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)
    delete_at=models.DateTimeField(blank=True, null=True)
    storage_exceed_block=models.BooleanField(default=False)
    delete_request_at=models.DateTimeField(blank=True, null=True)
    offlinedataroom=models.BooleanField(default=False)
    eighty_percent_mail = models.BooleanField(default=False)
    one_fifty_mb_mail = models.BooleanField(default=False)
    two_hundred_mb_mail = models.BooleanField(default=False)
    two_fifty_mb_mail = models.BooleanField(default=False)
    otp_auth = models.BooleanField(default=False,null=True,blank=True)
    is_usa_blob=models.BooleanField(default = False)
    dataroom_version=models.CharField(max_length = 200,blank=True,null=True)


    def save(self, *args, **kwargs):
        if self.id:
            pass
        else:
            self.dataroom_nameFront=self.dataroom_name
            self.dataroom_name= str(self.dataroom_name).replace(' ','_')
                # print('dataroom front name',self.dataroom_name)

            # for i in range(0,300):
            #     if Dataroom.objects.filter(id=i).exists():
            #         print(i,'doing for loop')
            #         dataa=Dataroom.objects.get(id=i)
            #         tempo=dataa.dataroom_name
            #         print(tempo)
            #         Dataroom.objects.filter(id=i).update(dataroom_nameFront=tempo)
        super(Dataroom, self).save(*args, **kwargs) 
        Dataroom.objects.filter(id=self.id).update(dataroom_id=self.id)

     

class dataroomProLiteFeatures(models.Model):
    dataroom=models.ForeignKey(Dataroom,models.CASCADE,null=True , blank=True)
    custom_watermarking=models.BooleanField(default=False)
    two_factor_auth=models.BooleanField(default=False)
    proj_overview=models.BooleanField(default=False)
    proj_video_intro=models.BooleanField(default=False)
    custom_logo=models.BooleanField(default=False)
    custom_external_link=models.BooleanField(default=False)
    auto_logout=models.BooleanField(default=False)
    co_current_logins=models.BooleanField(default=False)
    email_to_dataroom_upload=models.BooleanField(default=False)
    google_drive_upload=models.BooleanField(default=False)
    one_drive_upload=models.BooleanField(default=False)
    sharepoint_upload=models.BooleanField(default=False)
    dropbox_upload=models.BooleanField(default=False)
    favourites=models.BooleanField(default=False)
    redaction=models.BooleanField(default=False)
    la_admin_access=models.BooleanField(default=False)
    bulk_users_upload=models.BooleanField(default=False)
    doculink_perm=models.BooleanField(default=False)
    auto_expire=models.BooleanField(default=False)
    module_perm=models.BooleanField(default=False)
    auto_convert_msoffice=models.BooleanField(default=False)
    qa_with_cat=models.BooleanField(default=False)
    qa_submit=models.BooleanField(default=False)
    desktop_unlimit_upload=models.BooleanField(default=False)
    proj_management=models.BooleanField(default=False)
    voting_perm=models.BooleanField(default=False)
    proj_updates=models.BooleanField(default=False)
    country_perm=models.BooleanField(default=False)

    voting_report_perm=models.BooleanField(default=False)
    index_report_others=models.BooleanField(default=False)
    self_upload_status=models.BooleanField(default=False)
    all_user_upload_status=models.BooleanField(default=False)
    activity_tracker_perm=models.BooleanField(default=False)
    file_view_limit=models.BooleanField(default=False)
    viewer_support=models.BooleanField(default=False)
    fence_viewer=models.BooleanField(default=False)
    print_screen_perm=models.BooleanField(default=False)
    is_irm_protected=models.BooleanField(default=False)
    is_upload_restrict=models.BooleanField(default=False)





class PaidDays(models.Model):
    """docstring for PaidDaysModel"""
    def save(self, *args, **kwargs):
        self.days = (self.end_date - self.start_date).days
        super(PaidDays, self).save(*args, **kwargs)

    days = models.IntegerField(blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    dataroom = models.ForeignKey(Dataroom,  models.CASCADE)
    

class DataroomView(models.Model):
    user = models.ForeignKey(User, models.CASCADE) #1 to 1 link with Django User
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, related_name="dataroom_view_search")
    created_date = models.DateTimeField(auto_now_add=True)
    event = models.CharField(default="dataroom view", max_length=50)
    event_timestamp = models.DateTimeField(default=timezone.now)

class DataroomDeletionAndArchivedLog(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="login_user")
    dataroom = models.ForeignKey(Dataroom, models.CASCADE)
    deleted_or_archived_by_user = models.ForeignKey(User, models.CASCADE, related_name="deleted_or_archived_by")
    deleted_or_archived_time = models.DateTimeField(auto_now_add=True)
    is_delete_request = models.BooleanField(default=False)

class DataroomOverview(models.Model):
    user = models.ForeignKey(User, models.CASCADE) #1 to 1 link with Django User
    send_daily_email_updates = models.BooleanField(default=True,)
    choose_overview_default_page = models.BooleanField(default=True,)
    hide_file_indexing = models.BooleanField(default=True,)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    change_video_ppt = models.FileField(blank=True, null=True, upload_to=user_directory_path_for_dataroom_overview)
    dataroom_overview_heading = JSONField(blank=True, null=True)
    dataroom_custom_links = JSONField(blank=True, null=True)
    show_multiple_times_disclaimer = models.BooleanField(default=False)

class DataroomDisclaimerPreviewStatus(models.Model):
    dataroom_disclaimer_status = models.CharField(max_length=1000, blank=False, null=False)

class DataroomDisclaimer(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE)
    dataroom_disclaimer_name = models.CharField(blank=True, null=True, max_length=1000)
    dataroom_disclaimer = models.FileField(blank=True,storage=AzureMediaStorage(), null=True, upload_to=user_directory_path_for_dataroom_disclaimer)
    is_dataroom_disclaimer_default = models.BooleanField(default=False)
    dataroom_disclaimer_preview_status = models.ForeignKey(DataroomDisclaimerPreviewStatus, models.CASCADE)
    disclaimer_added_date = models.DateTimeField(auto_now_add=True)
    disclaimer_updated_date = models.DateTimeField(auto_now_add=True)
    file_size = models.FloatField(blank=True, null=True)
    file_size_mb = models.FloatField(blank=True, null=True)
    pages=models.IntegerField(blank=True,null=True,default=0)

    def save(self, *args, **kwargs):
        if self.file_size: 
            # print(self.file_size,'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')

            self.file_size_mb = round(self.file_size/1024/1024, 3)
        super(DataroomDisclaimer, self).save(*args, **kwargs)


# @receiver(post_save, sender=DataroomDisclaimer)
# def create_user_profile2(sender, instance, created, **kwargs):
#     import pdb;pdb.set_trace();
#     if created:
#         DataroomMembers.objects.filter(dataroom_id=instance.id,)


class ContactGroup(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    group_name = models.CharField(max_length=1000, blank=True)
    group_created_date = models.DateTimeField(auto_now_add=True)
    group_modified_date = models.DateTimeField(auto_now_add=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, blank=True, null=True)

class Contacts(models.Model):
    user = models.ForeignKey(User, models.CASCADE) #1 to 1 link with Django User
    email = models.EmailField(unique=False)
    first_name = models.CharField(max_length=300, blank=True)
    last_name = models.CharField(max_length=300, blank=True)
    is_visible = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, blank=True, null=True)
    #contact_group = models.ManyToManyField(ContactGroup, blank=True, null=True)

class ContactGroupMembers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE, blank=True, null=True)
    contact = models.ForeignKey(Contacts, on_delete=models.CASCADE, blank=True, null=True)
    member_added = models.DateTimeField(auto_now_add=True)
    member_updated = models.DateTimeField(auto_now_add=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, blank=True, null=True)



class DataroomRoles(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True)
    dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True)
    roles = models.ManyToManyField(Role)

class Watermarking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, blank=True, null=True)
    attachments = models.FileField(blank=True, null=True,max_length=500)
    # watermark_path = models.CharField(blank=True, null=True, max_length=100)
    type = models.CharField(blank=True, null=True, max_length=100)    
    font_size = models.IntegerField(blank=True, null=True)
    opacity = models.FloatField(blank=True, null=True)
    rotation = models.FloatField(blank=True, null=True)
    user_ipaddress = models.BooleanField(default=False)
    user_name = models.BooleanField(default=False)
    user_email = models.BooleanField(default=False)
    current_time = models.BooleanField(default=False)
    dataroom_name = models.BooleanField(default=False)
    custom_text = models.CharField(max_length=50,blank=True, null=True)
    vtop = models.BooleanField(default=False)    
    vcenter = models.BooleanField(default=False)    
    vbottom = models.BooleanField(default=False)
    hleft = models.BooleanField(default=False)
    hmiddle = models.BooleanField(default=False)
    hright = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, blank=True, null=True)





class otp_model( models.Model):
    dataroom = models.ForeignKey(Dataroom, on_delete=models.CASCADE, null=True,blank=True,related_name='dataroom_otp_1')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_otp_1')
    otp = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    is_verifed = models.BooleanField(default=False)