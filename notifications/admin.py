from django.contrib import admin
from .models import Message, AllNotifications


# admin.site.register(Message,)

class AllNotificationsAdmin(admin.ModelAdmin):
    model = AllNotifications
    
    list_display = ('id',)



admin.site.register(AllNotifications,AllNotificationsAdmin)