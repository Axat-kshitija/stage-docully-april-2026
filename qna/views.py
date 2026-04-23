from django.shortcuts import render
from .models import QuestionAnswer, FAQ
        # from .models import QuestionAnswer
from dataroom import utils as dataroom_utils
from django.conf import settings

from .serializers import QuestionAnswerSerializer, FAQSerializer
from rest_framework.views import APIView
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from data_documents.serializers import ManageDataroomCategoriesSerializer
from data_documents.models import ManageDataroomCategories
import json
from django.http import HttpResponse, Http404, JsonResponse
from users_and_permission.models import DataroomMembers,DataroomGroupFolderSpecificPermissions
from . import utils
from data_documents.models import *
from django.db.models import Max, F
from userauth.models import User_time_zone
from data_documents.utils import convert_to_kolkata

from userauth.models import TokenAuthentication,Token

class AcceptQuestion(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        qna_obj = QuestionAnswer.objects.filter(id=int(request.data)).first()
        qna_obj.final = True
        qna_obj.save()
        return Response({'data': 'Final question added successfully!'}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_201_CREATED)



from data_documents.serializers import CategoriesSerializer
from notifications.models import AllNotifications
# @renderer_classes((TemplateHTMLRenderer, ))
# @csrf_exempt
# @permission_classes((AllowAny, ))
class Create_question(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
    # if request.method == "POST" and request.is_ajax():
        # import pdb;pdb.set_trace();\
        
        user=request.user
        data = request.data
        context_data = {}
        category_id = data['category_id']
        que_title = data['que_title']
        # file_id = data['file_id']
        dataroom_id = pk
        login_user_id = user.id
        # print('8888888888888',request.POST['category_id'],'9999999999999999999999')
        qna_obj = QuestionAnswer.objects.create(user_id=login_user_id, dataroom_id=dataroom_id, question=que_title, category_id=category_id)
        qna_list = QuestionAnswer.objects.filter(dataroom_id=dataroom_id)
        category_list = Categories.objects.all()
        cat_serializer = CategoriesSerializer(category_list, many=True)
        qna_serializer = QuestionAnswerSerializer(qna_list.reverse(), many=True)
        s_qna_serializer = QuestionAnswerSerializer(qna_list.reverse().first(),)
        context_data['category_list'] = cat_serializer.data
        context_data['single_qna'] = s_qna_serializer.data
        context_data['qna_list'] = sorted(qna_serializer.data, key=lambda k: k['created_date'], reverse=True)
        category_obj = ManageDataroomCategories.objects.filter(category_id=category_id, dataroom_id=dataroom_id).first()
        # from . import utils
        from data_documents.utils import send_mail_to_coordinator
        check = Dataroom.objects.filter(id=dataroom_id,notify=True)
        if check.exists():
            send_mail_to_coordinator(qna_obj, category_obj)

        AllNotifications.objects.create(dataroom_id=dataroom_id, user_id=login_user_id,qna=qna_obj)

        # print (context_data,'00000000000000000000')
        # return HttpResponse(json.dumps(context_data), content_type='application/json')
        return Response({'msg':'done'},status=status.HTTP_201_CREATED)
        # return JsonResponse(context_data)





class GetQaReplyView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        question_list = []
        user = request.user
        data = request.data
        question = QuestionAnswer.objects.filter(qna_id=pk)
        qna_serializer_list = QuestionAnswerSerializer(question, many=True)
        for qna_serializer in qna_serializer_list.data:
            category_details = ManageDataroomCategories.objects.filter(category_id=qna_serializer['category']['id'])
            serializer = ManageDataroomCategoriesSerializer(category_details, many=True)
            question_list.append({'question_details': qna_serializer, 'category_details': serializer.data})
        # print('list data +++++++++++++++++>',question_list)
        # import pdb;pdb.set_trace();
        return Response(json.dumps(question_list), status=status.HTTP_201_CREATED)
        # return Response(question_list,status=status.HTTP_201_CREATED)



class UserQnaDetails(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    """docstring for UserQnaDetails"""
    def get(self, request, pk, format=None):
        user = request.user
        data = request.data
        quest = QuestionAnswer.objects.filter(id=pk).first()
        quest_categ = ManageDataroomCategories.objects.filter(category_id = quest.category_id, dataroom_id=quest.dataroom_id).values_list('user_id', flat=True)
        categ = ManageDataroomCategories.objects.filter(dataroom_id=quest.dataroom_id).values_list('user_id', flat=True)
        member = DataroomMembers.objects.filter(dataroom_id=quest.dataroom_id,member_id=user.id).first()
        print(member.is_q_a_user, categ, user.id)
        if member.is_q_a_user == True and  user.id not in categ:
            # print("not in")
            reply = True
        elif user.id == quest.user.id or user.id in quest_categ:
            reply = True
            print("in")
        else:
            reply = False
        #   print("False")
        # print("REPLYYYYYYYY", reply)
        return Response({'reply':reply},status=status.HTTP_201_CREATED)

class QuestionAnswerDetails(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        question_list = []
        user = request.user
        data = request.data
        question = QuestionAnswer.objects.filter(id=pk).first()
        qna_serializer = QuestionAnswerSerializer(question, many=False)
        
        category_details = ManageDataroomCategories.objects.filter(category_id=qna_serializer.data['category']['id'])
        # print(category_details)
        # print(qna_serializer.data['category']['id'])
        serializer = ManageDataroomCategoriesSerializer(category_details, many=True)
        question_list.append({'question_details': qna_serializer.data, 'category_details': serializer.data})
        # import pdb;pdb.set_trace();
        return Response(json.dumps(question_list), status=status.HTTP_201_CREATED)
        # return Response(question_list,status=status.HTTP_201_CREATED)


class QuestionAnswerView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        question_list = []
        user = request.user
        data = request.data
        q_list = []
        members = DataroomMembers.objects.filter(member=user.id,dataroom_id=pk,memberactivestatus=True,is_deleted=False).first()
        permission_member_group = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=pk).values('end_user_group')
        exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id__in=permission_member_group,is_view_only=False,is_no_access=True)]
        count=0
        if members.is_end_user:
            question = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id, qna_id=None, answer=None).exclude(folder__in=exclude_no_access_file)
            count=question.count()
            qna_serializer = QuestionAnswerSerializer(question, many=True).data
            # print("qna_serializer_if",qna_serializer)
            data = sorted(qna_serializer, key=lambda k: k['updated_date'],reverse=True)
            return Response({'data':data , 'size':count}, status=status.HTTP_201_CREATED)
        elif members.is_la_user or members.is_dataroom_admin:
            # categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
            question = QuestionAnswer.objects.filter(dataroom_id=pk, qna_id=None, answer=None).exclude(folder__in=exclude_no_access_file)
            count=question.count()
            qna_serializer = QuestionAnswerSerializer(question, many=True).data
            # print("qna_serializer_else before",qna_serializer)
            data = sorted(qna_serializer, key=lambda k: k['updated_date'],reverse=True)
            # print("qna_serializer_else after",qna_serializer)
            return Response({'data':data,'size':count}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, format=None):
        user = request.user
        data = request.data
        data['dataroom'] = int(pk)
        data['user'] = user.id
        # print("dataaaaaaaa", data)
        serializer = QuestionAnswerSerializer(data=data)
        # print("serializers is valid", serializer.is_valid())
        # print("serializers is valid", serializer.errors)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)


