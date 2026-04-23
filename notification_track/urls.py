from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^projectName/get_dataroom_notification_count/(?P<pk>[0-9]+)/$', GetDataroomNotificationCount.as_view()),
    url(r'^projectName/get_dataroom_notification/(?P<pk>[0-9]+)/$', GetDataroomNotification.as_view()),    
    url(r'^projectName/get_all_notification/$', GetAllNotification.as_view()),    

]
