from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings
import datetime
from .models import *
logger = logging.getLogger(__name__)



def canculate_due_amount(user,planid):
        from .models import planinvoiceuserwise,addon_plan_invoiceuserwise
        totalcharge=0
        tempplan=planinvoiceuserwise.objects.filter(id=planid).last()
        if tempplan.dataroom.addon_payment_overdue==True:
                if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planid,is_payment_done=False).exists():
                    addondata=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.id,is_payment_done=False)
                    for i in addondata:
                        totalcharge=int(i.total_cost)+totalcharge

        if  tempplan.dataroom.addon_payment_overdue==True or tempplan.dataroom.plan_payment_overdue==True:
                if planinvoiceuserwise.objects.filter(user_id=user.id,id=planid,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).exists():
                    planindata=planinvoiceuserwise.objects.filter(user_id=user.id,id=planid,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).last()
                    totalcharge=int(planindata.plan.cost)+totalcharge
                    if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.new_invoiceid,is_payment_done=False).exists():
                        addondata=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.new_invoiceid,is_payment_done=False)
                        for j in addondata:
                            totalcharge=int(j.total_cost)+totalcharge

        return totalcharge



def send_otp_email(subject,first_name,last_name, to, otp,name):
    # logger.info('inside email verification method')
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    ctx = {
        # 'user': first_name,
        'email': toemail,
        'subject': subject,
        'otp': otp,
        'first_name':first_name,
        'last_name':last_name,
        'name':name,
    }

    message = get_template('userauth/otp_mail.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('email successfully send')


def send_activation_email(subject, to, first_name, link):
    logger.info('inside email verification method')
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'link': link
    }

    message = get_template('userauth/account_verify.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('email successfully send')    
    #print ("send_email method called")


def send_trialperiod_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y")
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'starttdate':starttdate,
        'endddate':endddate
    }

    message = get_template('userauth/trial_period_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_trialtwodaysalert_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y")     
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'starttdate':starttdate,
        'endddate':endddate

    }

    message = get_template('userauth/trial_twodays_alert.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_plancancelemail_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname
    }

    message = get_template('userauth/plan_cancel_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_plancancelemail_emailtwo(subject, to, first_name, data,projectname):
    from datetime import timedelta,datetime    
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.cancel_at).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    canceltime=dateobject1.strftime("%d-%m-%Y") 
    deletedate=data.cancel_at+timedelta(days=15)    
    dateobject1=datetime.strptime(str(deletedate).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    deletedateee=dateobject1.strftime("%d-%m-%Y")  

    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'canceltime':canceltime,
        'deletedatee':deletedateee
    }

    message = get_template('userauth/plan_cancel_emailtwo.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_dataroomdelete_email(subject, to, first_name, data,projectname,user):
    from datetime import timedelta,datetime    
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dueamount=canculate_due_amount(user,data.id)
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    duedatee=dateobject2.strftime("%d-%m-%Y")    
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'dueamount':dueamount,
        'duedate':duedatee

    }

    message = get_template('userauth/dataroom_deletion.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_offlinedataroomdelete_email(subject, to, first_name,projectname):
    from datetime import timedelta,datetime    
    subject = subject
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL   
    ctx = {
        'user': first_name,
        'subject': subject,
        'projectname':projectname,
    }
    message = get_template('userauth/offline_dataroomdelete.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_markedfordeletion_email(subject, to, first_name, data,projectname,user):
    from datetime import timedelta,datetime    
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dueamount=canculate_due_amount(user,data.id)
    deletiondate=data.end_date+timedelta(days=15)    
    dateobject1=datetime.strptime(str(deletiondate).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    deletedate=dateobject1.strftime("%d-%m-%Y")  
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    duedatee=dateobject2.strftime("%d-%m-%Y")  
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'dueamount':dueamount,
        'duedate':duedatee,
        'deletiondate':deletedate

    }

    message = get_template('userauth/markedfor_deletion.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_accessrevoked_email(subject, to, first_name, data,projectname,addonflag,addondata,user):
    from datetime import timedelta,datetime
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    threeone=data.start_date+timedelta(days=15)    
    dateobject1=datetime.strptime(str(threeone).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    threedelay=dateobject1.strftime("%d-%m-%Y")     
    if addonflag==1:  
        dateobject2=datetime.strptime(str(addondata.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        duedatee=dateobject2.strftime("%d-%m-%Y")
        dataroomid=addondata.dataroom.id 
        planidd=addondata.planid

    else:
        dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        duedatee=dateobject2.strftime("%d-%m-%Y")
        dataroomid=data.dataroom.id
        planidd=data.id
    dueamount=canculate_due_amount(user,planidd)

    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'dataid': planidd,
        'projectname':projectname,
        'expiry_date':threedelay,
        'duedate':duedatee,
        'dataroomid':dataroomid,
        'dueamount':dueamount,
    }
    message = get_template('userauth/accessrevoked.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()




def send_trialexpiry_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y") 
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'starttdate':starttdate,
        'endddate':endddate

    }

    message = get_template('userauth/trial_expiry.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_autorenewon_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(datetime.now()).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    todaysdate=dateobject1.strftime("%d-%m-%Y")  
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    enddate=dateobject2.strftime("%d-%m-%Y")    
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'todaysdate':todaysdate,
        'enddate':enddate
    }

    message = get_template('userauth/autorenewon.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_autorenewoff_email(subject, to, first_name, data,projectname):
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(datetime.now()).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    todaysdate=dateobject1.strftime("%d-%m-%Y")  
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    enddate=dateobject2.strftime("%d-%m-%Y")    
    subject = str(subject)+str(enddate)    
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'todaysdate':todaysdate,
        'enddate':enddate
    }

    message = get_template('userauth/autorenewoff.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()













def send_paymentfail_email(subject, to, first_name, data,projectname,addonflag,addondata,amount_due):
    from datetime import timedelta,datetime
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    if addonflag==1:
        grand_total=addondata.total_cost
        threeone=addondata.start_date+timedelta(days=3)    
        dateobject1=datetime.strptime(str(threeone).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        threedelay=dateobject1.strftime("%d-%m-%Y")  
        dateobject2=datetime.strptime(str(addondata.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        duedatee=dateobject2.strftime("%d-%m-%Y")
    else:
        threeone=data.start_date+timedelta(days=3)    
        dateobject1=datetime.strptime(str(threeone).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        threedelay=dateobject1.strftime("%d-%m-%Y")  
        dateobject2=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        duedatee=dateobject2.strftime("%d-%m-%Y")
        grand_total=data.grand_total
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'dataid': data.id,
        'projectname':projectname,
        'expiry_date':threedelay,
        'duedate':duedatee,
        'dataroomid':data.dataroom.id,
        'grandtotal':amount_due,
    }

    message = get_template('userauth/payment_fail.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'],from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()






def send_planrenewal_email(subject, to, first_name, data,projectname,isaddon,addondata):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    except:
        dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    try:
        dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    except:
        dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
    endddate=dateobject2.strftime("%d-%m-%Y")    
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'isaddon':isaddon,
        'addondata':addondata,
        'starttdate':starttdate,
        'endddate':endddate
    }

    message = get_template('userauth/planrenewal_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_subscription_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    startdate=dateobject1.strftime("%d-%m-%Y")  
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    enddate=dateobject2.strftime("%d-%m-%Y")

    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'startdate':startdate,
        'enddate':enddate
    }

    message = get_template('userauth/subscription_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()


def send_twodaysalert_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y")
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'starttdate':starttdate,
        'endddate':endddate
    }

    message = get_template('userauth/twodays_alert.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_planexpiry_email(subject, to, first_name, data,projectname):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y")
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'projectname':projectname,
        'starttdate':starttdate,
        'endddate':endddate

    }

    message = get_template('userauth/plan_expiryalert.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()



def dvd_addon_request(subject, to, first_name, data,refno):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject1=datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    orderdate=dateobject1.strftime("%d-%m-%Y")
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
        'data': data,
        'orderdate':orderdate,
        'refno':refno
    }

    message = get_template('userauth/dvd_addon_request.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_mail_to_superadmin(subject, userid, first_name, user_email,data,addondata,projectname,payment_reference,upgradef,quantityflag,phone,company_name,country):
    user_info = User.objects.filter(id=userid).first()
    subscribed_user_info = User.objects.filter(email=user_email).first()
    subject = subject
    to = ['rrp5occwk_v8sheah@parser.zohocrm.com','sales@docullyvdr.com']
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    except:
        dateobject1=datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    try:
        dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    except:
        dateobject2=datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
    endddate=dateobject2.strftime("%d-%m-%Y")
    print(starttdate,'yyy',endddate,'uuu')
    if addondata==0:
        addon_quantity=''
        addon_type=''
        addon_validity=''
        planname=data.plan.name
        amount=data.grand_total
    else:
        if quantityflag==1:            
            addon_quantity=addondata.quantity
            addon_type='Data DVD Addon'
            planname=addondata.dvd_addon_plan.name
            amount=addondata.total_cost
        else:
            addon_quantity=addondata.quantity
            addon_type='Data Storage Addon'
            planname=addondata.addon_plan.name
            amount=addondata.addon_plan.cost
        addon_validity='Billing Period End Date '+str(endddate)


    if upgradef==1:
        addon_type='Plan Upgrade'
    ctx = {
        'user_info':user_info,
        'data': data,
        'addondata':addondata,
        'projectname':projectname,
        'plan_name':planname,
        'startdate':starttdate,
        'enddate':endddate,
        'Amount':amount,
        'signup_type':'Existing',
        'addon_type':addon_type,
        'addon_quantity':addon_quantity,
        'addon_validity':addon_validity,
        'payment_status':'Paid',
        'payment_mode': 'Online',
        'payment_reference': payment_reference,
        'phone':phone,
        'company_name':company_name,
        'country':country
    }

    message = get_template('userauth/admin_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docullyvdr.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()

def send_mail_to_superadminaddon(subject,userid,plandata,addondata,projectname,flag):
    user_info = User.objects.filter(id=userid).first()
    subject = subject
    to = ['rrp5occwk_v8sheah@parser.zohocrm.com','sales@docullyvdr.com']
    from_email = settings.DEFAULT_FROM_EMAIL
    dateobject0=datetime.strptime(str(addondata.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    purchase_date=dateobject0.strftime("%d-%m-%Y")
    if flag=='DataDVD':
        dateobject1=datetime.strptime(str(plandata.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    else:
        dateobject1=datetime.strptime(str(addondata.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    starttdate=dateobject1.strftime("%d-%m-%Y")
    dateobject2=datetime.strptime(str(plandata.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
    endddate=dateobject2.strftime("%d-%m-%Y")
    print(starttdate,'yyy',endddate,'uuu')
    ctx = {
        'subject': subject,
        'plandata': plandata,
        'projectname':projectname,
        'startdate':starttdate,
        'enddate':endddate,
        'purchase_date':purchase_date,
        'user_info':user_info,
        'addondata':addondata,
        'flag':flag
    }

    message = get_template('userauth/admin_email_addon.html').render(ctx)
    msg = EmailMessage(subject, message, to=to,cc=['billing@docullyvdr.com'], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
# def subscribed_plan_email(to, planid):
#     subject = subject
#     toemail=to
#     to = [to]
#     from_email = settings.DEFAULT_FROM_EMAIL
#     ctx = {
#         'user': first_name,
#         'email': toemail,
#         'subject': subject,
#         'data': data,
#         'projectname':projectname
#     }

#     message = get_template('userauth/trial_period_email.html').render(ctx)
#     msg = EmailMessage(subject, message, to=to, from_email=from_email)
#     msg.content_subtype = 'html'
#     msg.send()

def send_addon_email(subject, to, first_name):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
    }

    # message = get_template('userauth/account_verify.html').render(ctx)
    message='addon email'
    msg = EmailMessage(subject, message, to=to,cc=['billing@docully.com'], from_email=from_email)
    # msg.content_subtype = 'html'
    msg.send()
    # logger.info('email successfully send')  

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



