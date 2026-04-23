from django.contrib import admin
from .models import *

# Register your models here.
class DataroomMembersAdmin(admin.ModelAdmin):
    # list_display = ('days','start_date', 'end_date', 'is_active', 'user')
    # fields = ('days', 'last_name')
    search_fields = ['member__email','dataroom__id']

# admin.site.register(PaidDays, PaidDaysAdmin)

# admin.site.register(DataroomGroups,)
admin.site.register(DataroomMembers,DataroomMembersAdmin)
# admin.site.register(DataroomGroupPermission,)
# admin.site.register(DataroomMemberInvitation,)
# admin.site.register(DataroomGroupFolderSpecificPermissions,)
