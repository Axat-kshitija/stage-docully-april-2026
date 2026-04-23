from azure.storage.blob import BlockBlobService,PublicAccess
from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids,pendinginvitations
from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime,date,time
from django.utils import timezone
from .utils import send_mail_to_superadmin,send_dataroomdelete_email,send_markedfordeletion_email,send_accessrevoked_email,send_offlinedataroomdelete_email
from Vote.models import Vote
from notifications.models import AllNotifications,Notifications
from users_and_permission.models import DataroomGroups,DataroomMembers,DataroomGroupPermission
import os
from dms.settings import *
 


def dataroom_deletion_job():
				print('cpming here rr',datetime.now())
				# fifteen_end_date=datetime.now() - timedelta(days=15)
				fifteen_end_date=datetime.combine(date.today(),time(23, 59))+timedelta(days=15)
				if planinvoiceuserwise.objects.filter(cancel_at__lte=fifteen_end_date,is_latest_invoice=True,is_plan_active=False,is_expired=False,is_cancelled=True).exists():
					plandata1=planinvoiceuserwise.objects.filter(cancel_at__lte=fifteen_end_date,is_latest_invoice=True,is_plan_active=False,is_expired=False,is_cancelled=True)
					for k in plandata1:
						planinvoiceuserwise.objects.filter(id=k.id).update(is_expired=True)
						Dataroom.objects.filter(id=k.dataroom.id).update(is_deleted=True,delete_at=datetime.now())
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=k.dataroom.id).update(is_deleted=True,deleted_by_date=datetime.now(),is_deleted_permanent=True)
						if DataroomFolder.objects.filter(dataroom_id=k.dataroom.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=k.dataroom.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=k.dataroom.id).exists():
							data=Vote.objects.filter(dataroom_id=k.dataroom.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=k.dataroom.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=k.dataroom.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)						
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(k.dataroom.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(k.dataroom.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(k.dataroom.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(k.dataroom.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(k.dataroom.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(k.dataroom.id)+".pdf")	

						DataroomFolder.objects.filter(dataroom_id=k.dataroom.id).delete()
						AllNotifications.objects.filter(dataroom_id=k.dataroom.id).delete()
						Notifications.objects.filter(dataroom_id=k.dataroom.id).delete()				
						Watermarking.objects.filter(dataroom_id=k.dataroom.id).delete()
						pendinginvitations.objects.filter(dataroom_id=k.dataroom.id).delete()
						DataroomGroups.objects.filter(dataroom_id=k.dataroom.id).delete()
						DataroomMembers.objects.filter(dataroom_id=k.dataroom.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=k.dataroom.id).delete()
						Vote.objects.filter(dataroom_id=k.dataroom.id).delete()						
						send_dataroomdelete_email(subject= 'Deletion Notice – Docully Subscription for Project '+str(k.dataroom.dataroom_nameFront)+' has been Deleted', to = str(k.user.email), first_name = k.user.first_name, data =k,projectname=k.dataroom.dataroom_nameFront,user=k.user)		

				thirty_end_date=datetime.combine(date.today(),time(23, 59))+timedelta(days=15)
				if planinvoiceuserwise.objects.filter(end_date__lte=thirty_end_date,is_latest_invoice=True,is_plan_active=False,is_expired=False,is_cancelled=False).exists():
					plandata1=planinvoiceuserwise.objects.filter(end_date__lte=thirty_end_date,is_latest_invoice=True,is_plan_active=False,is_expired=False,is_cancelled=False)
					for l in plandata1:
						planinvoiceuserwise.objects.filter(id=l.id).update(is_expired=True)
						Dataroom.objects.filter(id=l.dataroom.id).update(is_deleted=True,delete_at=datetime.now())
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=l.dataroom.id).update(is_deleted=True,deleted_by_date=datetime.now(),is_deleted_permanent=True)
						if 	DataroomFolder.objects.filter(dataroom_id=l.dataroom.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=l.dataroom.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=l.dataroom.id).exists():
							data=Vote.objects.filter(dataroom_id=l.dataroom.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=l.dataroom.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=l.dataroom.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)							
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.dataroom.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.dataroom.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.dataroom.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.dataroom.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.dataroom.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.dataroom.id)+".pdf")	
						DataroomFolder.objects.filter(dataroom_id=l.dataroom.id).delete()
						AllNotifications.objects.filter(dataroom_id=l.dataroom.id).delete()
						Notifications.objects.filter(dataroom_id=l.dataroom.id).delete()	
						Watermarking.objects.filter(dataroom_id=l.dataroom.id).delete()
						pendinginvitations.objects.filter(dataroom_id=l.dataroom.id).delete()
						DataroomGroups.objects.filter(dataroom_id=l.dataroom.id).delete()
						DataroomMembers.objects.filter(dataroom_id=l.dataroom.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=l.dataroom.id).delete()
						Vote.objects.filter(dataroom_id=l.dataroom.id).delete()						
						send_dataroomdelete_email(subject= 'Deletion Notice – Docully Subscription for Project '+str(l.dataroom.dataroom_nameFront)+' has been Deleted', to = str(l.user.email), first_name = l.user.first_name, data =l,projectname=l.dataroom.dataroom_nameFront,user=l.user)		



				if Dataroom.objects.filter(delete_request_at__lte=thirty_end_date,offlinedataroom=True,is_deleted=False,is_request_for_deletion=True).exists():
					plandata1=Dataroom.objects.filter(delete_request_at__lte=thirty_end_date,is_deleted=False,offlinedataroom=True,is_request_for_deletion=True)
					for l in plandata1:
						Dataroom.objects.filter(id=l.id).update(is_deleted=True,delete_at=datetime.now(),is_expired=True)
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=l.id).update(is_deleted=True,deleted_by_date=datetime.now(),is_deleted_permanent=True)
						if 	DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=l.id).exists():
							data=Vote.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=l.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)							
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf")	
						DataroomFolder.objects.filter(dataroom_id=l.id).delete()
						AllNotifications.objects.filter(dataroom_id=l.id).delete()
						Notifications.objects.filter(dataroom_id=l.id).delete()	
						Watermarking.objects.filter(dataroom_id=l.id).delete()
						pendinginvitations.objects.filter(dataroom_id=l.id).delete()
						DataroomGroups.objects.filter(dataroom_id=l.id).delete()
						DataroomMembers.objects.filter(dataroom_id=l.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=l.id).delete()
						Vote.objects.filter(dataroom_id=l.id).delete()						
						send_offlinedataroomdelete_email(subject= 'Deletion Notice – Docully Project '+str(l.dataroom_nameFront)+' has been Deleted', to = str(l.user.email), first_name = l.user.first_name,projectname=l.dataroom_nameFront)		
