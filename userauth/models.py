from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
from datetime import *
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
from ckeditor.fields import RichTextField
from dms.custom_azure import AzureMediaStorage,AzureMediaStorage1








import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_token_user',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    expired = models.BooleanField(_('expired'),default=False)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    name = models.CharField(_('name'), max_length=40)
    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key





import rest_framework.authentication
 
# from .models import Token
 
 
class TokenAuthentication(rest_framework.authentication.TokenAuthentication):
    model = Token








def user_directory_path_for_profile(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # the file path should be like media/1/profile_pic/djay.jpg
   
    #datetime_str = datetime.strptime(date.today(), "%d/%m/%y")#datetime.strftime("%Y-%m-%d-%H-%M-%S")
    type_of_pic = "profile_pic"
    # print ("user id", instance.id)
    # print ('user_{0}/{1}/{2}'.format(instance.id, type_of_pic, filename))
    return 'user_{0}/{1}/{2}'.format(instance.id, type_of_pic, filename)

class EndUserType(models.Model):
    end_user_types = models.CharField(max_length=1000, blank=True)
    is_dataroom_admin = models.BooleanField(default=False)
    is_dataroom_la_admin = models.BooleanField(default=False)
    is_dataroom_enduser = models.BooleanField(default=False)


class Role(models.Model):
  '''
  The Role entries are managed by the system,
  automatically created via a Django data migration.
  '''
  MEMBER = 1
  DATAROOM_ADMIN = 2
  SUPERADMIN = 3
  ADMIN = 4
  ROLE_CHOICES = (
      (MEMBER, 'member'),
      (DATAROOM_ADMIN, 'dataroom_admin'),
      (SUPERADMIN, 'super_admin'),
      (ADMIN, 'admin')
  )

  id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)       


class User(AbstractBaseUser, PermissionsMixin):
    

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    username = models.CharField(max_length=100, blank=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True,null=True)
    company_name = models.CharField(_('company name'), max_length=100, blank=True,null=True)
    country = models.CharField(_('country'), max_length=30, blank=True,null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=False)
    avatar = models.ImageField(upload_to=user_directory_path_for_profile, storage=AzureMediaStorage, null=True, blank=True, default="images/defaultprofilepic.png")
    is_superadmin = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_subscriber = models.BooleanField(default=False)
    is_end_user = models.BooleanField(default=False)
    is_team = models.BooleanField(default=False)
    is_team_member = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)
    is_icon_downloaded = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role,blank=True)
    agree = models.BooleanField(default=False)
    receive_email = models.BooleanField(default=True)
    paid_subscription = models.BooleanField(default=False)
    start_email_notification = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    notify_recieved = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_blocked_time=models.DateTimeField(blank=True,null=True)
    login_trails=models.IntegerField(default=0,blank=True,null=True)
    forget_trails=models.IntegerField(default=0,blank=True,null=True)
    forget_trails_time=models.DateTimeField(blank=True,null=True)

    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        self.email=self.email.lower()
        try:
            super(User, self).save(*args, **kwargs)
        except:
            pass


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def set_username_as_email(self):
        username = self.email
        return username

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

def get_custom_anon_user(User):
    return User(
        username='AnonymousUser',
        birth_date=datetime.date(1410, 7, 15),
    )



class user_password_history(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='pass_history')
    password = models.CharField(max_length=400)




class Captcha_model(models.Model):
    code=models.CharField(max_length=400)
    is_used=models.BooleanField(default=False)








class salt_key(models.Model):
    salt_code=models.CharField(max_length=400)
    





class Profile(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='profile') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=400)
    is_activation_key_status = models.BooleanField(default=False)
    is_reset_key_status = models.BooleanField(default=False)
    reset_key = models.CharField(max_length=500)
    key_expires = models.DateTimeField()

