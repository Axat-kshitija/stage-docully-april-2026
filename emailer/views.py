from django.shortcuts import render
from django.http import HttpResponse
from .models import SiteSettings
from . import utils
# Create your views here.
def request_for_deletion(request):
	utils.send_deletion_dataroom_email()
	site_setting = SiteSettings.objects.get(id=1)
	# print ("site site_setting", site_setting)
	context = {
    	'first_name': "Dhananjay", 
    	'site_setting': site_setting
    }
	return render(request, 'emailer/request_for_delation.html', context)


#request_for_archive

def request_for_archive(request):
    site_setting = SiteSettings.objects.get(id=1)
    # print ("site site_setting", site_setting)
    context = {
    	'first_name': "Dhananjay", 
    	'site_setting': site_setting
    }
    return render(request, 'emailer/request_for_archive.html', context)