class SendQuestionView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        q_n = QuestionAnswer.objects.filter(id=pk).first()
        if q_n:
            q_n.acc = True
            q_n.reg = False
            q_n.save()
            serializer = QuestionAnswerSerializer(q_n)
        return Response(serializer.data , status=status.HTTP_201_CREATED)


class RegQuestionView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        q_n = QuestionAnswer.objects.filter(id=pk).first()
        if q_n:
            q_n.acc = False
            q_n.reg = True
            q_n.save()
            serializer = QuestionAnswerSerializer(q_n)
        return Response(serializer.data , status=status.HTTP_201_CREATED)


class QAnswerView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        data = request.data
        print("post method q&a",data)
        data['dataroom'] = int(pk)
        data['user'] = user.id
        data.update(QuestionAnswer.objects.filter(id=pk).first().__dict__)
        # print("dataaaaaaaa", data)
        obj_dict = QuestionAnswer.objects.create(user_id=user.id, dataroom_id=data['dataroom_id'], question=data['question'], answer=data['reply'], qna_id=data['id'], folder_id=data['folder_id'], category_id=data['category_id'])
        serializer = QuestionAnswerSerializer(obj_dict, many=False)
        # utils.send_qna_reply_mail(serializer.data)

        data = serializer.data
        # print('data------->',data)
        # print('---',data.get('qna'))
        qna = QuestionAnswer.objects.get(id=data.get('qna'))
        subject = "You have received a reply from "+str(user.first_name)+str(user.last_name)+" on Project "+str(qna.dataroom.dataroom_nameFront)
        to = [qna.user.email]
        # from_email = data.get('user').get('email')

        from constants.constants import backend_ip
        from django.template.loader import render_to_string, get_template
        from django.core.mail import EmailMessage, EmailMultiAlternatives
        ctx = {
            'email': to,
            'subject': subject,
            'data':data,
            'qna':qna,
            'admin_user':user
            }
        # print('ctx-------',ctx)
        # print('---------------------------to',to)
        # print('from email',from_email)

        message = get_template('emailer/replied_question.html').render(ctx)
        # message = "hello world "
        from_email = settings.DEFAULT_FROM_EMAIL

        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        # msg.attach_file(data.path.path)
        msg.content_subtype = 'html'
        msg.send()
        # if serializer.is_valid():
        #   serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_201_CREATED)

