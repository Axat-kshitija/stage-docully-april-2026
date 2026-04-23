from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids
from dataroom.models import Dataroom,DataroomDisclaimer
from Vote.models import Vote
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime
from django.utils import timezone
from django.db.models import F
from .utils import send_mail_to_superadmin,send_twodaysalert_email,send_trialtwodaysalert_email,send_trialexpiry_email,send_planrenewal_email,send_paymentfail_email
from django.db.models import Count, Min, Sum, Avg
import requests
from .ccavutil import encrypt,decrypt
import json

def daily_plan_cancel_job():
				start_datee = datetime.now()
				end_datee = start_datee + timedelta(days=1) 
				print('1111111111111111111111111',start_datee,end_datee,timezone.now())
				if planinvoiceuserwise.objects.filter(end_date__lte=end_datee,auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
					print('----inside iff')
					temp_plandata1=planinvoiceuserwise.objects.filter(end_date__lte=end_datee,auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False)
					for j in temp_plandata1:
						print('-------inside for',j.dataroom.id)
						plandataa=subscriptionplan.objects.filter(id=j.plan.id).first()
						planinvoiceuserwise.objects.filter(id=j.id).update(is_plan_active=False)
						if 'trial' not in plandataa.name.lower():
							addon_plan_invoiceuserwise.objects.filter(user_id=j.user.id,dataroom_id=j.dataroom.id,is_deleted=False,is_plan_active=True).update(is_plan_active=False,end_date=datetime.now())
							Dataroom.objects.filter(id=j.dataroom.id).update(is_expired=True)
						else:
							Dataroom.objects.filter(id=j.dataroom.id).update(is_expired=True,trial_expired=True)
							send_trialexpiry_email(subject= 'Alert - Your free trial period has expired', to =str(j.user.email), first_name = j.user.first_name, data =j,projectname=j.dataroom.dataroom_nameFront)
				else:
					print('---inside else')
