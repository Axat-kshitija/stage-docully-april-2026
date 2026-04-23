from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^projectName/send_message/(?P<pk>[0-9]+)/$', SendMessage.as_view()),
    url(r'^projectName/send_message_to_user/$', SendMessageToUser.as_view()),
    url(r'^projectName/get_dataroom_message/(?P<pk>[0-9]+)/$', GetDataroomMessage.as_view()),
    url(r'^projectName/chat_message_list/(?P<pk>[0-9]+)/$', ChatMessageList.as_view()),
    # url(r'^subject_list/(?P<pk>[0-9]+)/$', SubjectList.as_view()),

    # url(r'^get_dataroom_notification/(?P<pk>[0-9]+)/$', GetDataroomNotification.as_view()),    
]

