from users_and_permission.models import *
from dataroom.models import *
import datetime
from data_documents.models import *
from data_documents.serializers import *
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
from dateutil.parser import parse
from django.conf import settings
import logging
from constants import constants
from .models import Emailer, SiteSettings
from .serializers import EmailerSerializer
from userauth.models import *
from userauth.serializers import *
from django.db.models import Count, Min, Sum, Avg
from qna.models import *
from Vote.models import Vote
from django.utils import timezone

logger = logging.getLogger(__name__)

# def send_daily_activity_mail_to_admin_or_la_user(user_data_serialized,folder_activity_data_serialized):
#     subject = "Today’s activity summary on Docully"
#     to = ["himanshu.b@axat-tech.com"]
#     from_email = settings.DEFAULT_FROM_EMAIL
#     site_settings = SiteSettings.objects.get(id=1)
#     ctx = {
#         'upload_data': folder_activity_data_serialized,
#         'user': user_data_serialized,
#         'site_setting': site_settings
#     }

#     message = get_template('emailer/daily_activity_feed.html').render(ctx)
#     msg = EmailMessage(subject, message, to=to, from_email=from_email)
#     msg.content_subtype = 'html'
#     msg.send()
#     logger.info('mail successfully send')    
#     # Make entry of email to inside emailer serialzer # 
#     data = {
#         'subject':subject, 
#         'user' : user_data_serialized.id, 
#         'from_email':from_email, 
#         'body_html':message, 
#         'emailer_type': 1, 
#         'to_email': user_data_serialized.email
#     }
#     emailer_serializer = EmailerSerializer(data=data)
#     if emailer_serializer.is_valid():
#         emailer_serializer.save()





