"""dms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#from jet_django.urls import jet_urls
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


import debug_toolbar 

urlpatterns = [
 #   url(r'^jet_api/', include(jet_urls)),
    url(r'^projectName/admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^', include('userauth.urls')),
    url(r'^', include('dataroom.urls')),
    url(r'^', include('emailer.urls')),
    url(r'^', include('myteams.urls')),
    url(r'^', include('data_documents.urls')), 
    url(r'^', include('users_and_permission.urls')),
    url(r'^', include('qna.urls')),
    url(r'^', include('notifications.urls')),
    url(r'^', include('Vote.urls')),
    url(r'^', include('notification_track.urls')),

   # url(r'^__debug__/', include(debug_toolbar.urls)),

    # url(r'^swagger/', include('rest_framework_docs.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.MEDIA_URL1, document_root=settings.MEDIA_ROOT1) + static(settings.WATERMARK_URL, document_root=settings.WATERMARK_ROOT) + static(settings.STATIC_URL2, document_root=settings.STATIC_ROOT2)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns




# handler404 = 'data_documents.views.error_404'
# handler500 = 'data_documents.views.error_500'
# handler403 = 'data_documents.views.error_403'
# handler400 = 'data_documents.views.error_400'
# handler401 = 'data_documents.views.error_401'