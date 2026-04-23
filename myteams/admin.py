from django.contrib import admin
from .models import *
import csv
from django.http import HttpResponse
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.contrib.admin import DateFieldListFilter


def export_as_csv(self, request, queryset):

    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    new_queryset = MyTeams.objects.all()
    writer.writerow(field_names)
    for obj in new_queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


class MyTeamsAdmin(admin.ModelAdmin):
    model = MyTeams
    list_display = ('team_created_at','team_name', 'dataroom_allowed', 'dataroom_admin_allowed')
    date_hierarchy = 'team_created_at'
    list_filter = ('user',('team_created_at', DateRangeFilter))
    search_fields = ['user__first_name','user__email']


    actions = [export_as_csv]


# Register your models here.
admin.site.register(MyTeams, MyTeamsAdmin) 

