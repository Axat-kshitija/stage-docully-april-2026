import urllib.parse
from django.shortcuts import render
from rest_framework.views import APIView
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *
import operator
from django.db.models import Max, F, Min, Q, Sum
try:
    from functools import reduce
except ImportError:  # Python < 3
    pass
from datetime import datetime, timedelta
from azure.storage.blob import BlockBlobService,ContainerPermissions,ContentSettings

from . import utils
from dms.settings import *
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

import json
from users_and_permission.models import DataroomMembers, DataroomGroups, DataroomGroupFolderSpecificPermissions
from users_and_permission.serializers import DataroomMembersSerializer
from django.http import HttpResponse, Http404, JsonResponse
from constants.constants import backend_ip
from data_documents.models import BulkDownloadstatus
from userauth.models import TokenAuthentication,Token,User_time_zone
from data_documents.utils import convert_to_kolkata


class Voting(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        print('------',from_date,'---',to_date)
        todays_date = datetime.strftime(datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.strftime(datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

        vote123=Vote.objects.filter(dataroom_id=776).values('title',
        'vote_created',
        'vote_updated',
        'status',
        'start',
        'end')
        print('------------------',vote123)

        permission_member_group = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=pk).values('end_user_group')
        exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id__in=permission_member_group,is_view_only=False,is_no_access=True)]
        print('---------------perm,',permission_member_group)
        print('----------------',exclude_no_access_file)
        voting_list = Vote.objects.filter(dataroom_id=pk,vote_created__gte=first_date, vote_created__lte=todays_date, status=True).exclude(dataroomfile_id__in=exclude_no_access_file).order_by('-id')
        serializer = VotingListSerializer(voting_list, many=True)
        print(len(serializer.data))

        responseData = []

        from . import utils

        voting_list = Vote.objects.filter(dataroom_id=pk).exclude(dataroomfile_id__in=exclude_no_access_file).order_by('-id')
        serializer = VotingListSerializer(voting_list, many=True)

        member = DataroomMembers.objects.filter(member_id = request.user.id, dataroom_id=pk, is_deleted=False).first()
        members_data = DataroomMembersSerializer(member, many=False).data

        if serializer.data:

            for i in serializer.data:

                # print(i.get('id'),'000000000000000000000000000000')
                temp = utils.date_difference(i.get('start'),i.get('end'))

                if i.get('status'):
                    if temp:
                        Vote.objects.filter(id = i.get('id')).update(status=False)
                    
                    else:
                        Vote.objects.filter(id = i.get('id')).update(status=True)

                
                voting_result = VotingResult.objects.filter(member_id=members_data.get('id'), vote_id=i.get('id')).first()
                print(voting_result)
                serializer_1 = VotingDetailsSerializer(voting_result,many=False)
            
                # print(serializer_1,'111111111111111111111111')
            
                if members_data.get('is_dataroom_admin') or members_data.get('is_la_user'):
                    i['view'] = True
                    i['edit'] = True
                    i['is_voter'] = True # all admin able to vote is set true
                    print('oooooooooooooo',serializer_1.data.get('result'))
                    if serializer_1.data.get('result'):
                        i['is_voter'] = False
                    i['manage_member'] = True
                    print("iiiiiiiiiiiiiiiiiii",i)
                    i['vote']=serializer_1.data
                    responseData.append(i)
                else:
                    # print("end_user")
                    i['view'] = True
                    i['edit'] = True
                    if serializer_1.data.get('result'):
                        i['is_voter'] = False
                    else:
                        if i.get('status'):
                            i['is_voter'] = True
                        else:
                            i['is_voter'] = False

                    i['manage_member'] = True
                    i['vote']=serializer_1.data
                    # print(i.get('vote_created_by').get('id'), request.user.id,'RRRRRRRRRRRRRRRRRRRRRRRRR')
                    print(i['vote'].get('id'),"check",i['vote'].get('id') is not None,"---------",i.get('status'),"===",temp)
                    ### now closed vote also needed
                    # if i['vote'].get('id') and i.get('status') and not temp:
                    #######
                    if i['vote'].get('id') and i.get('status') and not temp:
                        # print("adding",i['vote'].get('id'),"---------",i.get('status'),"===",temp)
                        responseData.append(i)
                    elif i['vote'] is not None and not i.get('status') and temp:
                        # print("adding",i['vote'].get('id'),"---------",i.get('status'),"===",temp)
                        responseData.append(i)
                    else:
                        pass
                    # elif i.get('vote_created_by').get('id')==request.user.id:
                    #   print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                    #   responseData.append(i)

                i['end'] = datetime.strptime(i['end'],"%Y-%m-%dT%H:%M:%S")
                i['start'] = datetime.strptime(i['start'],"%Y-%m-%dT%H:%M:%S")

        count=len(responseData)
        return Response({'data':responseData,'size':count}, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        print(request.data,'THid is vote dataaaaaaaaaaaaaaaaaaaaa')


        dataroom_filess = request.FILES.getlist('file')
        # print(dataroom_filess)
        # for i, dataroom_files in enumerate(dataroom_filess):
        from dateutil.parser import parse
        import pytz
        data = json.loads(request.data.get('data'))
        user = request.user
        voting_data =data 
        # voting_data =json.dumps(voting_data)
        voting_data['vote_created_by'] = user.id
        voting_data['dataroom'] = int(pk)
        # voting_data['end'] = voting_data['end']
        voting_data['path'] = dataroom_filess[0] if len(dataroom_filess)>0 else None
        # print(timezone.now())
        tempppt=request.data.getlist('dataroomfile')
        # print(tempppt)
        if tempppt:
            voting_data['dataroomfile']=tempppt[0]
        temp1=request.data.getlist('file_size')
        # print(temp1)
        if temp1:

            voting_data['file_size']=temp1[0]

        # print(datetime.datetime.strptime(voting_data['end'],"%Y-%m-%dT%H:%M:%S"))
        from datetime import datetime, timedelta
        ###To Format End Date
        end = voting_data['end']
        end = parse(end)
        end = end.replace(tzinfo=None)

        ###To Format Start Date
        nowtime=datetime.now()
        hours = 5
        hours_added = timedelta(hours = hours)
        nowtime=datetime.strptime(str(nowtime),"%Y-%m-%d %H:%M:%S.%f")
        nowtime = nowtime - hours_added

        start = voting_data['start']
        start = parse(start)
        start = start.replace(tzinfo=None)

        start = utils.convert_datetime_timezone(str(start), "UTC","Asia/Kolkata")
        end = utils.convert_datetime_timezone(str(end), "UTC","Asia/Kolkata")
        start=datetime.strptime( start, '%Y-%m-%d %H:%M:%S')
        end=datetime.strptime( end, '%Y-%m-%d %H:%M:%S')
        if start>nowtime and end>nowtime:
            # print(start,'RRRRRRRRR',type(start))
            # print(end,'YYYYYYYY',type(end))
            # print(nowtime,'UUUUUUUU',type(nowtime))
            if data['groups']:
                    try:
                        for i in data['groups']:
                            print(data['groups'])
                            print(i['member'])

                            if i['member']:

                                for j in i['member']:
                                    if utils.check_member_in_voters(voting_data['voters'], j['data']['id']):
                                        voting_data['voters'].append(j['data'])
                                        print(voting_data['voters'],'vvvvvvvvvvvvvvvv')


                    except TypeError:
                        print (data['groups'])

            if voting_data.get('id')=='' or voting_data.get('id')==None:
                serializer = VotingSerializer(data=voting_data)
                # print ("serializer is valid", serializer.is_valid())
                # print ("serializer errors ", serializer.errors)
                if serializer.is_valid():
                    serializer.save()
                    Vote.objects.filter(id =serializer.data.get('id')).update(end=end, start=start )
                    # print(voting_data['voters'])
                    if voting_data['voters']:
                        print(voting_data['voters'])
                        for k in voting_data['voters']:
                            print(k)

                            dataroommeber = DataroomMembers.objects.filter(member_id=k['id'], is_deleted=False, dataroom_id=pk)
                            if(k['id'] !=request.user.id):
                                dataRoomMember = DataroomMembersSerializer(dataroommeber,many=True).data
                                voters_data = {'created_by':request.user.id, 'vote':serializer.data.get('id'), 'member':dataRoomMember[0].get('id'), 'dataroom':pk}

                                serializer_1 = VotingDetailsSerializer(data=voters_data)
                                if serializer_1.is_valid():
                                    serializer_1.save()
                                    votedataa=Vote.objects.get(id=serializer.data['id'])

                                    block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
                                    try:
                                        import os
                                        from data_documents.views import convert_to
                                        import PyPDF2
                                        os.chdir('/home/cdms_backend/cdms2/media')
                                        pathsplit=(votedataa.path.url).split('/')
                                        container_name='docullycontainer'
                                        pathu="voting/vote/"+pathsplit[-1].replace("%20", " ")
                                        block_blob_service.get_blob_to_path(container_name, pathu, pathsplit[-1])
                                        
                                        # print(pathu,pathsplit[-1],"pathu")
                                        ext=pathsplit[-1].split('.')
                                        ext=ext[-1]
                                        if ext=='pdf' or ext=='PDF':
                                            with open(pathsplit[-1], 'rb') as fileee:
                                                pdfReader = PyPDF2.PdfReader(fileee,strict=False)
                                                pn = len(pdfReader.pages)
                                                votedataa.pages = pn
                                                votedataa.save()

                                        else:
                                            with open(pathsplit[-1], 'rb') as ifh:
                                                read_data=ifh.read()
                                                with open("/home/cdms_backend/cdms2/DocFile_server/"+pathsplit[-1], 'wb') as fileee:
                                                    fileee.write(read_data)
                                                    # print("yes done pptx")
                                            convert_to('/home/cdms_backend/cdms2/server_DocFile/',  "/home/cdms_backend/cdms2/DocFile_server/"+pathsplit[-1])
                                            fileext=pathsplit[-1].split('.')
                                            # fileext.pop(-1)
                                            fileext[-1]='pdf'
                                            fileext='.'.join(fileext)
                                            with open("/home/cdms_backend/cdms2/server_DocFile/"+fileext, 'rb') as fileee:
                                                pdfReader = PyPDF2.PdfReader(fileee,strict=False)
                                                pn = len(pdfReader.pages)
                                                votedataa.pages = pn
                                                votedataa.save()

                                    except Exception as e:
                                        print('----------------------voteee expppp',e)
                                    utils.send_vote_notification(k['id'],user,pk,votedataa)

            else:
                voting_list = Vote.objects.filter(id= voting_data.get('id')).update(description = voting_data.get('description'), title = voting_data.get('title'))

            voting_list = Vote.objects.filter(dataroom_id=pk)
            serializer = VotingListSerializer(voting_list, many=True)
            # print(serializer.data,'rnew')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

            # return Response(data, status=status.HTTP_201_CREATED)

class MakeVote(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        from datetime import datetime, timedelta
        from dateutil.parser import parse
        import datetime,pytz

        current_date=datetime.datetime.utcnow()
        date_in_utc=current_date.replace(tzinfo=pytz.UTC)
        vote_date=date_in_utc.astimezone(pytz.timezone("Asia/Kolkata"))
        voting_result = VotingResult.objects.filter(id=request.data.get('id')).update(result=request.data.get('result'), vote_date = vote_date)

        return Response('Thank You for Vote!', status=status.HTTP_201_CREATED)


class VoteResult(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):

        responseData = []
        voting_result = VotingResult.objects.filter(vote_id=pk)
        serializer = VotingDetailsSerializer(voting_result,many=True)
        if serializer.data:
            for i in serializer.data:
                # print(i.get('member'))
                DataroomMemberObject = DataroomMembers.objects.filter(id=i['member']).first()
                dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data
                # print(dataRoomMember)
                responseData.append({
                    'result':i.get('result') if i.get('result') !=None else 'No Response',
                    'name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
                    'vote_date':i.get('vote_date'),
                    'id':i.get('id'),
                    'status':i.get('status'),
                    'title':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name'))})
                # responseData.append(dataRoomMember)

        return Response(responseData, status=status.HTTP_201_CREATED)

class AddVoter(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, pk2, format=None):

        voting_data = request.data
        data = {'exist':0,'new':0}
        for k in voting_data:

            dataroommeber = DataroomMembers.objects.filter(member_id=k['id'], is_deleted=False, dataroom_id=pk)
            dataRoomMember = DataroomMembersSerializer(dataroommeber,many=True).data

            voters_data = {'created_by':request.user.id, 'vote':int(pk2), 'member':dataRoomMember[0].get('id'), 'dataroom':int(pk)}
            Data = VotingResult.objects.filter(member_id=dataRoomMember[0].get('id'), vote_id=int(pk2)).first()
            serializer_result = VotingDetailsSerializer(Data, many=False).data
            # print(serializer_result, 23223)
            if serializer_result.get('member')==None:
                data['new']+=1
                serializer_1 = VotingDetailsSerializer(data=voters_data)
                if serializer_1.is_valid():
                    serializer_1.save()
            else:
                data['exist']+=1

        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request, pk, pk2, format=None):

        message = {'message':'Voter Successfully Restored'}
        Data = VotingResult.objects.filter(id=int(pk2)).first()
        serializer_result = VotingDetailsSerializer(Data, many=False).data
        if serializer_result:
            voter_status = False if serializer_result.get('status')==True else True
            if voter_status==False:
                message['message'] = 'Voter Successfully Removed, You can Restored Voter by using restore'
            VotingResult.objects.filter(id=int(pk2)).update(status=voter_status)

        return Response(message, status=status.HTTP_201_CREATED)


class ExportVoterStatusReport(APIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        import datetime
        data = []
        from dateutil import tz
        from datetime import datetime, timedelta
        to_zone = tz.gettz('Asia/Kolkata')
        voting_result = VotingResult.objects.filter(vote_id=pk).order_by('-id')
        serializer = VotingDetailsSerializer(voting_result,many=True)
        timez=''
        if User_time_zone.objects.filter(user_id=user.id).exists():
            user_zone=User_time_zone.objects.filter(user_id=user.id).last()
            timez=user_zone.time_zone.tz
        if serializer.data:
            count = 0
            for i in serializer.data:

                # utc = datetime.strptime(str(i.get('vote_date')), '%Y-%m-%dT%H:%M:%S.%f')
                # central = utc.astimezone(to_zone)
                # tmpDatetime = central.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
                tmpDatetime = datetime.strptime(str(i.get('vote_date')), '%Y-%m-%dT%H:%M:%S.%f')
                tmpDatetime = convert_to_kolkata(tmpDatetime,timez)
                tmpDatetime = datetime.strftime(tmpDatetime, '%Y-%m-%dT%H:%M:%S')

                # print(i.get('member'))
                count = count+1
                serializerVote = VotingSerializer(Vote.objects.filter(id=i.get('vote')).first(),many=False)
                # print(serializerVote.data.get('title'),serializerVote.data.get('path'),serializerVote.data.get('description'))
                DataroomMemberObject = DataroomMembers.objects.filter(id=i['member']).first()
                dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data
                data.append({'result':i.get('result') if i.get('result') !=None else 'Did not vote',
                    'name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
                    'date':tmpDatetime if i.get('result') !=None else '' ,
                    'sr':count,
                    'description':serializerVote.data.get('description'),
                    'path':str(backend_ip)+''+serializerVote.data.get('path') if serializerVote.data.get('path')!=None else '',
                    'title':serializerVote.data.get('title')})


        # data.sort(key=lambda item:item['date'], reverse=True)
        from . import utils
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        writer = csv.writer(response)

        header_data, datas = utils.getExcelVoterData(data)

        writer.writerow(header_data)
        writer.writerows(datas)
        # print(response)
        return response

# class ExportVoteReport(APIView):

#     """docstring for ActivitybyDateReport"""
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def get(self, request, pk, format=None):
#         user = request.user
#         from dateutil import tz
#         from datetime import datetime, timedelta
#         to_zone = tz.gettz('Asia/Kolkata')
#         data = []
#         voting_list = Vote.objects.filter(dataroom_id=pk).order_by('-id')
#         serializer = VotingListSerializer(voting_list, many=True)
#         print('111111111111111111111')
#         if serializer.data:
#             print('2222222222222')
#             count = 0
#             for i in serializer.data:
#                 print('33333333333333333333')
#                 count +=1
#                 # utc = datetime.strptime(str(i.get('vote_created')), '%Y-%m-%dT%H:%M:%S.%f')
#                 # central = utc.astimezone(to_zone)
#                 # tmpDatetime = central.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
#                 date1 = datetime.strptime(str(datetime.strptime(str(i.get('vote_created')),"%Y-%m-%dT%H:%M:%S.%f")), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
#                 start = datetime.strptime(str(datetime.strptime(str(i.get('start')),"%Y-%m-%dT%H:%M:%S")), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
#                 end = datetime.strptime(str(datetime.strptime(str(i.get('end')),"%Y-%m-%dT%H:%M:%S")), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')               
#                 voting_result = VotingResult.objects.filter(vote_id=i.get('id'))
#                 result_serializer = VotingDetailsSerializer(voting_result,many=True)
#                 ttt=0
#                 print(result_serializer.data)
#                 if result_serializer.data:                      
#                     for j in result_serializer.data:
#                         print('44444444444444444')
#                         DataroomMemberObject = DataroomMembers.objects.filter(id=j['member']).first()
#                         dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data
#                         vote_date1 = datetime.strptime(str(datetime.strptime(str(j.get('vote_date')),"%Y-%m-%dT%H:%M:%S.%f")), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
#                         if ttt==0:
#                             data.append({
#                                 'description':i.get('description'),
#                                 'title':i.get('title') if i.get('title') !=None else 'Blank',
#                                 'end':end,
#                                 'start':start,
#                                 'date':date1,
#                                 'sr':count,
#                                 'Voters_respone':j.get('result') if j.get('result') !=None else 'No Response',
#                                 'Voters_name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
#                                 'vote_date':vote_date1,
#                                 'status':'Open' if i.get('status')==True else 'Close'})
#                         else:
#                             data.append({
#                                 'description':'',
#                                 'title':'',
#                                 'end':'',
#                                 'start':'',
#                                 'date':'',
#                                 'sr':'',
#                                 'Voters_respone':j.get('result') if j.get('result') !=None else 'No Response',
#                                 'Voters_name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
#                                 'vote_date':vote_date1,
#                                 'status':'Open' if i.get('status')==True else 'Close'})
#                         ttt=1
#                 else:
#                             data.append({
#                                 'description':i.get('description'),
#                                 'title':i.get('title') if i.get('title') !=None else 'Blank',
#                                 'end':end,
#                                 'start':start,
#                                 'date':date1,
#                                 'sr':count,
#                                 'Voters_respone':'',
#                                 'Voters_name':'',
#                                 'vote_date':'',
#                                 'status':'Open' if i.get('status')==True else 'Close'})
#         # data.sort(key=lambda item:item['date'], reverse=False)
#         from . import utils
#         import csv
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
#         writer = csv.writer(response)

#         header_data, datas = utils.getExcelVoteData(data)

#         writer.writerow(header_data)
#         writer.writerows(datas)
#         # print(response)
#         return response








class ExportVoteReport(APIView):

    """docstring for ActivitybyDateReport"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        from dateutil import tz
        from datetime import datetime, timedelta

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
        

        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        to_zone = tz.gettz('Asia/Kolkata')
        data = []
        voting_list = Vote.objects.filter(dataroom_id=pk).order_by('-id')
        serializer = VotingListSerializer(voting_list, many=True)
        print('111111111111111111111')
        timez=''
        if User_time_zone.objects.filter(user_id=user.id).exists():
            user_zone=User_time_zone.objects.filter(user_id=user.id).last()
            timez=user_zone.time_zone.tz
        if serializer.data:
            print('2222222222222')
            count = 0
            for i in serializer.data:
                print('33333333333333333333')
                count +=1
                # utc = datetime.strptime(str(i.get('vote_created')), '%Y-%m-%dT%H:%M:%S.%f')
                # central = utc.astimezone(to_zone)
                # tmpDatetime = central.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
                date1 = datetime.strptime(str(datetime.strptime(str(i.get('vote_created')),"%Y-%m-%dT%H:%M:%S.%f")), '%Y-%m-%d %H:%M:%S.%f')
                start = datetime.strptime(str(datetime.strptime(str(i.get('start')),"%Y-%m-%dT%H:%M:%S")), '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(str(datetime.strptime(str(i.get('end')),"%Y-%m-%dT%H:%M:%S")), '%Y-%m-%d %H:%M:%S')
                voting_result = VotingResult.objects.filter(vote_id=i.get('id'))
                result_serializer = VotingDetailsSerializer(voting_result,many=True)
                ttt=0
                print(result_serializer.data)

                if result_serializer.data:                      
                    for j in result_serializer.data:
                        print('44444444444444444')
                        DataroomMemberObject = DataroomMembers.objects.filter(id=j['member']).first()
                        dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data
                        vote_date1 = datetime.strptime(str(datetime.strptime(str(j.get('vote_date')),"%Y-%m-%dT%H:%M:%S.%f")), '%Y-%m-%d %H:%M:%S.%f')
                        if ttt==0:
                            end = convert_to_kolkata(end,timez)
                            start = convert_to_kolkata(start,timez)
                            date1 = convert_to_kolkata(date1,timez)
                            end=datetime.strftime(end,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            start=datetime.strftime(start,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            date1=datetime.strftime(date1,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            vote_date1 = convert_to_kolkata(vote_date1,timez)
                            vote_date1 = datetime.strftime(vote_date1,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            data.append({
                                'description':i.get('description'),
                                'title':i.get('title') if i.get('title') !=None else 'Blank',
                                'end':end,
                                'start':start,
                                'date':date1,
                                'sr':count,
                                'Voters_respone':j.get('result') if j.get('result') !=None else 'No Response',
                                'Voters_name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
                                'vote_date':vote_date1,
                                'status':'Open' if i.get('status')==True else 'Close'})
                        else:
                            vote_date1 = convert_to_kolkata(vote_date1,timez)
                            vote_date1 = datetime.strftime(vote_date1,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            data.append({
                                'description':'',
                                'title':'',
                                'end':'',
                                'start':'',
                                'date':'',
                                'sr':'',
                                'Voters_respone':j.get('result') if j.get('result') !=None else 'No Response',
                                'Voters_name':str(dataRoomMember.get('member').get('first_name'))+' '+str(dataRoomMember.get('member').get('last_name')),
                                'vote_date':vote_date1,
                                'status':'Open' if i.get('status')==True else 'Close'})
                        ttt=1
                else:
                            end = convert_to_kolkata(end,timez)
                            start = convert_to_kolkata(start,timez)
                            date1 = convert_to_kolkata(date1,timez)
                            end=datetime.strftime(end,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            start=datetime.strftime(start,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            date1=datetime.strftime(date1,'%d-%m-%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                            data.append({
                                'description':i.get('description'),
                                'title':i.get('title') if i.get('title') !=None else 'Blank',
                                'end':end,
                                'start':start,
                                'date':date1,
                                'sr':count,
                                'Voters_respone':'',
                                'Voters_name':'',
                                'vote_date':'',
                                'status':'Open' if i.get('status')==True else 'Close'})
        # data.sort(key=lambda item:item['date'], reverse=False)
        datarooms = Dataroom.objects.filter(id=pk).last()
        if not os.path.exists(f'/home/cdms_backend/cdms2/media/{file_name_zip}'):
            os.mkdir(f'/home/cdms_backend/cdms2/media/{file_name_zip}')

        import datetime
        # serializer = DataroomSerializer(datarooms, many=True)
        file_name = str(datarooms.dataroom_nameFront)+' - Voting Report - '+str(datetime.datetime.strptime( to_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+' -to- '+str(datetime.datetime.strptime( from_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+'.csv'
       
        from . import utils
        import csv
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        # writer = csv.writer(response)

        header_data, datas = utils.getExcelVoteData(data)
        with open(f'/home/cdms_backend/cdms2/media/{file_name_zip}/{file_name}', 'w',encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if data == []:
                writer.writerow(['There is no activity performed in this date range']) 

            else:
                writer.writerow(header_data)
                writer.writerows(datas)
        # print(response)
        # return response
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
        # BulkDownloadstatus.objects.filter(id=objid)
        return Response('result', status=status.HTTP_201_CREATED)

















class VoteCountAnalysis(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        responseData = {}

        voting_list = Vote.objects.filter(id=pk).order_by('-id').first()
        serializer = VotingListSerializer(voting_list, many=False)

        Yes = VotingResult.objects.filter(vote_id=pk, result='Yes').count()
        No = VotingResult.objects.filter(vote_id=pk, result='No').count()
        Neutral = VotingResult.objects.filter(vote_id=pk, result='Neutral').count()
        All = VotingResult.objects.filter(vote_id=pk).count()
        responseData['no'] = No
        responseData['yes'] = Yes
        responseData['neutral'] = Neutral
        responseData['no_response'] = All-No-Yes-Neutral
        responseData['title'] = serializer.data.get('title')

        return Response(responseData, status=status.HTTP_201_CREATED)

class UploadVotingAttachment(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk, format=None):
        user = request.user
        voting_pic = request.FILES.getlist('voting_attachment')
        return Response(data)

class VoterGroupApi(APIView):
    authentication_classes = (TokenAuthentication, )

    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        voting_group_list = VoterGroup.objects.filter(dataroom=pk, status=True)
        # print(voting_group_list,"voting_group_list")
        serializer = VoterGroupSerializerList(voting_group_list, many=True)
        if serializer.data:
            for i in serializer.data:
                voting_group_list = VoterGroupMember.objects.filter(votergroup_id=i.get('id'))
                serializer_1 = VoterGroupMemberListSerializer(voting_group_list, many=True)
                i['member'] = serializer_1.data
                if i['member']:
                    for j in i['member']:
                        dataroom_member_data = DataroomMembers.objects.filter(id=j['member'])
                        dataroom_member_serializer = DataroomMembersSerializer(dataroom_member_data, many=True)
                        # print(dataroom_member_serializer.data[0])
                        j['data'] = dataroom_member_serializer.data[0].get('member')
                        # j['member'] = dataroom_member_serializer.data

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        voter_group = data
        voter_group['created_by'] = user.id

        if data.get('id')=='' or data.get('id')==None:
            serializer = VoterGroupSerializer(data=voter_group)
            # print ("serializer is valid", serializer.is_valid())
            # print ("serializer errors ", serializer.errors)       
            if serializer.is_valid():
                serializer.created_by = request.user.id
                serializer.dataroom = pk
                serializer.save()

                if 'member' in data:
                    for i in data['member']:

                        DataroomMemberObject = DataroomMembers.objects.filter(member_id=i.get('id')).first()
                        dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data


                        serializer_1 = VoterGroupMemberSerializer(data={'votergroup':serializer.data.get('id'),'member':dataRoomMember.get('id')})
                        # print ("serializer is valid", serializer_1.is_valid())
                        # print ("serializer errors ", serializer_1.errors)
                        if serializer_1.is_valid():
                            serializer_1.save()
                
                voting_group_list = VoterGroup.objects.filter(dataroom=pk, status=True)
                serializer = VoterGroupSerializerList(voting_group_list, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif data.get('status'):
            voter_group = VoterGroup.objects.filter(id=data.get('id')).update(title=data.get('title'), description = data.get('description'))
            voting_group_list = VoterGroup.objects.filter(dataroom=pk, status=True)
            serializer = VoterGroupSerializerList(voting_group_list, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            voter_group = VoterGroup.objects.filter(id=data.get('id')).update(status=False)
            voting_group_list = VoterGroup.objects.filter(dataroom=pk, status=True)
            serializer = VoterGroupSerializerList(voting_group_list, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(data, status=status.HTTP_201_CREATED)

class VoterGroupMemberApi(APIView):
    authentication_classes = (TokenAuthentication, )

    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print(pk)
        voting_group_list = VoterGroupMember.objects.filter(votergroup_id=pk)
        # print(voting_group_list)
        serializer = VoterGroupMemberListSerializer(voting_group_list, many=True)
        for i in serializer.data:
            dataroom_member_data = DataroomMembers.objects.filter(id=i['member']).first()
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member_data, many=False)
            i['data'] = dataroom_member_serializer.data.get('member')
            i['date'] = i['created_date']
            i['title'] = dataroom_member_serializer.data.get('member').get('first_name')+' '+dataroom_member_serializer.data.get('member').get('last_name')
            i['email'] = dataroom_member_serializer.data.get('member').get('email')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        # voter_member = {'member':104,'votergroup':pk}
        # print(data)
        responseData = {'exist':0,'new':0}
        for i in data:

            count = 0
            DataroomMemberObject = DataroomMembers.objects.filter(member_id=i['id']).first()
            dataRoomMember = DataroomMembersSerializer(DataroomMemberObject,many=False).data

            voterSerializer = VoterGroupMember.objects.filter(member_id=dataRoomMember.get('id'), votergroup_id = pk).first()


            serializer_1 = VoterGroupMemberSerializer(voterSerializer, many=False)
            # print(serializer_1.data)
            if serializer_1.data.get('votergroup'):
                responseData['exist'] +=1
            else:
                responseData['new'] +=1
                from datetime import datetime, timedelta
                from dateutil.parser import parse
                import datetime,pytz

                current_date=datetime.datetime.utcnow()
                date_in_utc=current_date.replace(tzinfo=pytz.UTC)
                member_add_date=date_in_utc.astimezone(pytz.timezone("Asia/Kolkata"))

                voter_member = {'member':dataRoomMember.get('id'),'votergroup':pk}

                serializer = VoterGroupMemberSerializer(data=voter_member)
                # print ("serializer is valid", serializer.is_valid())
                # print ("serializer errors ", serializer.errors)       
                if serializer.is_valid():
                    # print(33434)
                    serializer.save()
                    VoterGroupMember.objects.filter(id=serializer.data.get('id')).update(created_date = member_add_date)
        
        return Response(responseData, status=status.HTTP_201_CREATED)

class DelVoterGroupMember(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):

        message = {'message':'Member Successfully Restored'}
        Data = VoterGroupMember.objects.filter(id=int(pk)).first()
        serializer_result = VoterGroupMemberSerializer(Data, many=False).data
        if serializer_result:
            # print(serializer_result)
            voter_status = False if serializer_result.get('status')==True else True
            if voter_status==False:
                message['message'] = 'Member Successfully Removed, You can Restored Member by using restore'
            VoterGroupMember.objects.filter(id=int(pk)).update(status=voter_status)

        return Response(message, status=status.HTTP_201_CREATED)

class MemberVoting(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def get(self, request, pk, format=None):
        return Response([], status=status.HTTP_201_CREATED)
        voting_details = VotingResult.objects.filter(dataroom_id=pk)
        # print(voting_group_list)
        serializer = VotingDetailsListSerializer(voting_details, many=True)
        # print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        vote = {'vote':5,'member':99,'result':'Neutral','description':'I am very happy','dataroom':pk,'created_by':user.id}
        serializer = VotingDetailsSerializer(data=vote)
        # print ("serializer is valid", serializer.is_valid())
        # print ("serializer errors ", serializer.errors)       
        if serializer.is_valid():
            # print(33434)
            serializer.save()
            voting_group_list = VotingResult.objects.filter(dataroom_id=pk,member_id=99)
            serializer = VotingDetailsListSerializer(voting_group_list, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({}, status=status.HTTP_201_CREATED)


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, ))
# @authentication_classes((TokenAuthentication,))
@permission_classes((AllowAny, ))
def file_view(request, pk, pk1):

    # print("this api is calling")
    activity_list = []
    context_data = {}
    from constants import constants
    base_url = "http://52.172.204.103:8000"
    frontend_url = "http://52.172.204.103"
    data = Vote.objects.filter(id=pk).first()
    # print(data,'rusikesh')
    current2=datetime.now()
    # print(current2,"current2=datetime.now()")
    conversion_path=str(data.path.url)
    # print(conversion_path,"con path")
    path = str(data.path)
    dpath = str(data.path)
    docs = False
    odf = False
    csv = False
    pdf = False
    excel = False
    psd = False
    pptx = False
    png = False
    message = ''
    user = User.objects.get(id=pk1)
    if request.accepted_renderer.format == 'html':
        if path.endswith('.odt') or path.endswith('.pdf') or path.endswith('.ods') or path.endswith('.odp'):
            odf = True
            path = str(data.path.url)
            dpath = path 
            if path.endswith('.pdf'):
                pdf = True
        elif path.endswith('.csv'):
            csv = True
            path = str(data.path.url)
            dpath = path
        elif path.endswith('.xlsx') or path.endswith('.xls'):
            excel = True
            path = str(data.path.url)
            dpath = path
        elif path.endswith('.docx') or path.endswith('.doc'):
            # print("in docs condition")
            docs = True
            path = str(data.path.url)
            dpath = path
        elif path.endswith('.ppt') or path.endswith('.pptx'):
            pptx = True
            path = str(data.path.url)
            dpath = path
            # print(dpath,'pptpathnew')

        elif path.endswith('.psd'):
            psd = True
        elif path.endswith('.png'):
            png = True
            path = str(data.path.url)
            dpath = path
        else:
            path = str(data.path.url)
            dpath = path



                # if path.endswith('.pdf'):
                #   block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==')
                #   container_name ='docullycontainer'
                #   path_name = path.split("/")
                #   print(path_name,"ravi1")
                #   print( path_name[-2]+'/'+path_name[-1],"ravi2")
                #   print(path_name[-1],"ravi3")
                #   block_blob_service.get_blob_to_path(container_name, path_name[-2]+'/'+path_name[-1], path_name[-1])
                #   new_path = "/home/cdms_backend/cdms2/"+ path_name[-1]



        filnn=dpath.split("/")
        # print(filnn,"filnn")
        filnnwext=filnn[-1].split(".")
        doc_list=['doc','docx','ppt','pptx','xlsx','xls','csv','txt']
        if filnnwext[-1]=='jpg':
            # print("in if ",filnnwext[-1])
            # print(filnnwext,"filnnwext")
            pdf_filename=str(filnnwext[0])+"."+filnnwext[-1]
            # print(pdf_filename,"pdf_filename")
            blobname=filnn[-2]+"/"+pdf_filename
            # print(blobname,"blobname")
            pdfpath2="https://docullystorage.blob.core.windows.net/docullycontainer/"+blobname+sas_url
            # print(pdfpath2,"pdfpath")
            context_data['jpg'] = pdfpath2
        elif filnnwext[-1]=='jpeg':
            # print("elif in jpeg")
            # print("in if ",filnnwext[-1])
            # print(filnnwext,"filnnwext")
            pdf_filename=str(filnnwext[0])+"."+filnnwext[-1]
            # print(pdf_filename,"pdf_filename")
            blobname=filnn[-2]+"/"+pdf_filename
            # print(blobname,"blobname")
            pdfpath2="https://docullystorage.blob.core.windows.net/docullycontainer/"+blobname+sas_url
            # print(pdfpath2,"pdfpath")
            context_data['jpeg'] = pdfpath2
        elif (filnnwext[-1]=='mp4') or (filnnwext[-1]=='mp3'):
            # print("elif in multi media")
            # print("in if ",filnnwext[-1])
            basename = os.path.basename(str(dpath))
            blobname=filnn[-2]+"/"+basename
            # print(blobname,"blobname")
            pdfpath="https://docullystorage.blob.core.windows.net/docullycontainer/"+blobname+sas_url
            # print(pdfpath,"imagepath")
            if filnnwext[-1]=='mp3':
                context_data['mp3'] = pdfpath
            else:
                context_data['mp4'] = pdfpath
        elif (filnnwext[-1] in doc_list):
            # print("elif in multi ext")
            # print("in if ",filnnwext[-1])
            # print(filnnwext,"filnnwext")
            pdf_filename=str(filnnwext[0])+".pdf"
            # print(pdf_filename,"pdf_filename")
            blobname=filnn[-2]+"/"+pdf_filename
            # print(blobname,"blobname")
            pdfpath2="https://docullystorage.blob.core.windows.net/docullycontainer/"+blobname+sas_url
            # print(pdfpath2,"pdfpath")
            if filnnwext[-1]=='txt':
                context_data['txtt'] = pdfpath2
            else:
                context_data['refpath'] = pdfpath2
        
        elif (filnnwext[-1]=='png') or (filnnwext[-1]=='pdf'):
            basename = os.path.basename(str(dpath))
            blobname=filnn[-2]+"/"+basename
            # print(blobname,"blobname")
            pdfpath="https://docullystorage.blob.core.windows.net/docullycontainer/"+blobname+sas_url
            # print(pdfpath,"imagepath")
            context_data['refpath'] = pdfpath
        context_data['path'] = str(path)+sas_url+'#toolbar=0'
        context_data['filename'] = filnn[-1]
        context_data['uploadedby'] = data.vote_created_by
        context_data['uploadeddate']=data.vote_created
        context_data['dpath'] = dpath+sas_url
        context_data['base_url'] = base_url
        context_data['frontend_url'] = frontend_url
        context_data['docs'] = docs
        context_data['odf'] = odf
        context_data['pdf'] = pdf
        context_data['csv'] = csv
        context_data['psd'] = psd
        context_data['pptx'] = pptx
        context_data['png'] = png
        context_data['url'] = "https://services.docully.com"+'/projectName/file-view/'+str(pk)+'/'+str(pk1)+'/'
        context_data['excel'] = excel
        context_data['login_user'] = pk1
        context_data['message'] = message
        context_data['user'] = user
        context_data['pathen'] = urllib.parse.quote(context_data['path'])
        context_data['pathdownload']=path
        context_data['pathpptpdf']=context_data['path'].replace('pptx','pdf')
        context_data['title'] = data.title

        return render(request, 'votefile-view.html', context_data )

