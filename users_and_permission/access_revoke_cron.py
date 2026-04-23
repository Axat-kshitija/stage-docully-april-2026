from .models import DataroomGroups, DataroomGroupPermission, DataroomGroupFolderSpecificPermissions, DataroomMembers
from datetime import timedelta,datetime

def permisionrevoke_job():
	start_datee = datetime.now()
	DataroomGroups.objects.filter(access_revoke__lte=start_datee,is_active=True).update(is_active=False)
	DataroomGroupFolderSpecificPermissions.objects.filter(access_revoke__lte=start_datee).update(is_no_access=True,is_access=False,is_view_only=False,is_view_and_print=False,is_view_and_print_and_download=False,is_upload=False,is_watermarking=False,is_drm=False,is_editor=False,is_shortcut=False)
	print('cron working 001')