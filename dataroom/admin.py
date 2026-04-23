# # Register your models here.
from django.contrib import admin
from .models import *
import csv
from django.http import HttpResponse
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.contrib.admin import DateFieldListFilter


def export_as_csv(self, request, queryset):

    exclude_list = ['expiry_date','is_paid','is_expired','dataroom_logo','dataroom_nameFront','account_level_branding','dataroom_modules','is_dataroom_on_live','is_dataroom_cloned','is_request_for_deletion','is_request_for_archive','dataroom_cloned_from','my_team','event','event_timestamp']
    meta = self.model._meta
    field_names = [field.name for field in meta.fields if field.name not in exclude_list]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)
    new_queryset = Dataroom.objects.all()

    writer.writerow(field_names)
    for obj in new_queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


class DataroomAdmin(admin.ModelAdmin):
    model = Dataroom
    list_display = ('id','dataroom_name','dataroom_nameFront')
    list_filter = ('dataroom_name','dataroom_logo',('created_date', DateRangeFilter))
    # fields = ('__all__',)
    search_fields = ['user__first_name','user__email','my_team__user__email','my_team__user__first_name']
    actions = [export_as_csv]
    date_hierarchy = 'created_date'

admin.site.register(Dataroom, DataroomAdmin)
admin.site.register(DataroomOverview)
admin.site.register(DataroomDisclaimer)
# admin.site.register(Dataroom)


# # Register your models here.
# from django.contrib import admin
# from .models import *
# from import_export.admin import ImportExportActionModelAdmin


# class CustomLinkInline(admin.TabularInline):
#     model = CustomLink
#     fields = ['link_title', 'link']
#     extra = 1
#     sortable = 'order'
#     suit_classes = 'suit-tab suit-tab-custom_link'


# class SetVideoInline(admin.TabularInline):
#     model = SetVideo
#     fields = ['current_video', 'auto_playing']
#     extra = 1
#     sortable = 'order'
#     suit_classes = 'suit-tab suit-tab-set_overview_video'


# class DisclaimerInline(admin.TabularInline):
#     model = Disclaimer
#     fields = [('accept_disclaimer', 'disclaimer')]
#     extra = 1
#     sortable = 'order'
#     suit_classes = 'suit-tab suit-tab-workspace_disclaimers'


# class DataroomOverviewAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
#     model = DataroomOverview
#     list_display = ('user', 'workspace_name', 'send_notification_members', 'use_file_workshop_home', 'hide_file_index_admin')

#     inlines = (CustomLinkInline, SetVideoInline, DisclaimerInline)

#     fieldsets = [
#         (None, {
#             'classes': ('suit-tab suit-tab-workspace',),
#             'fields': ['user', 'workspace_name', 'send_notification_members', 'use_file_workshop_home', 'hide_file_index_admin']
#         }),
#         (None, {
#             'classes': ('suit-tab suit-tab-custom_overview_text',),
#             'fields': ['heading', 'description']
#         }),
#         (None, {
#             'classes': ('suit-tab suit-tab-logo',),
#             'fields': ['logo',]
#         }),
#     ]

#     suit_form_tabs = (('workspace', 'Workspace'), ('logo', 'Workspace Logo'), ('custom_overview_text', 'Custom Overview Text'), ('custom_link', 'Custom Link'), ('set_overview_video', 'Set Overview Video'), ('workspace_disclaimers', 'Workspace Disclaimers'))


# # Register your models here.
# admin.site.register(DataroomModules,)
# admin.site.register(DataroomStage,)
# admin.site.register(Dataroom,)
# admin.site.register(DataroomOverview, DataroomOverviewAdmin)
# # admin.site.register(CustomLink,)
# # admin.site.register(SetVideo,)
# # admin.site.register(PriviewStatus,)
# # admin.site.register(Disclaimer,)