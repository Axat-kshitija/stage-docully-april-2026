from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(BulkActivityTracker)


class DataroomFolderAdmin(admin.ModelAdmin):
    model = DataroomFolder
    
    list_display = ('id','created_date','name','dataroom','dataroom_id','is_deleted','deleted_by','parent_folder__name','is_root_folder','permanent_deleted_by','is_deleted_permanent')

    def parent_folder__name(self, obj):
        if obj.parent_folder:
            return obj.parent_folder.name
        else:
            None

    list_filter = ('dataroom_id',)

    # fields = ('__all__',)
    search_fields = ['dataroom__dataroom_name','name','id']
    # actions = [export_as_csv]
    # date_hierarchy = 'created_date'

admin.site.register(DataroomFolder,DataroomFolderAdmin)

# admin.site.register(dataroomactivitymerge)
admin.site.register(Bulkuploadstatus)
admin.site.register(FolderDeleteDownload)
admin.site.register(FolderTrash)