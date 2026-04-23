# # Register your models here.
from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
import csv
from django.http import HttpResponse
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.contrib.admin import DateFieldListFilter

# from rest_framework.authtoken.models import Token

# class SomeModelAdmin(admin.ModelAdmin):
#     def admin_action(self, request, queryset):

# actions = ["export_as_csv"]

# def export_as_csv(self, request, queryset):
#     pass

# export_as_csv.short_description = "Export Selected"




def response_action(self, request, queryset):
    # override to allow for exporting of ALL records to CSV if no chkbox selected
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    if request.META['QUERY_STRING']:
        qd = dictify_querystring(request.META['QUERY_STRING'])
    else:
        qd = None
    data = request.POST.copy()
    if len(selected) == 0 and data['action'] in ('export_to_csv', 'extended_export_to_csv'):
        ct = ContentType.objects.get_for_model(queryset.model)
        klass = ct.model_class()
        if qd:
            queryset = klass.objects.filter(**qd)[:65535] # cap at classic Excel maximum minus 1 row for headers
        else:
            queryset = klass.objects.all()[:65535] # cap at classic Excel maximum minus 1 row for headers
        return getattr(self, data['action'])(request, queryset)
    else:
        return super(ModelAdminCSV, self).response_action(request, queryset)


def export_as_csv(self, request, queryset):

    exclude_list = ['avatar','id','last_login','username','receive_emai','password','is_superuser','is_subscriber','is_end_user','is_team','is_team_member','is_developer','is_icon_downloaded','is_staff','agree','receive_email']
    meta = self.model._meta
    field_names = [field.name for field in meta.fields if field.name not in exclude_list]
    new_queryset = User.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in new_queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

# export_as_csv.short_description = "Act on all %(verbose_name_plural)s"
export_as_csv.acts_on_all = True

class CustomLinkInline(admin.TabularInline):
    model = Role
    fields = ['id']
    suit_classes = 'suit-tab suit-tab-custom_link'


class UserAdmin(admin.ModelAdmin):
    list_filter = ('first_name','last_name', 'email',('date_joined', DateRangeFilter))
    list_display = ('date_joined','first_name','last_name', 'email',)
    search_fields = ['email','first_name']
    date_hierarchy = 'date_joined'
    actions = [export_as_csv]

class planinvoiceuserwiseAdmin(admin.ModelAdmin):
    search_fields = ['dataroom__dataroom_nameFront','dataroom__id']

class ccavenue_payment_cartidsAdmin(admin.ModelAdmin):
    search_fields = ['user__email','new_plan__id','ref_id']


class AccessHistoryAdmin(admin.ModelAdmin):
    # list_filter = ('first_name','last_name', 'email',('date_joined', DateRangeFilter))
    list_display = ('user','logged_in_ip','logged_in_time', 'logged_out_time','is_logged_in')

class TimeZonesListAdmin(admin.ModelAdmin):
    # list_filter = ('first_name','last_name', 'email',('date_joined', DateRangeFilter))
    list_display = ('country_code','country','tz', 'offset','abbreviation')

admin.site.register(TimeZonesList,TimeZonesListAdmin)



# admin.site.unregister(Token)
admin.site.unregister(Group)
# admin.site.register(User)
admin.site.register(User, UserAdmin)
admin.site.register(subscriptionplan)
admin.site.register(plansfeature)
admin.site.register(addon_plans)
admin.site.register(planinvoiceuserwise,planinvoiceuserwiseAdmin)
admin.site.register(ccavenue_payment_cartids,ccavenue_payment_cartidsAdmin)
admin.site.register(addon_plan_invoiceuserwise)
admin.site.register(addon_plan_tempforsameday)
admin.site.register(dvd_addon_plans)
admin.site.register(dvd_addon_invoiceuserwise)
admin.site.register(AccessHistory,AccessHistoryAdmin)
admin.site.register(Captcha_model)

admin.site.register(User_time_zone)