import logging
class AddOrRemoveFaq(APIView):
    """docstring for AddOrRemoveFaq"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom_group_id = DataroomMembers.objects.filter(dataroom_id=pk,member_id=user.id).values('end_user_group')
        exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id__in=dataroom_group_id,is_view_only=False,is_no_access=True)]
        faq = FAQ.objects.filter(dataroom=pk, status=True).exclude(folder_id__in=exclude_no_access_file).order_by('-updated_date').order_by('-created_date')
        print(faq)
        count=faq.count()
        serializer = FAQSerializer(faq, many=True)
        return Response({'data':serializer.data,'size':count} , status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        # print("end ====================>")
        # print('faq datttttttttttttaaaaaaaaaaaaaa ',request.data,' faq datttttttttttttaaaaaaaaaaaaaa')
        # print("folder id",request.data.get('folder').get('id'))
        user = request.user
        if(request.data.get('id')=='' or request.data.get('id')==None):
            # print("enter in none conditon")
            serializer = FAQSerializer(data={'file_flag':request.data.get('file_flag'), 'user':request.data.get('user').get('id'),'question':request.data.get('question'),'answer':request.data.get('answer'),'qna':request.data.get('qna'),'folder':request.data.get('folder').get('id'),'is_faq':True,'dataroom':request.data.get('dataroom'),'created_by':request.user.id, 'updated_by':request.user.id})
            if serializer.is_valid():
                serializer.save()
                faq = FAQ.objects.filter(id=serializer.data.get('id')).update( updated_by='')
                faq = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
                serializer = FAQSerializer(faq, many=True)
                return Response(serializer.data , status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_201_CREATED)
        elif(request.data.get('status')):
            # print("status true")
            faq = FAQ.objects.filter(id=request.data.get('id')).update(question = request.data.get('question'),file_flag=request.data.get('file_flag'), answer=request.data.get('answer'), folder_id=request.data.get('folder').get('id'),updated_by=request.user.id)

            faq_data = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
            # print(request.user.id)
            serializer = FAQSerializer(faq_data, many=True)
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        else:
            # print("qna else conditon")
            faq = FAQ.objects.filter(id=request.data.get('id')).update(status = request.data.get('status'),file_flag=request.data.get('file_flag'), folder_id=request.data.get('folder').get('id'),updated_by=request.user.id)

            faq_data = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
            # print(request.user.id)
            serializer = FAQSerializer(faq_data, many=True)
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        # print("end ====================>")
        return Response([] , status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_201_CREATED)

        

class QAnswerReport(APIView):
    """docstring for QAnswerReport"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        data = request.data
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

        obj_dict = QuestionAnswer.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date, qna_id=None, answer=None)
        serializer = QuestionAnswerSerializer(obj_dict, many=True)
        data = serializer.data
        data.sort(key=lambda item:item['created_date'], reverse=True)
        count=len(data)
        return Response({'data':data,'size':count} , status=status.HTTP_201_CREATED)


