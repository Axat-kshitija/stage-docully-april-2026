from django.conf.urls import url
from . import views 


urlpatterns = [
    url('projectName/request_for_deletion', views.request_for_deletion, name='request_for_deletion'),
    url('projectName/request_for_archive', views.request_for_archive, name='request_for_archive'),

]
