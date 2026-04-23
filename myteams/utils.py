from dataroom.models import Dataroom,DataroomDisclaimer
from Vote.models import Vote
from data_documents.models import DataroomFolder
from django.db.models import Sum
from datetime import timedelta,datetime
# from .models import *


def storage_used(data):
	for i in data:
		dataroomId = i['dataroom']['id']
		vote_consumed = round((Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		dataroom_total_size=dataroom_consumed + disclaimer_consumed + vote_consumed
		i['dataroom_consumed']=round((dataroom_total_size/1024),2)
	return data

def storage_usedforteams(data):
	for i in data:
			dataroomId = Dataroom.objects.filter(my_team_id=i['id'])

			if dataroomId.exists():
				dataroomId=dataroomId.last().id
				vote_consumed = round((Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
				disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
				dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
				dataroom_total_size=dataroom_consumed + disclaimer_consumed + vote_consumed
				i['dataroom_consumed']=dataroom_total_size/1024
				i['dataroom_storage_allocated']=i['dataroom_storage_allowed']
			else:
				i['dataroom_consumed']=00


	return data

def storage_usedfordataroom(data):
	for i in data:
		dataroomId = i['id']
		vote_consumed = round((Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=dataroomId,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=dataroomId).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=dataroomId, is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
		dataroom_total_size=dataroom_consumed + disclaimer_consumed + vote_consumed
		i['dataroom_consumed']=dataroom_total_size/1024
	return data

def calculatedeletedate(data):
	for i in data:
		i['dataroomdeletiondate']=''


		if (i['is_plan_active']==False and i['is_latest_invoice']==True and i['dataroom']['is_expired']==True):
			if i['end_date']:
				try:
					dateobject=datetime.strptime(str(str(i['end_date'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')+timedelta(days=15)
				except:
					dateobject=datetime.strptime(str(str(i['end_date'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')+timedelta(days=15)

				i['dataroomdeletiondate']=dateobject.strftime("%d-%m-%Y %H:%M")

		if (i['is_cancelled']==True and i['is_latest_invoice']==True and i['is_plan_active']==False):
			if i['cancel_at']:
				try:
					dateobject=datetime.strptime(str(str(i['cancel_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')+timedelta(days=15)
				except:
					dateobject=datetime.strptime(str(str(i['cancel_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')+timedelta(days=15)

				i['dataroomdeletiondate']=dateobject.strftime("%d-%m-%Y %H:%M")

		if (i['dataroom']['is_request_for_deletion']==True and i['is_latest_invoice']==True):
			if i['dataroom']['delete_request_at']:
				try:
					dateobject=datetime.strptime(str(str(i['dataroom']['delete_request_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')+timedelta(days=15)
				except:
					dateobject=datetime.strptime(str(str(i['dataroom']['delete_request_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')+timedelta(days=15)

				i['dataroomdeletiondate']=dateobject.strftime("%d-%m-%Y %H:%M")
				try:	
					dateobject1=datetime.strptime(str(str(i['dataroom']['delete_request_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
				except:
					dateobject1=datetime.strptime(str(str(i['dataroom']['delete_request_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
				i['dataroom']['delete_request_at']=dateobject1.strftime("%d-%m-%Y %H:%M")
		if i['dataroom']['is_deleted']==True:
			if i['dataroom']['delete_at']:
				try:
					dateobject=datetime.strptime(str(str(i['dataroom']['delete_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
				except:
					dateobject=datetime.strptime(str(str(i['dataroom']['delete_at'])).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')

				i['dataroomdeletiondate']=dateobject.strftime(" %d-%m-%Y  %H:%M")		

	return data