class AccessHistory(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name = 'user') #1 to 1 link with Django User
    logged_in_ip = models.CharField(max_length = 100, blank = False)
    logged_in_time = models.DateTimeField()
    logged_out_time = models.DateTimeField(blank = False,null=True)
    is_logged_in = models.BooleanField(default = False)

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a Token instance for any User instance created."""
    if created:
        Token.objects.get_or_create(user=instance)

class InvitationStatus(models.Model):
    invitation_status = models.CharField(max_length=100, blank=False)

class InviteUser(models.Model):
    # Invitation should expired after 48 hours and give user option to again resend invitation #
    invitiation_sender = models.ForeignKey(User, models.CASCADE, related_name='invitiation_sender')
    invitatation_sent_date = models.DateTimeField(auto_now_add=True)
    invitatation_acceptance_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    invitiation_receiver = models.ForeignKey(User, models.CASCADE, related_name='invitiation_receiver')
    invitation_status = models.ForeignKey(InvitationStatus, models.CASCADE)
    is_invitation_accepted = models.BooleanField(default=False)
    is_invitation_expired = models.BooleanField(default=False)
    invitation_link = models.CharField(max_length=1000, blank=True)
    invitation_token = models.CharField(max_length=1000, blank=True)
    dataroom_invitation = models.IntegerField(blank=True, null=True)
    is_shifted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        from users_and_permission.models import DataroomMembers
        if self.is_invitation_accepted==True:
            # print('coming here!!!!!!!!!!!!!!!!!!!!!!!')
            DataroomMembers.objects.filter(dataroom_id=self.dataroom_invitation,member_id=self.invitiation_receiver,member_added_by_id=self.invitiation_sender,is_deleted=False).update(memberactivestatus=True)

        super(InviteUser, self).save(*args, **kwargs)     






from users_and_permission.models import DataroomGroups
from dataroom.models import Dataroom
class pendinginvitations(models.Model):
    dataroom=models.ForeignKey(Dataroom, models.CASCADE, null=True,blank=True)
    senderuser=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    email=models.CharField(max_length=1000, blank=True,null=True)
    dataroom_group = models.ForeignKey(DataroomGroups, models.CASCADE, null=True, blank=True)
    first_name=models.CharField(max_length=1000, blank=True,null=True)
    last_name=models.CharField(max_length=1000, blank=True,null=True)
    is_end_user=models.BooleanField(default=False)
    emailsendflag=models.BooleanField(default=False)
    is_la_user=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)

class plansfeature(models.Model):
    heading=models.CharField(max_length=1000, blank=True,null=True)
    title=models.CharField(max_length=1000, blank=True,null=True)
    desciption=RichTextField(config_name='default', blank=True, null=True, help_text="Please fill this field")
    created_date = models.DateTimeField(auto_now_add=True)



class subscriptionplan(models.Model):
    name=models.CharField(max_length=1000, blank=True,null=True)
    features=models.ForeignKey(plansfeature, models.CASCADE, null=True,blank=True)
    storage =models.IntegerField(blank=True, null=True)
    datarooms =models.IntegerField(blank=True, null=True)
    users=models.CharField(max_length=1000, blank=True,null=True)
    term=models.CharField(max_length=1000, blank=True,null=True)
    cost=models.IntegerField(blank=True, null=True)
    planstatus=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)



class addon_plans(models.Model):
    name=models.CharField(max_length=1000, blank=True,null=True)
    storage =models.IntegerField(blank=True, null=True)
    datarooms =models.IntegerField(blank=True, null=True)
    users=models.CharField(max_length=1000, blank=True,null=True)
    term=models.CharField(max_length=1000, blank=True,null=True)
    cost=models.IntegerField(blank=True, null=True)
    planstatus=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)


class dvd_addon_plans(models.Model):
    name=models.CharField(max_length=1000, blank=True,null=True)
    hardware_medium=models.CharField(max_length=1000, blank=True,null=True)
    cost=models.IntegerField(blank=True, null=True)
    planstatus=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

dvd_addon_status=(
                    ("Processing","Processing"),
                    ("Shipped","Shipped"),
                    ("Delivered","Delivered"),
                    )

class dvd_addon_invoiceuserwise(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    dvd_addon_plan=models.ForeignKey(dvd_addon_plans, models.CASCADE,null=True,blank=True)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    quantity=models.IntegerField(blank=True, null=True)
    total_cost=models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length = 50,choices = dvd_addon_status,default = 'Processing')    
    is_calceled=models.BooleanField(default=False)
    is_payment_done=models.BooleanField(default=False)
    ccavenue_cartid=models.CharField(max_length=1000, blank=True,null=True)
    planid=models.CharField(max_length=1000, blank=True,null=True)


class addon_plan_tempforsameday(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    addon_plan=models.ForeignKey(addon_plans, models.CASCADE,null=True,blank=True)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    start_date=models.DateTimeField(blank=True,null=True)
    end_date=models.DateTimeField(blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    is_plan_active=models.BooleanField(default=False)
    user_undo_upload=models.BooleanField(default=False)
    invoice_generated=models.BooleanField(default=False)
    entry_used=models.BooleanField(default=False)


class addon_plan_invoiceuserwise(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    addon_plan=models.ForeignKey(addon_plans, models.CASCADE,null=True,blank=True)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    start_date=models.DateTimeField(blank=True,null=True)
    end_date=models.DateTimeField(blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    is_plan_active=models.BooleanField(default=False)
    ccavenue_cartid=models.CharField(max_length=1000, blank=True,null=True)
    quantity=models.IntegerField(blank=True, null=True)
    is_renewal=models.BooleanField(default=False)
    planid=models.CharField(max_length=1000, blank=True,null=True)
    total_cost=models.IntegerField(blank=True, null=True)
    is_payment_done=models.BooleanField(default=False)
    paid_at=models.DateTimeField(blank=True,null=True)


class planinvoiceuserwise(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    plan=models.ForeignKey(subscriptionplan, models.CASCADE,null=True,blank=True)
    dataroom=models.ForeignKey(Dataroom, models.CASCADE,null=True,blank=True)
    addon_plans=models.ManyToManyField(addon_plan_invoiceuserwise, blank=True)
    dvd_addon_plans=models.ManyToManyField(dvd_addon_invoiceuserwise, blank=True)
    project_name=models.CharField(max_length=1000, blank=True,null=True)
    selected_plan=models.CharField(max_length=1000, blank=True,null=True)
    edition=models.CharField(max_length=1000, blank=True,null=True)
    select_billing_term=models.CharField(max_length=1000, blank=True,null=True)
    customer_name=models.CharField(max_length=1000, blank=True,null=True)
    company_name=models.CharField(max_length=1000, blank=True,null=True)    
    billing_address=models.CharField(max_length=1000, blank=True,null=True)
    billing_city=models.CharField(max_length=1000, blank=True,null=True)
    billing_state=models.CharField(max_length=1000, blank=True,null=True)
    billing_country=models.CharField(max_length=1000, blank=True,null=True)
    po_box=models.CharField(max_length=1000, blank=True,null=True)
    effective_price=models.CharField(max_length=1000, blank=True,null=True)
    total_fee=models.CharField(max_length=1000, blank=True,null=True)
    vat=models.CharField(max_length=1000, blank=True,null=True)
    grand_total=models.CharField(max_length=1000, blank=True,null=True)
    payment_option=models.CharField(max_length=1000, blank=True,null=True)
    payment_complete=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    start_date=models.DateTimeField(blank=True,null=True)
    end_date=models.DateTimeField(blank=True,null=True)
    is_plan_active=models.BooleanField(default=False)
    auto_renewal=models.BooleanField(default=False)
    plan_renewed=models.BooleanField(default=False)
    new_invoiceid=models.CharField(max_length=1000, blank=True,null=True)
    cancel_at_monthend=models.BooleanField(default=False)
    is_plan_upgraded=models.BooleanField(default=False)
    is_latest_invoice=models.BooleanField(default=True)
    is_expired=models.BooleanField(default=False)
    ccavenue_cartid=models.CharField(max_length=1000,blank=True,null=True)
    is_cancelled=models.BooleanField(default=False)
    cancel_at=models.DateTimeField(blank=True,null=True)
    paid_at=models.DateTimeField(blank=True,null=True)




class ccavenue_payment_cartids(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    is_new_plan=models.BooleanField(default=False)
    is_DVD_addon=models.BooleanField(default=False)
    is_storage_addon=models.BooleanField(default=False)
    is_renewal=models.BooleanField(default=False)
    new_plan=models.ForeignKey(planinvoiceuserwise, models.CASCADE,null=True,blank=True)
    dvd_plan=models.ForeignKey(dvd_addon_invoiceuserwise, models.CASCADE,null=True,blank=True)
    storage_addon=models.ForeignKey(addon_plan_invoiceuserwise, models.CASCADE,null=True,blank=True)
    ref_id=models.CharField(max_length=1000, blank=True,null=True)
    si_ref_id=models.CharField(max_length=1000, blank=True,null=True)
    bank_ref_id=models.CharField(max_length=500, blank=True,null=True)
    receipt_no=models.CharField(max_length=1000, blank=True,null=True)
    bank_mid=models.CharField(max_length=1000, blank=True,null=True)
    is_payment_done=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)



# class otp_model( models.Model):
#     dataroom = models.ForeignKey(Dataroom, models.CASCADE, null=True,blank=True)
#     user = models.ForeignKey(User, models.CASCADE, related_name='user_otp')
#     otp = models.IntegerField(default=0)
#     created = models.DateTimeField(auto_now_add=True)
#     is_verifed = models.BooleanField(default=False)


class TimeZonesList(models.Model):
    country_code=models.CharField(max_length=100,null=True,blank=True)
    country=models.CharField(max_length=100,null=True,blank=True)
    tz=models.CharField(max_length=100,null=True,blank=True)
    offset=models.CharField(max_length=100,null=True,blank=True)
    abbreviation=models.CharField(max_length=50,null=True,blank=True)




class User_time_zone(models.Model):
    user=models.ForeignKey(User, models.CASCADE,null=True,blank=True)
    time_zone=models.ForeignKey(TimeZonesList, models.CASCADE,null=True,blank=True)