def my_scheduled_job():

    print("cron is working")
    qs = DataroomMembers.objects.filter(is_deleted=False,member__receive_email=True)
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    # print("data usage",DataroomFolder.objects.filter(dataroom_id=199, created_date__range=(today_min, today_max)).aggregate(total_consumed_space = Sum('file_size'))

    # member_list = [i.id for i in qs if i.is_dataroom_admin or i.is_la_user == True]
    member_list = [i.id for i in qs]
    print("member_list",member_list)
    qna_permission = False
    dataroom_free = 0
    upload_data_permission = False
    count = 0
    

    for i in member_list:
        data = {}
        user_role = ""
        # print("i",i)
        dataroom_member = DataroomMembers.objects.get(id=i)
        if dataroom_member.member.id==1581:
            user_check_email = User.objects.filter(id=dataroom_member.member_id,receive_email=True)
            overview=DataroomOverview.objects.filter(dataroom_id=dataroom_member.dataroom_id,send_daily_email_updates=True)
            if user_check_email.exists() and overview.exists():

                dataroom_expiry_check = Dataroom.objects.filter(id=dataroom_member.dataroom_id,is_expired=False,is_request_for_archive=False)
                if dataroom_expiry_check.exists():
                    print("exist dataroom")
                    user_data = User.objects.get(id=dataroom_member.member_id)
                    user_check = User.objects.filter(id=dataroom_member.member_id)
                    upload_data_check = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id)
                    member_permission = DataroomMembers.objects.filter(member_id=dataroom_member.member_id, dataroom_id=dataroom_member.dataroom_id,is_deleted=False).first()
                    try:
                        if dataroom_member.is_dataroom_admin is False:             
                            qna_permission_check = DataroomGroupPermission.objects.filter(dataroom_groups_id=member_permission.end_user_group.first().id, dataroom_id=dataroom_member.dataroom_id).first()
                            if qna_permission_check.is_edit_index:
                                upload_data_permission = True

                            if dataroom_member.is_la_user:
                                user_role = "is_la_user"
                                print(i,"la user qna permission",qna_permission_check.is_q_and_a)
                                print("la user dataroom id",dataroom_member.dataroom_id)
                                if qna_permission_check.is_q_and_a:
                                    qna_permission = True
                                    print("la user",dataroom_member.dataroom_id)
                                    print("la user qna values",QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None).values())
                                    qna_obj = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None)
                                    data['total_questions'] = qna_obj.count()
                                    data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id).exclude(answer=None, qna_id=None).count()
                                    answered = 0
                                    pending = 0
                                    for qna in qna_obj:
                                        answered_count = QuestionAnswer.objects.filter(qna_id=qna.id).count()
                                        if answered_count > 0:
                                            answered += 1
                                        else:
                                            pending += 1
                                    data['answered'] = answered
                                    data['pending'] = pending

                                elif dataroom_member.is_end_user:
                                    user_role = "end_user"
                                    qna_permission = False
                                    print("end_user condition")
                                    print(qna_permission_check.is_q_and_a,"end_user condition permission")
                                else:
                                    print("pass it is admin")
                        try:
                            print("check new admin",dataroom_member.is_dataroom_admin)
                        except Exception as e:
                            print("admin exception",e)
                        if dataroom_member.is_dataroom_admin:
                            print("admin entered in true condition")
                            user_role = "admin"
                            qna_permission = True
                            qna_obj = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None)
                            data['total_questions'] = qna_obj.count()
                            data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id).exclude(answer=None, qna_id=None).count()
                            answered = 0
                            pending = 0
                            for qna in qna_obj:
                                answered_count = QuestionAnswer.objects.filter(qna_id=qna.id).count()
                                if answered_count > 0:
                                    answered += 1
                                else:
                                    pending += 1
                            data['answered'] = answered
                            data['pending'] = pending
                        else:
                            print("pass")


                        if user_check.exists():
                            print("qna data",data)
                            user_data_serialized = UserSerializer(user_data, many=False).data
                            if upload_data_check.exists():
                                upload_data_var = True
                                folder_activity_data = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id,created_date__range=(today_min, today_max))[:2]
                                folder_activity_data_count = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id,created_date__range=(today_min, today_max)).count()
                                folder_activity_data_serialized = FolderuploadinbulkSerializer(folder_activity_data, many=True).data
                            else:
                                folder_activity_data_count = 0
                                folder_activity_data_serialized = None

                            dataroom_storage = Dataroom.objects.filter(id=dataroom_member.dataroom_id)
                                
                            try:
                                try:
                                    if dataroom_storage.exists():
                                        dataroom_storage_one = Dataroom.objects.get(id=dataroom_member.dataroom_id)
                                        total_dataroom_storage  = dataroom_storage_one.dataroom_storage_allocated*1024
                                        dataroom_name = dataroom_storage_one.dataroom_nameFront
                                    try:
                                        dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb'))
                                        trash_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=True, is_folder=False, is_deleted_permanent=False).aggregate(Sum('file_size_mb'))
                                        Vote_consumed = Vote.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=True).aggregate(Sum('file_size_mb'))
                                        DataroomDisclaimer_consumed = DataroomDisclaimer.objects.filter(dataroom_id=dataroom_member.dataroom_id).aggregate(Sum('file_size_mb'))

                                        if dataroom_consumed["file_size_mb__sum"] is None:
                                            dataroom_consumed_storage = 0
                                        else:
                                            dataroom_consumed_storage = round(dataroom_consumed["file_size_mb__sum"])
                                        
                                        if Vote_consumed["file_size_mb__sum"] is None:
                                            Vote_consumed_storage = 0
                                        else:
                                            Vote_consumed_storage = round(Vote_consumed["file_size_mb__sum"])

                                        if DataroomDisclaimer_consumed["file_size_mb__sum"] is None:
                                            DataroomDisclaimer_consumed_storage = 0
                                        else:
                                            DataroomDisclaimer_consumed_storage = round(DataroomDisclaimer_consumed["file_size_mb__sum"])

                                        if trash_consumed["file_size_mb__sum"] is None:
                                            trash_consumed_storage = 0
                                        else:
                                            trash_consumed_storage = round(trash_consumed["file_size_mb__sum"])

                                        totaldataroomcosumed = trash_consumed_storage  + Vote_consumed_storage + DataroomDisclaimer_consumed_storage + dataroom_consumed_storage
                                        dataroom_free = int(total_dataroom_storage) - int(totaldataroomcosumed)
                                    except Exception as e:
                                        print("data storage error",e)
                                        
                                except Exception as e:
                                    print("e")
                                    total_dataroom_storage = 0
                                    dataroom_name = "None"

                                print(user_data_serialized["email"])

                                subject = "Today’s activity summary on Docully for " + dataroom_name + " at " + str(datetime.date.today())
                                to = [user_data_serialized["email"]]
                                # to = ["himanshu.b@axat-tech.com"]
                                print('--------------length',len(folder_activity_data_serialized))
                                from_email = settings.DEFAULT_FROM_EMAIL
                                site_settings = SiteSettings.objects.get(id=1)
                                if data['total_questions'] > 0 and data['total_answer'] > 0 and data['pending'] > 0 and len(folder_activity_data_serialized) > 0:
                                    ctx = {
                                        'count':folder_activity_data_count,
                                        'upload_data': folder_activity_data_serialized,
                                        'user': user_data_serialized,
                                        'total_dataroom_storage':total_dataroom_storage,
                                        # 'dataroom_free':dataroom_free,
                                        'totaldataroomcosumed':totaldataroomcosumed,
                                        'dataroom_name': dataroom_name,
                                        'qna_permission': qna_permission,
                                        'qna_data':data,
                                        'upload_data_permission':upload_data_permission,
                                        'site_setting': site_settings
                                    }


                                    message = get_template('emailer/daily_activity_feed.html').render(ctx)
                                    msg = EmailMessage(subject, message, to=to, from_email=from_email)
                                    msg.content_subtype = 'html'
                                    msg.send()
                                    print('mail successfully send')
                                    print("email send")
                                else:
                                    print("email not send----------------")
                                # Make entry of email to inside emailer serialzer # 
                                # data = {
                                #     'subject':subject, 
                                #     'user' : user_data_serialized["id"], 
                                #     'from_email':from_email, 
                                #     'body_html':message, 
                                #     'emailer_type': 1, 
                                #     'to_email': user_data_serialized["email"]
                                # }
                                # emailer_serializer = EmailerSerializer(data=data)
                                # if emailer_serializer.is_valid():
                                #     emailer_serializer.save()
                            except Exception as e:
                                print("check e-->",e)
                    except Exception as e:
                        print("permission error",qna_permission)
            else:
                pass