# class ExportQNA(APIView):
#   """docstring for QAnswerReport"""
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )

#   def get(self, request, pk, format=None):
#       user = request.user
#       data = request.data
#       from_date = request.GET.get('from_date')
#       to_date = request.GET.get('to_date')
#       import datetime
#       todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
#       first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

#       obj_dict = QuestionAnswer.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date, qna_id=None, answer=None)
#       serializer = QuestionAnswerSerializer(obj_dict, many=True)
#       data = serializer.data
#       data.sort(key=lambda item:item['created_date'], reverse=True)
#       from . import utils
#       import csv
#       response = HttpResponse(content_type='text/csv')
#       response['Content-Disposition'] = 'attachment; filename="QNA.csv"'
#       writer = csv.writer(response)

#       header_data, datas = utils.getExcelDataQnaReport(data)

#       writer.writerow(header_data)
#       writer.writerows(datas)
#       return response
        # return Response(serializer.data , status=status.HTTP_201_CREATED)





class ExportQNA(APIView):
    """docstring for QAnswerReport"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        # data = request.data
        data111 = json.loads(request.data)
        # print(data,'this data we get ooooooooooooo')
        # ts = datetime.now().timestamp()
        # file_name = str(data['token'])+'_'+str(ts).split('.')[0]
        # print(request.data,'utururruuuuuuuuuuuuuuuuuuuuuu',data, "HHHHHHHHHH")
        objid=data111['statusid']
        months_count=data111['mohthscount']
        print(months_count,'lllllllllllllllllll------------------------------------------')
        BulkDownloadstatus.objects.filter(id=objid).update(failfilecount=months_count)
        file_name_zip=str(BulkDownloadstatus.objects.filter(id=objid).last().filename.split('.')[0])
        

        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

        obj_dict = QuestionAnswer.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date, qna_id=None, answer=None).order_by('-created_date')
        # serializer = QuestionAnswerSerializer(obj_dict, many=True)
        # data = serializer.data
        # data.sort(key=lambda item:item['created_date'], reverse=True)
        from . import utils
        import csv
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="QNA.csv"'
        # writer = csv.writer(response)
        datarooms = Dataroom.objects.filter(id=pk).last()
        today = datetime.datetime.today()
        if not os.path.exists(f'/home/cdms_backend/cdms2/media/{file_name_zip}'):
            os.mkdir(f'/home/cdms_backend/cdms2/media/{file_name_zip}')

        timez=''
        if User_time_zone.objects.filter(user_id=user.id).exists():
            user_zone=User_time_zone.objects.filter(user_id=user.id).last()
            timez=user_zone.time_zone.tz
        # serializer = DataroomSerializer(datarooms, many=True)
        file_name = str(datarooms.dataroom_nameFront)+' - Q & A Report - '+str(datetime.datetime.strptime( to_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+' -to- '+str(datetime.datetime.strptime( from_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+'.csv'
        row=False
        # header_data, datas = utils.getExcelDataQnaReport(data)
        with open(f'/home/cdms_backend/cdms2/media/{file_name_zip}/{file_name}', 'w',encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not obj_dict.exists():
                writer.writerow(['There is no activity performed in this date range']) 

            else:
                datas = []
                for da in obj_dict: 
                    pending=True
                    header_data = [
                    'Question','Submitted By','Category', 'Status', 'Posted On','File Name', 'Answer', 'Last Response date'
                    ]
                    if row==False:
                        writer.writerow(header_data)

                    print('-------------------1')

                    # for i in count:
                    cou = QuestionAnswer.objects.filter(qna_id=da.id,dataroom_id=pk)
                    for i in cou:
                        dd=DataroomMembers.objects.filter(member_id=i.user.id,dataroom_id=i.dataroom.id,is_deleted=False,is_end_user=False).filter(Q(is_dataroom_admin=True)| Q(is_la_user=True)).exists()
                        if dd:
                        # if count > 0 :
                            pending = False
                        else:
                            pending = True
                    row=True
                    if timez!='':

                        created_date = str(convert_to_kolkata(da.created_date,timez))
                        updated_date = str(convert_to_kolkata(da.updated_date,timez))

                        # created_date = datetime.datetime.strftime(da.created_date,'%Y-%m-%d %H:%M:%S')
                        # updated_date = datetime.datetime.strftime(da.updated_date,'%Y-%m-%d %H:%M:%S')

                    else:
                        created_date = da.created_date
                        updated_date = da.updated_date
                    if pending == True:
                        status = "Unanswered"
                    else:
                        status = "Answered"
                    act = ()
                    # writer.writerow(da.get('question'),da.get('user').get('first_name')+' '+da.get('user').get('last_name'),da.get('category').get('categories_name'), status, created_date+" "+user_zone.time_zone.abbreviation, str(da.get('folder').get('name')), str(da.get('answer')), updated_date+" "+user_zone.time_zone.abbreviation)
                    folder_name='None'
                    if da.folder:
                        folder_name=da.folder.name
                    first_row=False
                    if QuestionAnswer.objects.filter(dataroom_id=pk, qna_id=da.id).exists():
                        answer1=QuestionAnswer.objects.filter(dataroom_id=pk, qna_id=da.id).order_by('-updated_date')
                        for i in answer1:
                            if first_row==False:
                                print('--------------firast rowwww')
                                writer.writerow([da.question, da.user.first_name+' '+da.user.last_name, da.category.categories_name, status, created_date+" "+user_zone.time_zone.abbreviation, str(folder_name), i.user.first_name+':'+i.answer, str(datetime.datetime.strftime(i.updated_date,'%Y-%m-%d %H:%M:%S'))+" "+user_zone.time_zone.abbreviation])
                            else:
                                print('--------------second rowwww')

                                # updated_date = datetime.datetime.strftime(i.updated_date,'%Y-%m-%d %H:%M:%S')
                                writer.writerow(['','','','','','',i.user.first_name+':'+i.answer,str(datetime.datetime.strftime(i.updated_date,'%Y-%m-%d %H:%M:%S'))+" "+user_zone.time_zone.abbreviation])
                            first_row=True    
                    else:
                        print('--------------elseseee')
                        writer.writerow([da.question, da.user.first_name+' '+da.user.last_name, da.category.categories_name, status, created_date+" "+user_zone.time_zone.abbreviation, str(folder_name), 'None', 'None'])
                    # act = act + (da.get('question'),da.get('user').get('first_name')+' '+da.get('user').get('last_name'),da.get('category').get('categories_name'), status, created_date+" "+user_zone.time_zone.abbreviation, str(da.get('folder').get('name')), str(da.get('answer')), updated_date+" "+user_zone.time_zone.abbreviation)
                    # datas.append(act)
                


                # writer.writerow(header_data)
                # writer.writerows(datas)
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
        # BulkDownloadstatus.objects.filter(id=objid)
        from rest_framework import status
        return Response('result', status=status.HTTP_201_CREATED)
        # return response





from django.db.models import Q

class QAnswerAnalytics(APIView):
    """docstring for QAnswerReport"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRR',dataroompermission,user.id,pk)
        if dataroompermission==False:
            data = {}
            members = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id, is_deleted=False).first()
            if members.is_dataroom_admin or members.is_la_user:
                qna_obj = QuestionAnswer.objects.filter(dataroom_id=pk, answer=None, qna_id=None)
                data['total_questions'] = qna_obj.count()
                data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=pk).exclude(answer=None, qna_id=None).count()
            else:
                qna_obj = QuestionAnswer.objects.filter(dataroom_id=pk,user_id=user.id, answer=None, qna_id=None)
                data['total_questions'] = qna_obj.count()
                data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id).exclude(answer=None, qna_id=None).count()
            answered = 0
            pending = 0
            cou=1
            list_ans=[]
            for qna in qna_obj:
                answered_count = QuestionAnswer.objects.filter(qna_id=qna.id)
                if answered_count:
                    for i in answered_count:
                        print('----cou',cou)
                        cou=cou+1
                        dd=DataroomMembers.objects.filter(member_id=i.user.id,dataroom_id=i.dataroom.id,is_deleted=False,is_end_user=False).filter(Q(is_dataroom_admin=True)| Q(is_la_user=True)).count()
                        if dd>0:
                # if answered_count > 0:
                            # answered += 1
                            list_ans.append(i.qna.id)
                # else:
                #     pending += 1

            print('-----------list_ans before',list_ans)
            list_ans = list(set(list_ans))
            print('-----------list_ans after',list_ans)
            answered=len(list_ans)
            pending=qna_obj.count()-len(list_ans)
            data['answered'] = answered
            data['pending'] = pending
            return Response(data , status=status.HTTP_201_CREATED)
        else:
            return Response(None)

