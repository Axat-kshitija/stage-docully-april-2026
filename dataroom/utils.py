from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone 
from constants.constants import *
from users_and_permission.models import DataroomMembers, DataroomGroups
from .models import Dataroom 

logger = logging.getLogger(__name__) 

def date_difference_new(joined_date):
    current_date = timezone.now()
    # print("current_date", current_date, "joined_date", joined_date)
    # joined_date = datetime.strptime(joined_date,"%Y-%m-%dT%H:%M:%S.%f")
    joined_date = datetime.strptime(joined_date,"%Y-%m-%d %H:%M:%S.%f")
    # print("current_date", current_date.replace(tzinfo=None), "joined_date", joined_date.replace(tzinfo=None))
    diff = abs((joined_date.replace(tzinfo=None) - current_date.replace(tzinfo=None)).days)
    expiry_date = joined_date.replace(tzinfo=None) + timedelta(days=10)
    return diff, expiry_date

def date_difference(joined_date):
    current_date = timezone.now()
    # print("current_date", current_date, "joined_date", joined_date)
    # joined_date = datetime.strptime(joined_date,"%d/%m/%Y %H:%M:%S")
    #### original
    joined_date = datetime.strptime(joined_date,"%Y-%m-%dT%H:%M:%S.%f")
    #### original
    # joined_date = datetime.strptime(joined_date,"%Y-%m-%d %H:%M:%S.%f")
    # print("current_date", current_date.replace(tzinfo=None), "joined_date", joined_date.replace(tzinfo=None))
    diff = abs((joined_date.replace(tzinfo=None) - current_date.replace(tzinfo=None)).days)
    expiry_date = joined_date.replace(tzinfo=None) + timedelta(days=10)
    return diff, expiry_date

def send_email_trial_dataroom(data, user, emails):
    # print("emailllllls", emails)
    subject = data.get("dataroom_name")+" dataroom is expired from trial version on "+data.get("trial_expiry_date")
    to = [site_settings['support_email_id']]
    from_email = settings.DEFAULT_FROM_EMAIL
    
    ctx = {
        'user': user,
        'email': to,
        'subject': subject,
        'data' : data
    }

    message = get_template('emailer/contact_support_trail.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email, cc=emails)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send') 


def send_password_to_dataroom_admin_or_end_user(user, dataroom, password, subject ):
    logger.info("send password to dataroom admin or end user")
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    
    ctx = {
        'user': user,
        'email': to,
        'subject': subject,
        'password' : password, 
        'dataroom' : dataroom
    }

    message = get_template('emailer/dataroom_admin_password.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
 
def send_email_to_already_exist_admin_or_end_user(user , dataroom, subject):
    logger.info("send password to dataroom admin or end user")
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    
    ctx = {
        'user': user,
        'email': to,
        'subject': subject,
        'dataroom': dataroom
    }

    message = get_template('emailer/dataroom_admin__or_user_already_exist.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    


def getStartEndDateofWeek(dataroom, from_date, to_date):
    data = {}
    dates_list = []
    dataroom_views = []
    billable_hours = []
    unbilled_hours = []
    # print("From Date", from_date, type(from_date), "To Date", to_date, type(to_date))
    #day = datetime.today()
    dt = datetime.today().date()
    start = datetime.strptime(from_date, '%Y-%m-%d')#dt - timedelta(days=dt.weekday())
    end = datetime.strptime(to_date, '%Y-%m-%d')#start + timedelta(days=6)
    days = ((end-start).days)+1
    # print("daysssssssss", days)
    for i in reversed(range(0,days)):
        # print("End-----", end, type(end), i)
        dates = end - timedelta(days=i)
        # print("End-----", dates)
        #print(dates.strftime('%d-%b'))
        dates_list.append(dates.strftime('%d/%m'))
        dataroom_views.append(dataroom.filter(created_date__year=dates.year, created_date__month=dates.month, created_date__day=dates.day).count())
    data['dates_list'] = dates_list
    data['dataroom_views'] = dataroom_views
    return data


def WatermarkingImage(data, ip):
    # print("--------",data)
    from . import watermarking
    # if data.get('type') == 'center :: center':
    if watermarking.add_watermark_cc(data, ip):

        return True
        
    return False

def checkdataroomaccess(user,dataroom):
    dataroommemberdata=DataroomMembers.objects.filter(member_id=user,dataroom_id=dataroom,is_deleted=False).first()
    dataa=Dataroom.objects.filter(id=dataroom).first()
    permissionvar=True
    if dataa.is_expired==False and dataa.is_request_for_archive==False and dataa.is_deleted==False and dataa.is_request_for_deletion==False:
        print('inside11111111111',dataroommemberdata)

        if dataroommemberdata:
            print('inside22222222222')

            if dataroommemberdata.is_deleted==False:
                print('inside333333333333')

                permissionvar=False  
    else:
      pass
    return permissionvar