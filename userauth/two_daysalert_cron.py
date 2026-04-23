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

def daily_twoday_alert__job():
				twostart_datee = datetime.now() + timedelta(days=2)
				twoend_datee = twostart_datee + timedelta(days=1) 
				print(datetime.now())
				if planinvoiceuserwise.objects.filter(end_date__range=(twostart_datee,twoend_datee),cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
					temp_plandata1=planinvoiceuserwise.objects.filter(end_date__range=(twostart_datee,twoend_datee),cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False)
					for j in temp_plandata1:
						plandataa=subscriptionplan.objects.filter(id=j.plan.id).first()
						if 'trial' not in plandataa.name.lower():
							send_twodaysalert_email(subject= 'Auto Renewal in 02 Days - Your Docully Subscription', to =str(j.user.email), first_name = j.user.first_name, data =j,projectname=j.dataroom.dataroom_nameFront)

				if planinvoiceuserwise.objects.filter(end_date__range=(twostart_datee,twoend_datee),auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
					temp_plandata1=planinvoiceuserwise.objects.filter(end_date__range=(twostart_datee,twoend_datee),auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False)
					for j in temp_plandata1:
						plandataa=subscriptionplan.objects.filter(id=j.plan.id).first()
						if 'trial' in plandataa.name.lower():
							send_trialtwodaysalert_email(subject= 'Your free trial is expiring in 2 days', to = str(j.user.email), first_name = j.user.first_name, data =j,projectname=j.dataroom.dataroom_nameFront)