def my_scheduled_jobold():

    print("cron is working")
    qs = DataroomMembers.objects.filter(is_deleted=False)
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    # print("data usage",DataroomFolder.objects.filter(dataroom_id=199, created_date__range=(today_min, today_max)).aggregate(total_consumed_space = Sum('file_size'))

    # member_list = [i.id for i in qs if i.is_dataroom_admin or i.is_la_user == True]
    member_list = [i.id for i in qs]
    print("member_list",member_list)
    qna_permission = False
    dataroom_free = 0
    upload_data_permission = False
    count = 0
    

    for i in member_list:
        data = {}
        user_role = ""
        print("i",i)
        dataroom_member = DataroomMembers.objects.get(id=i)
        user_check_email = User.objects.filter(id=dataroom_member.member_id,receive_email=True)
        if user_check_email.exists():
            dataroom_expiry_check = Dataroom.objects.filter(id=dataroom_member.dataroom_id,is_expired=False)
            if dataroom_expiry_check.exists():
                print("exist dataroom")
                user_data = User.objects.get(id=dataroom_member.member_id)
                user_check = User.objects.filter(id=dataroom_member.member_id)
                upload_data_check = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id)
                member_permission = DataroomMembers.objects.filter(member_id=dataroom_member.member_id, dataroom_id=dataroom_member.dataroom_id,is_deleted=False).first()
                try:
                    if dataroom_member.is_dataroom_admin is False:             
                        qna_permission_check = DataroomGroupPermission.objects.filter(dataroom_groups_id=member_permission.end_user_group.first().id, dataroom_id=dataroom_member.dataroom_id).first()
                        if qna_permission_check.is_edit_index:
                            upload_data_permission = True

                        if dataroom_member.is_la_user:
                            user_role = "is_la_user"
                            print(i,"la user qna permission",qna_permission_check.is_q_and_a)
                            print("la user dataroom id",dataroom_member.dataroom_id)
                            if qna_permission_check.is_q_and_a:
                                qna_permission = True
                                print("la user",dataroom_member.dataroom_id)
                                print("la user qna values",QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None).values())
                                qna_obj = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None)
                                data['total_questions'] = qna_obj.count()
                                data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id).exclude(answer=None, qna_id=None).count()
                                answered = 0
                                pending = 0
                                for qna in qna_obj:
                                    answered_count = QuestionAnswer.objects.filter(qna_id=qna.id).count()
                                    if answered_count > 0:
                                        answered += 1
                                    else:
                                        pending += 1
                                data['answered'] = answered
                                data['pending'] = pending

                            elif dataroom_member.is_end_user:
                                user_role = "end_user"
                                qna_permission = False
                                print("end_user condition")
                                print(qna_permission_check.is_q_and_a,"end_user condition permission")
                            else:
                                print("pass it is admin")
                    try:
                        print("check new admin",dataroom_member.is_dataroom_admin)
                    except Exception as e:
                        print("admin exception",e)
                    if dataroom_member.is_dataroom_admin:
                        print("admin entered in true condition")
                        user_role = "admin"
                        qna_permission = True
                        qna_obj = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id, answer=None, qna_id=None)
                        data['total_questions'] = qna_obj.count()
                        data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=dataroom_member.dataroom_id).exclude(answer=None, qna_id=None).count()
                        answered = 0
                        pending = 0
                        for qna in qna_obj:
                            answered_count = QuestionAnswer.objects.filter(qna_id=qna.id).count()
                            if answered_count > 0:
                                answered += 1
                            else:
                                pending += 1
                        data['answered'] = answered
                        data['pending'] = pending
                    else:
                        print("pass")


                    if user_check.exists():
                        print("qna data",data)
                        user_data_serialized = UserSerializer(user_data, many=False).data
                        if upload_data_check.exists():
                            upload_data_var = True
                            folder_activity_data = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id,created_date__range=(today_min, today_max))[:2]
                            folder_activity_data_count = Folderuploadinbulk.objects.filter(dataroom_id=dataroom_member.dataroom_id,created_date__range=(today_min, today_max)).count()
                            folder_activity_data_serialized = FolderuploadinbulkSerializer(folder_activity_data, many=True).data
                        else:
                            folder_activity_data_count = 0
                            folder_activity_data_serialized = None

                        dataroom_storage = Dataroom.objects.filter(id=dataroom_member.dataroom_id)
                            
                        try:
                            try:
                                if dataroom_storage.exists():
                                    dataroom_storage_one = Dataroom.objects.get(id=dataroom_member.dataroom_id)
                                    total_dataroom_storage  = dataroom_storage_one.dataroom_storage_allocated*1024
                                    dataroom_name = dataroom_storage_one.dataroom_nameFront
                                try:
                                    dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb'))
                                    trash_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=True, is_folder=False, is_deleted_permanent=False).aggregate(Sum('file_size_mb'))
                                    Vote_consumed = Vote.objects.filter(dataroom_id=dataroom_member.dataroom_id, is_deleted=True).aggregate(Sum('file_size_mb'))
                                    DataroomDisclaimer_consumed = DataroomDisclaimer.objects.filter(dataroom_id=dataroom_member.dataroom_id).aggregate(Sum('file_size_mb'))

                                    if dataroom_consumed["file_size_mb__sum"] is None:
                                        dataroom_consumed_storage = 0
                                    else:
                                        dataroom_consumed_storage = round(dataroom_consumed["file_size_mb__sum"])
                                    
                                    if Vote_consumed["file_size_mb__sum"] is None:
                                        Vote_consumed_storage = 0
                                    else:
                                        Vote_consumed_storage = round(Vote_consumed["file_size_mb__sum"])

                                    if DataroomDisclaimer_consumed["file_size_mb__sum"] is None:
                                        DataroomDisclaimer_consumed_storage = 0
                                    else:
                                        DataroomDisclaimer_consumed_storage = round(DataroomDisclaimer_consumed["file_size_mb__sum"])

                                    if trash_consumed["file_size_mb__sum"] is None:
                                        trash_consumed_storage = 0
                                    else:
                                        trash_consumed_storage = round(trash_consumed["file_size_mb__sum"])

                                    totaldataroomcosumed = trash_consumed_storage  + Vote_consumed_storage + DataroomDisclaimer_consumed_storage + dataroom_consumed_storage
                                    dataroom_free = int(total_dataroom_storage) - int(totaldataroomcosumed)
                                except Exception as e:
                                    print("data storage error",e)
                                    
                            except Exception as e:
                                print("e")
                                total_dataroom_storage = 0
                                dataroom_name = "None"

                            print(user_data_serialized["email"])

                            subject = "Today’s activity summary on Docully for " + dataroom_name + " at " + str(datetime.date.today())
                            to = [user_data_serialized["email"]]
                            # to = ["himanshu.b@axat-tech.com"]
                            from_email = settings.DEFAULT_FROM_EMAIL
                            site_settings = SiteSettings.objects.get(id=1)

                            ctx = {
                                'count':folder_activity_data_count,
                                'upload_data': folder_activity_data_serialized,
                                'user': user_data_serialized,
                                'total_dataroom_storage':total_dataroom_storage,
                                'dataroom_free':dataroom_free,
                                'dataroom_name': dataroom_name,
                                'qna_permission': qna_permission,
                                'qna_data':data,
                                'upload_data_permission':upload_data_permission,
                                'site_setting': site_settings
                            }


                            message = get_template('emailer/daily_activity_feed.html').render(ctx)
                            msg = EmailMessage(subject, message, to=to, from_email=from_email)
                            msg.content_subtype = 'html'
                            msg.send()
                            logger.info('mail successfully send')
                            print("email send")

                            # Make entry of email to inside emailer serialzer # 
                            # data = {
                            #     'subject':subject, 
                            #     'user' : user_data_serialized["id"], 
                            #     'from_email':from_email, 
                            #     'body_html':message, 
                            #     'emailer_type': 1, 
                            #     'to_email': user_data_serialized["email"]
                            # }
                            # emailer_serializer = EmailerSerializer(data=data)
                            # if emailer_serializer.is_valid():
                            #     emailer_serializer.save()
                        except Exception as e:
                            print("check e-->",e)
                except Exception as e:
                    print("permission error",qna_permission)
        else:
            pass

