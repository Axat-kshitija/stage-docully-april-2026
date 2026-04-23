from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids
from dataroom.models import Dataroom,DataroomDisclaimer
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime
from django.utils import timezone
from .utils import send_mail_to_superadmin,send_dataroomdelete_email,send_markedfordeletion_email,send_accessrevoked_email

def overdue_accessrevoke_job():
				three_end_date=datetime.now() - timedelta(days=3)
				print(datetime.now())
				if planinvoiceuserwise.objects.filter(end_date__lte=three_end_date,auto_renewal=True,is_latest_invoice=True,is_plan_active=False,is_expired=False,plan_renewed=True).exists():
					plandata= planinvoiceuserwise.objects.filter(end_date__lte=three_end_date,auto_renewal=True,is_latest_invoice=True,is_plan_active=False,is_expired=False,plan_renewed=True)
					for i in plandata:
						Dataroom.objects.filter(id=i.dataroom.id).update(is_expired=True)
						send_markedfordeletion_email(subject= 'Notice – Access to Docully Subscription for Project '+str(i.dataroom.dataroom_nameFront)+' has been marked for Deletion.', to = str(i.user.email), first_name = i.user.first_name, data =i,projectname=i.dataroom.dataroom_nameFront,user=i.user)						
						send_accessrevoked_email(subject='Docully Subscription for Project '+str(i.dataroom.dataroom_nameFront)+' – Access Revoked', to=str(i.user.email), first_name=i.user.first_name, data=i,projectname=i.dataroom.dataroom_nameFront,addonflag=0,addondata='',user=i.user)

				if addon_plan_invoiceuserwise.objects.filter(created_date__lte=three_end_date,is_payment_done=False,is_deleted=False).exists():
					addondata=addon_plan_invoiceuserwise.objects.filter(created_date__lte=three_end_date,is_payment_done=False,is_deleted=False)
					addon_plan_invoiceuserwise.objects.filter(created_date__lte=three_end_date,is_payment_done=False).update(is_deleted=True)
					for j in addondata:
						plandata=planinvoiceuserwise.objects.filter(id=j.planid).last()
						Dataroom.objects.filter(id=j.dataroom.id).update(is_expired=True)
						send_accessrevoked_email(subject='Docully Subscription for Project '+str(j.dataroom.dataroom_nameFront)+' – Access Revoked', to=str(i.user.email), first_name=j.user.first_name, data=plandata,projectname=j.dataroom.dataroom_nameFront,addonflag=1,addondata=j,user=j.user)