class QuestionAnswerFilteringView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk,pk1, format=None):
        question_list = []
        user = request.user
        data = request.data
        q_list = []
        members = DataroomMembers.objects.filter(member=user.id,dataroom_id=pk).first()
        pk1 = int(pk1)
        print(pk1)
        if pk1 == -1:
            categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
            question = QuestionAnswer.objects.filter(dataroom_id=pk,category_id__in=categories, qna_id=None, answer=None)
            # print("questionsssss", question)
            qna_serializer = QuestionAnswerSerializer(question, many=True).data
            return Response(qna_serializer, status=status.HTTP_201_CREATED)
        elif pk1 == 0:
            categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
            answer = QuestionAnswer.objects.filter(dataroom_id=pk,category_id__in=categories).exclude(qna_id=None).values('qna_id')
            question = QuestionAnswer.objects.filter(dataroom_id=pk, id__in=answer, category_id__in=categories)
            # print("questionsssss", question)
            qna_serializer = QuestionAnswerSerializer(question, many=True).data
            return Response(qna_serializer, status=status.HTTP_201_CREATED)
        else:
            if members.is_end_user:
                question = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id,category_id=pk1, qna_id=None, answer=None)
                qna_serializer = QuestionAnswerSerializer(question, many=True).data
                return Response(qna_serializer, status=status.HTTP_201_CREATED)
            elif members.is_la_user or members.is_dataroom_admin:
                # categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
                question = QuestionAnswer.objects.filter(dataroom_id=pk,category_id=pk1, qna_id=None, answer=None)
                # print("questionsssss", question)
                qna_serializer = QuestionAnswerSerializer(question, many=True).data
                return Response(qna_serializer, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
