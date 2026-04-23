from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids
from dataroom.models import Dataroom,DataroomDisclaimer
from Vote.models import Vote
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime
from django.utils import timezone
from django.db.models import F
from .utils import send_mail_to_superadmin
from django.db.models import Count, Min, Sum, Avg
import requests
from .ccavutil import encrypt,decrypt
import json


def daily_addon_invoice_job():
		print('r','111111111111111')
		if addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False).exists():	
			print('r','22222222222')
		
			tempaddon_data=addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False)

			for i in tempaddon_data:
				print('r','3333333333333333333')
	
				try:
					print('r','444444444444')

					disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)

					dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=i.dataroom.id,is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=i.dataroom.id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
					vote_consumed = round((Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
					
					total_consumed=vote_consumed + disclaimer_consumed + dataroom_consumed
					dataroomsize=Dataroom.objects.filter(id=i.dataroom.id).first().dataroom_storage_allocated * 1024
					if total_consumed > dataroomsize: 
						print('r','5555555555')

						extrasize=int(total_consumed)-int(dataroomsize)
						addon_storage=int(i.addon_plan.storage)*1024
						if int(extrasize/addon_storage)<(extrasize/addon_storage):
							addonsneed=int(extrasize/addon_storage)+1
						else:
							addonsneed=int(extrasize/addon_storage)
						print(extrasize,addonsneed,addon_storage)
						# for j in range(0,addonsneed):
						plandata1=planinvoiceuserwise.objects.filter(dataroom_id=i.dataroom.id,is_latest_invoice=True,is_expired=False).first()  

						ccavenue_data=ccavenue_payment_cartids.objects.filter(new_plan_id=plandata1.id).first()

						obj3=ccavenue_payment_cartids()
						obj3.user_id=i.user.id
						obj3.is_storage_addon=True
						obj3.save()


						access_code='AVXY03ID76AY64YXYA'
						workingKey='94DEDF16E45876158DCC2ADDF67BC754'
						amountt=int(i.addon_plan.cost)*3.67*int(addonsneed)
						merchant_data1='{"si_sub_ref_no":"'+str(ccavenue_data.si_ref_id)+'","si_mer_charge_ref_no":"'+str(obj3.id)+'","si_amount":"3.67","si_currency":"AED"}'

						encryption = encrypt(merchant_data1,workingKey)
						newurl="https://login.ccavenue.ae/apis/servlet/DoWebTrans?enc_request="+encryption+"&access_code=AVXY03ID76AY64YXYA&request_type=JSON&command=chargeSI&version=1.1&si_sub_ref_no="+str(ccavenue_data.si_ref_id)+"&si_mer_charge_ref_no="+str(obj3.id)+"&si_currency=AED&si_amount=3.67"
						datart=requests.post(newurl)
						responsedata=str(datart.text)
						responsedata=responsedata.replace('status','').replace('enc_response','').replace("\r",'').replace('\n','').replace('=','')	
						responsedata=responsedata.split('&')						
						if responsedata[0]=='0':
							print('r','6666666666666')

							decResp = decrypt(responsedata[1],workingKey)
							y = json.loads(decResp)
							if y['si_charge_status']=='0' and y['si_charge_txn_status']=='0':
								print('r','77777777777')

								obj=addon_plan_invoiceuserwise()
								obj.user_id=i.user.id
								obj.addon_plan_id=i.addon_plan.id
								obj.dataroom_id=i.dataroom.id
								obj.start_date=i.start_date
								obj.is_deleted=False
								obj.is_plan_active=True
								obj.total_cost=int(int(i.addon_plan.cost)*int(addonsneed))
								obj.quantity=addonsneed
								obj.planid=plandata1.id
								obj.ccavenue_cartid=obj3.id
								obj.end_date=plandata1.end_date
								obj.save()
								plandata1.addon_plans.add(obj)
								plandata1.save()
								data=planinvoiceuserwise.objects.filter(id=plandata1.id).first()
								Dataroom.objects.filter(id=i.dataroom.id).update(dataroom_storage_allocated = F('dataroom_storage_allocated')+int(int(i.addon_plan.storage)*addonsneed))
								addon_plan_tempforsameday.objects.filter(id=i.id).update(invoice_generated=True)
								send_mail_to_superadmin(subject= 'Data Storage Addon #'+str(i.dataroom.id), userid=i.user.id, first_name = i.user.first_name, user_email=i.user.email ,data =data,addondata=obj,projectname=data.project_name,payment_reference=y['reference_no'],upgradef=0,quantityflag=0)                    
								ccavenue_payment_cartids.objects.filter(id=obj3.id).update(storage_addon_id=obj.id,ref_id=y['reference_no'],si_ref_id=y['si_sub_ref_no'],bank_ref_id=y['bank_ref_no'],receipt_no=y['receipt_no'],bank_mid=y['bank_mid'],is_payment_done=True)
							else:
								pass
						else:
							pass
					else:
						pass
				except:
					Dataroom.objects.filter(id=i.dataroom.id).update(is_expired=True,is_expired=True)
					addon_plan_invoiceuserwise.objects.filter(user_id=i.user.id,dataroom_id=i.dataroom.id,is_deleted=False,is_plan_active=True).update(is_plan_active=False,end_date=datetime.now())
					planinvoiceuserwise.objects.filter(dataroom_id=i.dataroom.id,is_latest_invoice=True,is_plan_active=True).update(is_plan_active=False,is_expired=True)
							

		else:
			pass




		# if addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False).exists():	
		# 	print('coming here 2222222222')
	
		# 	tempaddon_data=addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False)
		# 	for i in tempaddon_data:
		# 		print('coming here 333333333')
		# 		print('coming here rrrrrrrrrrr',Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).exists(),Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) 

		# 		vote_consumed = round((Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
		# 		print('coming here aaaaaaaa')
				
		# 		disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
		# 		print('coming here bbbbb')
				
		# 		dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=i.dataroom.id,is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=i.dataroom.id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
		# 		print('coming here cccccc')
				
		# 		total_consumed=vote_consumed + disclaimer_consumed + dataroom_consumed
		# 		print('coming here ddddddddddd')
				
		# 		dataroomsize=Dataroom.objects.filter(id=i.dataroom.id).first().dataroom_storage_allocated * 1024
		# 		print(total_consumed,dataroomsize)
		# 		if total_consumed > dataroomsize: 
		# 			print('coming here 444444444444')
		# 			extrasize=int(total_consumed)-int(dataroomsize)
		# 			addon_storage=int(i.addon_plan.storage)*1024
		# 			if int(extrasize/addon_storage)<(extrasize/addon_storage):
		# 				addonsneed=int(extrasize/addon_storage)+1
		# 			else:
		# 				addonsneed=int(extrasize/addon_storage)
		# 			print(extrasize,addonsneed,addon_storage)
		# 			for j in range(0,addonsneed):
		# 				print('coming here 555555555555')
		# 				obj=addon_plan_invoiceuserwise()
		# 				obj.user_id=i.user.id
		# 				obj.addon_plan_id=i.addon_plan.id
		# 				obj.dataroom_id=i.dataroom.id
		# 				obj.start_date=i.start_date
		# 				obj.is_deleted=False
		# 				obj.is_plan_active=True
		# 				obj.save()
		# 				plandata1=planinvoiceuserwise.objects.filter(dataroom_id=i.dataroom.id,is_latest_invoice=True).first()  
		# 				plandata1.addon_plans.add(obj)
		# 				plandata1.save()
		# 				data=planinvoiceuserwise.objects.filter(id=plandata1.id).first()
		# 				Dataroom.objects.filter(id=i.dataroom.id).update(dataroom_storage_allocated = F('dataroom_storage_allocated')+int(i.addon_plan.storage))
		# 				addon_plan_tempforsameday.objects.filter(id=i.id).update(invoice_generated=True)
		# 				send_mail_to_superadmin(subject= '1GB Data Storage #'+str(i.dataroom.id), userid=i.user.id, first_name = i.user.first_name, user_email=i.user.email ,data =data,addondata=obj,projectname=data.project_name,payment_reference='',upgradef=0,quantityflag=0)                    
