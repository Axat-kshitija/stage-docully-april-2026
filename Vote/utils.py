from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone 
from constants.constants import *
import pytz
from userauth.models import User
from dataroom.models import Dataroom

logger = logging.getLogger(__name__) 


def date_difference(joined_date,end):
    # current_date = timezone.now()
    current_date =timezone.now()
    current_timezone =timezone.now()
    # print(current_date)
    # print(current_timezone)
    # print(joined_date, 16)
    # print("current_date", current_date, "joined_date", joined_date)
    joined_date = datetime.strptime(joined_date,"%Y-%m-%dT%H:%M:%S")
    end = datetime.strptime(end,"%Y-%m-%dT%H:%M:%S")
    # print("current_date", current_date.replace(tzinfo=None), "joined_date", joined_date.replace(tzinfo=None))
    # current_date = timezone.now()
    # if(current_date.replace(tzinfo=None)>=end.replace(tzinfo=None)):
    #change done to fix the date issue 
    if (current_date >=end):
    	return True
    return False 


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    import datetime
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt

def check_member_in_voters(array, element):
    # print(array, element)
    if array:
        for i in array:

            if i['id'] == element:

                return False
    return True


def getExcelVoterData(data):
    datas = []
    for da in data:
        act = ()
        date1 = ''
        if da.get('date') != '': 
            dateobject1=datetime.strptime(str(da.get('date')),'%Y-%m-%d %H:%M:%S')
            date1=dateobject1.strftime('%d-%m-%Y %H:%M:%S')
        else:
            data1 =da.get('data')

        act = act + (da.get('sr'), da.get('title'),da.get('description'), da.get('name'), da.get('result'), date1)
        datas.append(act)
    header_data = [
        'Sr', 'Vote Title', 'Vote Description', 'Voter Name' , 'Voter Response', 'Date & Time'
    ]
    return header_data, datas


def getExcelVoteData(data):
    datas = []
    for da in data:
        act = ()
        # dateobject1=datetime.strptime(str(da.get('date')),'%Y-%m-%d %H:%M:%S')
        # date1=dateobject1.strftime("%Y-%d-%m %H:%M:%S")
        # dateobject2=datetime.strptime(str(da.get('start')),'%Y-%m-%d %H:%M:%S')
        # start=dateobject2.strftime("%Y-%d-%m %H:%M:%S")
        # dateobject3=datetime.strptime(str(da.get('end')),'%Y-%m-%d %H:%M:%S')
        # end=dateobject3.strftime("%Y-%d-%m %H:%M:%S")



        act = act + (da.get('sr'),da.get('date'), da.get('title'), da.get('description'),da.get('start') ,da.get('end'),da.get('Voters_name'),da.get('Voters_respone'),da.get('vote_date'), da.get('status'))
        datas.append(act)
    header_data = [
        'Sr. No.','Vote creation Date & time', 'Vote Title', 'Vote Description' 
        , 'Start Date of Voting', 
        'End Date of Voting','Voters name','Voters respone','Voting Date & time', 'Status'
    ]
    return header_data, datas


def send_vote_notification(touser,sender, dataroomid, votedata):
    userdata=User.objects.get(id=touser)
    if userdata.notify_recieved:
        dataroomdata=Dataroom.objects.get(id=dataroomid)
        subject = 'Invitation to Vote on Project '+dataroomdata.dataroom_nameFront+' on Docully'
        to = [userdata.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        if votedata.path!='':
            filenametoshow=str(votedata.path.name).split("/")[-1]
        elif votedata.dataroomfile:
            filenametoshow=votedata.dataroomfile.name
        else:
            filenametoshow=''

        ctx = {
            'user':userdata,
            'sender':sender,
            'dataroom_name':dataroomdata.dataroom_nameFront,
            'votedata':votedata,
            'filenametoshow':filenametoshow,
            'email': to,
            'subject': subject,
        }

        message = get_template('userauth/voter_notification.html').render(ctx)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    else:
        pass