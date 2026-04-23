from django.contrib import admin
from .models import *

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'support_email_id', 'help_email_id', 'phone_no')

class EmailerTypeAdmin(admin.ModelAdmin):
    list_display = ('id','emailer_type', )

class EmailerAdmin(admin.ModelAdmin):
	list_display = ('from_email', 'subject', 'body_html', 'to_email', 'email_sent_date')

admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(EmailerType, EmailerTypeAdmin)
admin.site.register(Emailer, EmailerAdmin)
# Register your models here.
