from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings
from .models import Emailer, SiteSettings
from .serializers import EmailerSerializer
from constants import constants
import datetime
from django.utils.crypto import get_random_string
from userauth.models import Profile,User
logger = logging.getLogger(__name__)


def send_deletion_dataroom_email(dataroom, user,mails):
    # subject = "Request for Deletion of Dataroom"
    # subject = subject
    subject = "Deletion request for " + dataroom.dataroom_nameFront + " at " + str(datetime.date.today())
    subject = subject
    # to=mails
    to=[user.email,constants.site_settings['support_email_id']]
    print(to,'RRRRRRRRRRRRRRRRRRIIIIIIIIIIIIIIIIII')
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        'user': user,
        'site_setting': site_settings
    }

    message = get_template('emailer/request_for_delation.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    to = [constants.site_settings['support_email_id']]

    # message2 = get_template('emailer/request_for_delation_cancel.html').render(ctx)
    # msg2 = EmailMessage(subject, message2, to=to, from_email=from_email)
    # msg2.content_subtype = 'html'
    # msg2.send()

    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user.id, 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 1, 
        'to_email': user.email
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()

def send_deletion_dataroom_cancel_email(dataroom, user,mails):
    subject = "Request for Cancel Deletion Request of " + dataroom.dataroom_nameFront + " at " + str(datetime.date.today())
    subject = subject
    to = [user.email,constants.site_settings['support_email_id']]
    # to=to+mails
    # print(to,'YYYYYYYYYYYYYYUUUUUUUUUUUUUUUUUUUU')

    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        'user': user,
        'site_setting': site_settings
    }

    message = get_template('emailer/request_for_delation_cancel.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user.id, 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 1, 
        'to_email': user.email
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()


def send_archive_dataroom_email(dataroom, user,mails):
    subject = "Request for Archive for " + dataroom.dataroom_nameFront + " at " + str(datetime.date.today())
    subject = subject
    to = [constants.site_settings['support_email_id']]
    to=to+mails
    # print(to,'Checkkkkkkkkkkkkkhhhhhhhhhhhhygtftfrfrd')
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        'user': user,
        'site_setting': site_settings
    }

    message = get_template('emailer/request_for_archive.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 1')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user.id, 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user.email
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()


def send_archive_dataroom_cancel_email(dataroom, user,mails):
    subject = "Request for Cancel Archive Request of " + dataroom.dataroom_nameFront + " at " + str(datetime.date.today())
    subject = subject
    to = [constants.site_settings['support_email_id']]
    to=to+mails

    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        'user': user,
        'site_setting': site_settings
    }

    message = get_template('emailer/request_for_archive_cancel.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 1')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user.id, 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user.email
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()








