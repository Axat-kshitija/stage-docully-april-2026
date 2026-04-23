from django.core.management import BaseCommand
from os import path
import json

from userauth.models import InvitationStatus, EndUserType
from dataroom.models import DataroomStage, DataroomDisclaimerPreviewStatus
from emailer.models import SiteSettings, EmailerType
from constants import constants
# The class must be named Command, and subclass BaseCommand11
class Command(BaseCommand):
    # Show this when the user types help
    help = "Populate initial database"
    dataroom_stages = constants.dataroom_stages
    site_settings = constants.site_settings
    emailer_types = constants.emailer_types
    all_invitation_status = constants.invitation_status
    dataroom_disclaimer_status = constants.dataroom_disclaimer_status
    end_user_types = constants.end_user_types

    def handle(self, *args, **options):
        self.stdout.write("Loading initial records")    
        self.load_dataroom_stages()
        self.add_site_settings_data()
        self.emailer_type()
        self.load_all_invitation_status()
        self.load_disclaimer_status()
        self.load_end_user_types()

    def load_dataroom_stages(self):
      print ("load dataroom method called")
      print ("dataroom stages are ", self.dataroom_stages)
      DataroomStage.objects.all().delete()
      for stages in self.dataroom_stages:
          dataroom = DataroomStage()
          dataroom.dataroom_stage = stages
          dataroom.save()

      print ("Dataroom status is successfully stored")

    def add_site_settings_data(self):
      print ("add site settings data")
      site_setting = SiteSettings()
      site_setting.domain_name = self.site_settings["domain_name"]
      site_setting.domain_url = self.site_settings['domain_url']
      site_setting.support_email_id = self.site_settings["support_email_id"]
      site_setting.help_email_id = self.site_settings["help_email_id"]
      site_setting.phone_no = self.site_settings["phone_no"]
      site_setting.save()

    def emailer_type(self):
      print ("emialer type")
      for emailer in self.emailer_types:
        emailer_ty = EmailerType()
        emailer_ty.emailer_type = emailer
        emailer_ty.save()

    def load_all_invitation_status(self):
        for invite in self.all_invitation_status:
          invitation = InvitationStatus()
          invitation.invitation_status = invite
          invitation.save()


    def load_disclaimer_status(self):
      for disclaimer in self.dataroom_disclaimer_status:
        disclaimer_status = DataroomDisclaimerPreviewStatus()
        disclaimer_status.dataroom_disclaimer_status = disclaimer
        disclaimer_status.save()


    def load_end_user_types(self):
      print ("load end user types")
      for end_user in self.end_user_types:
          new_end_user = EndUserType()
          new_end_user.end_user_types = end_user
          new_end_user.save()


    def load_data(self, *x):
        local_path = path.join(path.dirname(path.realpath(__file__)), *x)
        with open(local_path) as data_file:
            result = json.load(data_file)
        return result
