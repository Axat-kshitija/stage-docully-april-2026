from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids
from dataroom.models import Dataroom,DataroomDisclaimer
from Vote.models import Vote
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime,date,time
from django.utils import timezone
from django.db.models import F
from .utils import send_mail_to_superadmin,send_twodaysalert_email,send_trialtwodaysalert_email,send_trialexpiry_email,send_planrenewal_email,send_paymentfail_email
from django.db.models import Count, Min, Sum, Avg
import requests
from .ccavutil import encrypt,decrypt
import json
import stripe
stripe.api_key = 'sk_test_51NL2YpSDKmPlLj2iibexoWwPr01eypoqPSenOPqVjDruALmbAuZ2T8HcAsJx89Lz5J3ipBjJqaVu2YRhBleZXdJs00701jrPoi'
        
def daily_plan_invoice_job():
				start_datee = datetime.now()
				end_datee = start_datee - timedelta(days=1) 
				print('1111111111111111111111111',start_datee,end_datee,timezone.now())


				if planinvoiceuserwise.objects.filter(end_date__range=(end_datee,start_datee),cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
					temp_plandata=planinvoiceuserwise.objects.filter(end_date__range=(end_datee,start_datee),cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False)
					print('22222222222222222222')
					for k in temp_plandata:
						print('333333333333333')
						if k.end_date.date() == date.today():
							Dataroom.objects.filter(id=k.dataroom.id,is_request_for_archive=True)
						try:
							overdueamount=0
							plandataa=subscriptionplan.objects.filter(id=k.plan.id).first()
							if Dataroom.objects.filter(id=k.dataroom.id,addon_payment_overdue=True).exists() and addon_plan_invoiceuserwise.objects.filter(planid=k.id,is_payment_done=False).exists():
								addondata=addon_plan_invoiceuserwise.objects.filter(planid=k.id,is_payment_done=False)
								for m in addondata:
									overdueamount=int(m.total_cost)+overdueamount				
							if 'trial' not in plandataa.name.lower():
								ccavenue_data=ccavenue_payment_cartids.objects.filter(new_plan_id=k.id).last()
								need_addons=0
								obj3=ccavenue_payment_cartids()
								obj3.user_id=k.user.id
								obj3.is_renewal=True
								# obj3.is_new_plan=True
								obj3.save()
								print('444444444444444444')


								plan_obj=planinvoiceuserwise()
								plan_obj.user_id=k.user.id
								plan_obj.plan_id=k.plan.id
								plan_obj.dataroom_id=k.dataroom.id
								plan_obj.selected_plan=k.selected_plan
								plan_obj.edition=k.edition
								plan_obj.select_billing_term=k.select_billing_term
								plan_obj.customer_name=k.customer_name
								plan_obj.company_name=k.dataroom.dataroom_nameFront
								plan_obj.billing_address=k.billing_address
								plan_obj.billing_city=k.billing_city
								plan_obj.billing_state=k.billing_state
								plan_obj.billing_country=k.billing_country
								plan_obj.po_box=k.po_box
								plan_obj.effective_price=k.effective_price
								plan_obj.total_fee=k.total_fee
								plan_obj.vat=k.vat
								plan_obj.grand_total=int(k.plan.cost)
								plan_obj.payment_option=k.payment_option
								plan_obj.is_latest_invoice=False
								plan_obj.start_date=datetime.now()
								plan_obj.auto_renewal=True
								plan_obj.ccavenue_cartid=obj3.id
								plan_obj.project_name=k.project_name

								if plandataa.term.lower()=='monthly':
										plan_obj.end_date=datetime.combine(date.today(),time(23, 59))+timedelta(days=30)
								elif plandataa.term.lower()=='quarterly':
										plan_obj.end_date=datetime.now() + timedelta(days=90)
								elif plandataa.term.lower()=='annually' or plandataa.term.lower()=='yearly':
										plan_obj.end_date=datetime.now() + timedelta(days=365)
								addon_plan_invoiceuserwise.objects.filter(user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True,planid=k.id).update(is_plan_active=False,end_date=datetime.now())
									
								vote_consumed = round((Vote.objects.filter(dataroom_id=k.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=k.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
								disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=k.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=k.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
								dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=k.dataroom.id,is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=k.dataroom.id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
								total_consumed=vote_consumed + disclaimer_consumed + dataroom_consumed
								dataroomsize=Dataroom.objects.filter(id=k.dataroom.id).first().dataroom_storage_allocated * 1024
								plan_storage=k.plan.storage*1024
								if plan_storage < total_consumed:
									extra_storage=total_consumed-plan_storage
									addon_storage=1*1024
									if int(extra_storage/addon_storage)<(extra_storage/addon_storage):
										need_addons=int(extra_storage/addon_storage)+1
									else:
										need_addons=int(extra_storage/addon_storage)
								plan_obj.save()
								plandata1=planinvoiceuserwise.objects.filter(id=plan_obj.id).first()  
								if need_addons!=0:
												obj=addon_plan_invoiceuserwise()
												obj.user_id=k.user.id
												obj.addon_plan_id=1
												obj.dataroom_id=k.dataroom.id
												obj.start_date=datetime.now()
												obj.is_deleted=False
												obj.is_plan_active=True
												obj.is_renewal=True
												obj.total_cost=int(100*int(need_addons))
												obj.quantity=need_addons
												obj.planid=plan_obj.id
												obj.ccavenue_cartid=obj3.id
												obj.end_date=plan_obj.end_date

												obj.save()

												plandata1=planinvoiceuserwise.objects.filter(id=plan_obj.id).first()  
												plandata1.addon_plans.add(obj)
												plandata1.grand_total=int(k.plan.cost)+int(100*int(need_addons))
												plandata1.save()

								Dataroom.objects.filter(id=k.dataroom.id).update(dataroom_storage_allocated = int(k.plan.storage)+int(need_addons))

								access_code='AVXY03ID76AY64YXYA'
								workingKey='94DEDF16E45876158DCC2ADDF67BC754'
								# amountt=(int(k.grand_total)+int(need_addons*50))*3.67
								amnttemp=need_addons*100
								amountt1=float(k.plan.cost+amnttemp+overdueamount)
								amountt=amountt1*3.67
								merchant_data1='{"si_sub_ref_no":"'+str(ccavenue_data.si_ref_id)+'","si_mer_charge_ref_no":"'+str(obj3.id)+'","si_amount":"'+str(amountt)+'","si_currency":"AED"}'

								encryption = encrypt(merchant_data1,workingKey)
								# newurl="https://login.ccavenue.ae/apis/servlet/DoWebTrans?enc_request="+str(encryption)+"&access_code=AVXY03ID76AY64YXYA&request_type=JSON&command=chargeSI&version=1.1&si_sub_ref_no="+str(ccavenue_data.si_ref_id)+"&si_mer_charge_ref_no="+str(obj3.id)+"&si_currency=AED&si_amount="+str(amountt)
								# datart=requests.post(newurl)
								# responsedata=str(datart.text)
								# responsedata=responsedata.replace('status','').replace('enc_response','').replace("\r",'').replace('\n','').replace('=','')	
								# responsedata=responsedata.split('&')						
								planinvoiceuserwise.objects.filter(id=k.id).update(is_plan_active=False,plan_renewed=True,new_invoiceid=plan_obj.id)
								print('5555555')
								email=plan_obj.user.email
						        customer_data = stripe.Customer.list(email=email).data   
						        print('---------------================',customer_data)
						        # if the array is empty it means the email has not been used yet  
						        if len(customer_data) != 0:
						        # creating customer
						            customer = customer_data[0]
						            extra_msg = "Customer already existed." 
									ss=stripe.PaymentMethod.list(
							          customer=customer.id,
							          # type="card",
							        ).data
							        print('-----------pay ',ss[0])
							        try:
							            pay=stripe.PaymentIntent.create(
							            amount=amountt,
							            currency='inr',
							            automatic_payment_methods={"enabled": True},
							            customer=customer.id,
							            payment_method=ss[0].id,
							            off_session=True,
							            confirm=True,
							            )
							            print('--------------',pay)
							        
						            # customer = stripe.Customer.create(
						            # # email=email, payment_method=payment_method_id)  
						            # email=email)  
								# if responsedata[0]=='0':
								# 	decResp = decrypt(responsedata[1],workingKey)
								# 	y = json.loads(decResp)
								# 	print('6666666666')
								# 	if y['si_charge_status']=='0' and y['si_charge_txn_status']=='0':
								# 				print('7777777777')
										planinvoiceuserwise.objects.filter(id=k.id).update(is_latest_invoice=False,is_plan_active=False)
										planinvoiceuserwise.objects.filter(id=plan_obj.id).update(payment_complete=True,is_latest_invoice=True,is_plan_active=True,paid_at=datetime.now())
										if overdueamount!=0:
											if Dataroom.objects.filter(id=k.dataroom.id,addon_payment_overdue=True).exist() and addon_plan_invoiceuserwise.objects.filter(planid=k.id,is_payment_done=False).exists():
												addondata=addon_plan_invoiceuserwise.objects.filter(planid=planindata.id,is_payment_done=False)
												for n in addondata:
													addon_plan_invoiceuserwise.objects.filter(id=n.id).update(is_payment_done=True,paid_at=datetime.datetime.now())
												Dataroom.objects.filter(id=k.dataroom.id).update(addon_payment_overdue=False,is_expired=False)																
										if need_addons!=0:
											addon_plan_invoiceuserwise.objects.filter(id=obj.id).update(is_payment_done=True,paid_at=datetime.now())
											ccavenue_payment_cartids.objects.filter(id=obj3.id).update(is_storage_addon=True,new_plan_id=plan_obj.id,storage_addon_id=obj.id,ref_id=y['reference_no'],si_ref_id=y['si_sub_ref_no'],bank_ref_id=y['bank_ref_no'],receipt_no=y['receipt_no'],bank_mid=y['bank_mid'],is_payment_done=True)
											send_mail_to_superadmin(subject= 'User Activity- Plan Renewal #'+str(k.dataroom.id), userid=k.user.id, first_name = k.user.first_name, user_email=k.user.email ,data =plandata1,addondata=obj,projectname=plandata1.project_name,payment_reference=y['reference_no'],upgradef=0,quantityflag=0)                    
											send_planrenewal_email(subject= 'Your Docully Subscription is renewed successfully', to =plandata1.user.email, first_name = plandata1.user.first_name, data =plandata1,projectname=plandata1.dataroom.dataroom_nameFront,isaddon=True,addondata=obj)
										else:
											ccavenue_payment_cartids.objects.filter(id=obj3.id).update(new_plan_id=plan_obj.id,ref_id=y['reference_no'],si_ref_id=y['si_sub_ref_no'],bank_ref_id=y['bank_ref_no'],receipt_no=y['receipt_no'],bank_mid=y['bank_mid'],is_payment_done=True)
											send_mail_to_superadmin(subject= 'User Activity- Plan Renewal #'+str(k.dataroom.id), userid=k.user.id, first_name = k.user.first_name, user_email=k.user.email ,data =plan_obj,addondata=0,projectname=plan_obj.project_name,payment_reference=y['reference_no'],upgradef=0,quantityflag=0)                    
											send_planrenewal_email(subject= 'Your Docully Subscription is renewed successfully', to =plan_obj.user.email, first_name = plan_obj.user.first_name, data =plan_obj,projectname=plan_obj.dataroom.dataroom_nameFront,isaddon=False,addondata='')
									except stripe.error.CardError as e:
										err = e.error
										# Error code will be authentication_required if authentication is needed
										print("Code is:00000000000000 %s" % err.code)
										payment_intent_id = err.payment_intent['id']
										payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
						        		# else:
										if need_addons!=0:
											Dataroom.objects.filter(id=k.dataroom.id).update(plan_payment_overdue=True,addon_payment_overdue=True)
										else:	
											Dataroom.objects.filter(id=k.dataroom.id).update(plan_payment_overdue=True)
										send_paymentfail_email(subject= 'Alert - Docully Subscription for Project '+str(k.dataroom.dataroom_nameFront)+' - Payment Overdue', to =str(k.user.email), first_name = k.user.first_name, data=plandata1,projectname=k.dataroom.dataroom_nameFront,addonflag=0,addondata='',amount_due=str(amountt1))


									
								else:
									if need_addons!=0:
										Dataroom.objects.filter(id=k.dataroom.id).update(plan_payment_overdue=True,addon_payment_overdue=True)
									else:	
										Dataroom.objects.filter(id=k.dataroom.id).update(plan_payment_overdue=True)
									send_paymentfail_email(subject= 'Alert - Docully Subscription for Project '+str(k.dataroom.dataroom_nameFront)+' - Payment Overdue', to =str(k.user.email), first_name = k.user.first_name, data=plandata1,projectname=k.dataroom.dataroom_nameFront,addonflag=0,addondata='',amount_due=str(amountt1))
							
							else:
								Dataroom.objects.filter(id=k.dataroom.id).update(is_expired=True,trial_expired=True)
								addon_plan_invoiceuserwise.objects.filter(user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True).update(is_plan_active=False,end_date=datetime.now())
								planinvoiceuserwise.objects.filter(id=k.id).update(is_plan_active=False)
						
						except:
								Dataroom.objects.filter(id=k.dataroom.id).update(plan_payment_overdue=True)
								addon_plan_invoiceuserwise.objects.filter(user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True).update(is_plan_active=False,end_date=datetime.now())
								planinvoiceuserwise.objects.filter(id=k.id).update(is_plan_active=False)
								send_paymentfail_email(subject= 'Alert##### - Something wrong with crone 2 check for this', to =str('rushikesh.g@axat-tech.com'), first_name = k.user.first_name, data=k,projectname=k.dataroom.dataroom_nameFront,addonflag=0,addondata='',amount_due=0)


						# utils.send_mail_to_superadmin(subject= 'User Activity- Paid subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=obj.project_name,payment_reference='',upgradef=rflag,quantityflag=0)                    
						# if p==1:
											# need_addons=int(extra_storage/addon_storage)+1
											# already_addons=addon_plan_invoiceuserwise.objects.filter(user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True).count()
											# if  need_addons<already_addons:
											# 	needtodelete=already_addons-need_addons
											# 	invoicedata1=addon_plan_invoiceuserwise.objects.filter(user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True)
											# 	pp=0
											# 	if len(k.addon_plans.all())>=need_addons:
											# 		for p in k.addon_plans.all():
											# 			plan_obj.addon_plans.add(invoicedata1[pp])
											# 			pp=pp+1
											# 			if pp>=need_addons-1:
											# 				break
											# 	if needtodelete>0:
											# 		for ll in range(needtodelete-1, -1, -1):
											# 			addon_plan_invoiceuserwise.objects.filter(id=invoicedata1[ll].id,user_id=k.user.id,dataroom_id=k.dataroom.id,is_deleted=False,is_plan_active=True).update(is_deleted=True,is_plan_active=False,end_date=datetime.now())