def tempfile_deletion_job():
        import shutil
        import os
        import stat
        print('crone executing at',datetime.datetime.now())
        date = datetime.datetime.now()
        BulkDownloadstatus.objects.filter().update(is_deleted=True) 
        # os.chdir('/home/cdms_backend/cdms2/mediaa')
        # mkdir(f'abc{date}')
        os.chdir("/home/cdms_backend/cdms2")
        if os.path.exists('media'):
            try:
                print('chchchch767676766666666666666666666666666666666666666667777777777777777777')
                shutil.rmtree('media',ignore_errors=True)
                print('----1')
                try:
                    os.mkdir('media')
                except:
                    pass
                os.chmod('media', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                print('----2')
                # except:
                #     pass
                temp_path2 = os.path.join('media','fileviewcatche')
                print('----3')
                os.mkdir(temp_path2)
                os.chmod('media/fileviewcatche', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            except Exception as e:
                print('---------------eeee',e)
                os.mkdir(os.path.join('media','BBBB'))
        else:
            print('path not exist')
        # print('crone executing at',datetime.datetime.now())
        # BulkDownloadstatus.objects.filter().update(is_deleted=True)   
        # os.chdir("/home/cdms_backend/cdms2")
        # if os.path.exists('media'):
        #   print('chchchch767676766666666666666666666666666666666666666667777777777777777777')
        #   shutil.rmtree('media')
        #   os.makedirs('media')
        #   temp_path2 = os.path.join('media','fileviewcatche')
        #   os.makedirs(temp_path2)
        # else:
        #   print('path not exist')