def email_to_dataroom_authorised(user,dataroom):
    subject = "Email to Data Room upload request received and accepted."
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = { 
        'user': user,
        'site_setting': site_settings, 
        # 'new_data':new_data
        'dataroom':dataroom.dataroom_nameFront
    }

    message = get_template('data_documents/email_to_dataroom_initiate_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()





def email_to_dataroom_invalid_dataroom(user,dataroom):
    subject = "Email to Data Room upload request declined – Data Room not found."
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = { 
        'user': user,
        'site_setting': site_settings, 
        # 'new_data':new_data
        'dataroom':dataroom
    }

    message = get_template('data_documents/email_to_dataroom_invalid_dataroom_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()



def email_to_dataroom_unauth_user(user,dataroom):
    subject = "Email to Data Room upload request is declined."
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = { 
        'user': user,
        'site_setting': site_settings, 
        # 'new_data':new_data
        'dataroom':dataroom
    }

    message = get_template('data_documents/email_to_dataroom_unauth_user_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()












#invitation_email.html
def send_invitation_account_email(user):
    subject = "Invitation to on Docully"
    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = { 
        'user': user,
        'site_setting': site_settings, 
        'new_data':new_data
    }

    message = get_template('emailer/invitation_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 2')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user["id"], 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user["email"]
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()


#invitation_email.html
def send_dataroom_admin_email_if_user_exist(user, new_data, sender, dataroom_data ,custom_msg):
    # print(dataroom_data)
    try:
        subject = "Invitation to Dataroom "+dataroom_data['dataroom_nameFront']+" on DocullyVDR."
    except:
        subject = "Invitation to Dataroom "+dataroom_data.dataroom_nameFront+" on DocullyVDR."

    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    print(new_data,'888888888888888888888999999999999999999')
    ctx = {
        'user': user,
        'site_setting': site_settings, 
        'new_data':new_data, 
        'sender': sender, 
        'dataroom':dataroom_data,
        'custom_msg':custom_msg,
    }
    # print('mail sending working 3')

    message = get_template('emailer/send_dataroom_admin_email_if_user_exist.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send(fail_silently=False)

    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user.id, 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user.email
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()

# lNLMc6RtT2G0O8s5bcTdXqFf3wu58tcq2RRJjdyVdUhVJ3T14Ojzcz6k0kXecRhueovsBl71GxW3eDMQUHBH7ZC0PA9RPFnJWfML
# lNLMc6RtT2G0O8s5bcTdXqFf3wu58tcq2RRJjdyVdUhVJ3T14Ojzcz6k0kXecRhueovsBl71GxW3eDMQUHBH7ZC0PA9RPFnJWfML




def group_active_mail_send(user, sender, dataroom_data):
    # print(dataroom_data)
    try:
        subject = "Invitation to Dataroom "+dataroom_data['dataroom_nameFront']+" on DocullyVDR."
    except:
        subject = "Invitation to Dataroom "+dataroom_data.dataroom_nameFront+" on DocullyVDR."

    subject = subject
    to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    # print(new_data,'888888888888888888888999999999999999999')
    ctx = {
        'user': user,
        'site_setting': site_settings, 
        # 'new_data':new_data, 
        'sender': sender, 
        'dataroom':dataroom_data,
        # 'custom_msg':custom_msg,
    }
    # print('mail sending working 3')

    message = get_template('emailer/group_active_mail.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send(fail_silently=False)

    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    # data = {
    #     'subject':subject, 
    #     'user' : user.id, 
    #     'from_email':from_email, 
    #     'body_html':message, 
    #     'emailer_type': 2, 
    #     'to_email': user.email
    # }
    # emailer_serializer = EmailerSerializer(data=data)
    # if emailer_serializer.is_valid():
    #     emailer_serializer.save()






def send_dataroom_admin_email_if_user_is_not_exist( sender, new_data,user, dataroom_data,user1,custom_msg):
    # print(sender, new_data,user, dataroom_data,"not exsited")
    token = get_random_string(length=100)
    print('p--------tokennn',token)
    profile = Profile.objects.filter(user_id=sender.get('id')).last()
    profile.user_id = sender.get('id')
    profile.reset_key = token
    profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
    profile.save()
    link="https://stage.docullyvdr.com/projectName/"
    link = link+"password_set/?token="+profile.reset_key
    subject = "Activate & setup password for your DocullyVDR account."
    subject = subject
    to = [user]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    emailerdata=list(User.objects.filter(email__iexact=user.lower()).values())
    # print(emailerdata,"emailerdata")
    non_exist=emailerdata[0]
    # print(non_exist,"emailerdata_from_table")
    # print(user1,"?????????????????????????")
    senderdata=list(User.objects.filter(email=user1).values())
    sender1=senderdata[0]
    ctx = { 
        'non_exist':non_exist,
        'user': user,
        'site_setting': site_settings, 
        'new_data':new_data, 
        'sender1':sender1, 
        'dataroom': dataroom_data,
        'link':link,
        'custom_msg':custom_msg,
    }

    message = get_template('emailer/send_dataroom_admin_email_if_user_is_not_exist.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 4')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    # data = {
    #     'subject':subject, 
    #     'user' : user.id, 
    #     'from_email':from_email, 
    #     'body_html':message, 
    #     'emailer_type': 2, 
    #     'to_email': user.email
    # }
    # emailer_serializer = EmailerSerializer(data=data)
    # if emailer_serializer.is_valid():
    #     emailer_serializer.save()



def send_dataroom_enduser_email_if_user_is_not_exist(user, new_data):
    subject = "Welcome to the Docully Dataroom"
    subject = subject
    to = [user["email"]]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'user': user,
        'site_setting': site_settings, 
        'new_data':new_data
    }

    message = get_template('emailer/send_dataroom_admin_email_if_user_is_not_exist.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 5')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user["id"], 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user["email"]
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()

def send_dataroom_enduser_email_if_user_is_exist(user, new_data):
    subject = "Welcome to the Confliex Dataroom"
    subject = subject
    to = [user["email"]]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'user': user,
        'site_setting': site_settings, 
        'new_data':new_data
    }

    message = get_template('emailer/send_dataroom_admin_email_if_user_exist.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    # print('mail sending working 6')
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
    data = {
        'subject':subject, 
        'user' : user["id"], 
        'from_email':from_email, 
        'body_html':message, 
        'emailer_type': 2, 
        'to_email': user["email"]
    }
    emailer_serializer = EmailerSerializer(data=data)
    if emailer_serializer.is_valid():
        emailer_serializer.save()


def send_80_percent_mail(data, adminto, dataroom,user):
    subject = "Your Data Room has reached 80% of contracted storage limit."
    to = adminto
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        'user': user,
        'site_setting': site_settings,
        'percent': 80
    }

    message = get_template('emailer/send_percent_mail.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email, cc = [constants.site_settings['support_email_id']])
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
    # Make entry of email to inside emailer serialzer # 
   
def send_100_percent_mail(data, adminto, dataroom,user):
    subject = "Your Data Room has reached more than 100% percent of the total storage"
    for i in adminto:
        to = [i]
        from_email = settings.DEFAULT_FROM_EMAIL
        site_settings = SiteSettings.objects.get(id=1)
        ctx = {
            'dataroom': dataroom,
            'user_email':i,
            'site_setting': site_settings,
            'percent': 100
        }

        message = get_template('emailer/send_percent_mail.html').render(ctx)
        msg = EmailMessage(subject, message, to=to, from_email=from_email, cc = [constants.site_settings['support_email_id']])
        msg.content_subtype = 'html'
        msg.send()
        logger.info('mail successfully send')    
    


def send_150_percent_mail(data, dataroom,user,dataroom_storage):
    subject = "[Alert] Data Room Storage Exceeded 150 GB"
    # for i in adminto:
    to = ["varun.k@axat-tech.com"]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        # 'user_email':i,
        'site_setting': site_settings,
        'percent': 150,
        'dataroom_storage':dataroom_storage
    }

    message = get_template('data_documents/lite_dataroom_150gb_mail_to_admin.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email, cc = [constants.site_settings['support_email_id']])
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
    

    


def send_200_percent_mail(data, dataroom,user,dataroom_storage):
    subject = "[Alert] Data Room Storage Exceeded 200 GB"
    # for i in adminto:
    to = ["varun.k@axat-tech.com"]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        # 'user_email':i,
        'site_setting': site_settings,
        'percent': 200,
        'dataroom_storage':dataroom_storage
    }

    message = get_template('data_documents/lite_dataroom_200gb_mail_to_admin.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email, cc = [constants.site_settings['support_email_id']])
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
    


    


def send_250_percent_mail(data, dataroom,user,dataroom_storage):
    subject = "[Alert] Data Room Storage Exceeded 250 GB"
    # for i in adminto:
    to = ["varun.k@axat-tech.com"]
    from_email = settings.DEFAULT_FROM_EMAIL
    site_settings = SiteSettings.objects.get(id=1)
    ctx = {
        'dataroom': dataroom,
        # 'user_email':i,
        'site_setting': site_settings,
        'percent': 250,
        'dataroom_storage':dataroom_storage
    }

    message = get_template('data_documents/lite_dataroom_250gb_mail_to_admin.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email, cc = [constants.site_settings['support_email_id']])
    msg.content_subtype = 'html'
    msg.send()
    logger.info('mail successfully send')    
    
