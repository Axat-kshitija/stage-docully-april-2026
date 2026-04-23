from django.shortcuts import render
import os
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions, routers, serializers, viewsets
from rest_framework.parsers import JSONParser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.utils import timezone 
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.crypto import get_random_string
import datetime
import operator
from dataroom import utils as dataroom_utils
from data_documents.utils import convert_to_kolkata
from userauth.models import User_time_zone
import requests

from django.db.models import Max, F, Min, Q, Sum
try:
    from functools import reduce
except ImportError:  # Python < 3
    pass
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    ListCreateAPIView)
from rest_framework import permissions
# from rest_framework.authtoken.models import Token
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FileUploadParser
from django.core.mail import send_mail
from random import randint
from userauth.serializers import UserSerializer, AccessHistorySerializer, InviteUserSerializer,pendinginvitationsSerializer
from userauth import constants, utils
from userauth.models import Profile, AccessHistory, User, InvitationStatus, InviteUser,pendinginvitations
import json
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete
from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework.renderers import JSONRenderer
from .models import DataroomMembers
from .serializers import DataroomMembersSerializer
from emailer import utils as emailer_utils
from emailer.models import SiteSettings
from dataroom.models import Dataroom, DataroomRoles, DataroomOverview
from dataroom.models import DataroomView, Watermarking
from dataroom.serializers import DataroomRolesSerializer,DataroomViewSerializer

from data_documents.serializers import DataroomFolderSerializer

from .models import DataroomGroups, DataroomGroupPermission, DataroomGroupFolderSpecificPermissions, DataroomMembers,Irm_group_protection_details
from .serializers import DataroomGroupsSerializer, DataroomGroupPermissionSerializer, DataroomGroupFolderSpecificPermissionsSerializer
from data_documents.models import DataroomFolder
from notifications.models import AllNotifications
from userauth.models import TokenAuthentication,Token
from myteams.models import *

class ChangeDisclaimerStatus(APIView):
    serializers = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        print(request.data,'777777777777777')
        try:
            dataroom_mem = DataroomMembers.objects.filter(member__id=int(request.data['userid']))
        except:
            dataroom_mem = DataroomMembers.objects.filter(member__id=request.data)

        if dataroom_mem:
            for each in dataroom_mem:
                overview = DataroomOverview.objects.filter(dataroom_id=each.dataroom_id).first()
                if overview.show_multiple_times_disclaimer == True:
                    each.disclaimer_status = False
                    each.save()
            return Response({"result": True}, status=status.HTTP_201_CREATED)
        else:
            return Response({"result": True}, status=status.HTTP_201_CREATED)


class GetAllPrimaryUser(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRR',dataroompermission,user.id,pk)
        if dataroompermission==False:
            # print("____________________________________________")
            # print(user.id)
            dataroom_primary_user = DataroomMembers.objects.filter(dataroom_id=pk,is_deleted=False,is_primary_user=True)
            serializer = DataroomMembersSerializer(dataroom_primary_user, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(None)


class GetEndUserGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom_member = DataroomGroups.objects.filter(dataroom_id=pk)
        serializer = DataroomGroupsSerializer(dataroom_member, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)


class CheckAdminUser(APIView):
    serializers = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        dataroom_group_id = request.data['dataroom_group_id']
        # print("dataroom", dataroom_group_id)        
        dataroom = Dataroom.objects.filter(id=int(dataroom_group_id)).first()
        # count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.my_team.id, is_deleted=False).count()
        # print("dataroom",dataroom.my_team.dataroom_admin_allowed, count,'22222222222')
        # if dataroom.my_team.dataroom_admin_allowed > count:
        if dataroom_group_id:
                dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group_id, is_dataroom_admin=True).first()
                # print("dataroom-Meme", dataroom_mem)
                if dataroom_mem == None:
                    return Response({"result": True, 'msg':'Added successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"result": False, 'msg':'This is user already exist in this dataroom!'}, status=status.HTTP_400_BAD_REQUEST)                
        # else:
            # return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": False, 'msg':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class CheckAdmin(APIView):
    serializers = UserSerializer
    # permission_classes = [permissions.AllowAny]
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        # print("Request Data", request.data)
        dataroom_group_id = request.data['dataroom_group_id']        
        dataroom = DataroomGroups.objects.filter(id=int(dataroom_group_id)).first()
        # count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.dataroom.my_team.id, is_deleted=False).count()
        # print("dataroom",dataroom.dataroom.my_team.dataroom_admin_allowed, count,'44444444444')
        # if dataroom.dataroom.my_team.dataroom_admin_allowed > count:
        if dataroom_group_id:
                dataroom_group = DataroomGroups.objects.filter(id=dataroom_group_id)           
                try:
                    if request.data['is_end_user']:
                        dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_la_user=True, is_deleted=False)
                        dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_dataroom_admin=True, is_deleted=False).first()
                        if not dataroom_mem and not dataroom_la_check:
                            return Response({"result": True, 'msg':'Success'}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"result": False, 'msg':'This user already exist in this group!!'}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_la_user=True, is_deleted=False)
                    dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_dataroom_admin=True, is_deleted=False).first()
                    # print("Dataroom Member", dataroom_mem, dataroom_la_check)
                    if not dataroom_mem and not dataroom_la_check:
                        return Response({"result": True}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"result": False,'msg':'This user already exist in this group!!'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
            # return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)              
        return Response({"result": False, 'msg':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class CheckLaUser(APIView):
    serializers = UserSerializer
    # permission_classes = [permissions.AllowAny]
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        # print("Request Data", request.data)
        dataroom_group_id = request.data['dataroom_group_id']        
        dataroom = DataroomGroups.objects.filter(id=int(dataroom_group_id)).first()
        # count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.dataroom.my_team.id, is_deleted=False).count()
        # MyTeams.objects.filter(id=dataroom.dataroom.my_team.id).update(dataroom_admin_allowed=100)
        # print("dataroom",dataroom.dataroom.my_team.dataroom_admin_allowed, count,'3333333333')
        # if dataroom.dataroom.my_team.dataroom_admin_allowed > count:
        if dataroom_group_id:
                dataroom_group = DataroomGroups.objects.filter(id=dataroom_group_id)           
                dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_dataroom_admin=True)
                # print("dataroom_mem.", dataroom_mem)
                try:
                    if request.data['is_end_user']:
                        dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_deleted=False)
                        # print("dataroooom", dataroom_la_check)
                        if not dataroom_mem and not dataroom_la_check:
                            return Response({"result": True}, status=status.HTTP_201_CREATED)
                        else:
                            dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_deleted=False)
                            if dataroom_la_check:
                                return Response({"result": True}, status=status.HTTP_201_CREATED)
                            else:
                                return Response({"result": False, 'msg':'This user already exist in this group!'}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), is_deleted=False, dataroom_id=dataroom_group.first().dataroom_id)
                    if not dataroom_mem and not dataroom_la_check:
                        return Response({"result": True}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"result": False, 'msg':'This user already exist in this group!'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
            # return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": False, 'msg':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteDataroomAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        from datetime import datetime
        dataroom_member = DataroomMembers.objects.get(id=pk)
        dataroom_member.is_deleted = True
        dataroom_member.is_dataroom_admin = False
        dataroom_member.group_name="Admin"
        dataroom_member.date_updated=datetime.now()
        dataroom_member.save()
        #changes added by harish 
        # print(pk)
        # print("---------------------dataroom_invitation",dataroom_member.dataroom_id)
        InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

        return Response({'data': 'Admin successfully deleted !'}, status=status.HTTP_201_CREATED)


class DeleteTypeDataroomAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        dataroom_member = DataroomMembers.objects.get(id=pk)
        # dataroom_member.request.data['delete_type'] = True
        # print('//////////////',request.data)
        dataroom_group=DataroomGroups.objects.get(id=request.data['group_id'])
        from datetime import datetime
        if request.data['is_deleted'] == 'is_deleted_la':
            dataroom_member.is_deleted_la = True
            dataroom_member.end_user_group.remove(request.data['group_id'])
            #added by harish  
            dataroom_member.group_name=dataroom_group.group_name
            dataroom_member.date_updated=datetime.now()
            # print("value of -----------pk",pk)
            # print(dataroom_member.dataroom_id)
            InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

            # dataroom_member.is_la_user = False
            dataroom_member.save()
        if request.data['is_deleted'] == 'is_deleted_end':
            dataroom_member.is_deleted_end = True
            dataroom_member.is_end_user = False
            dataroom_member.end_user_group.remove(request.data['group_id'])
            dataroom_member.group_name=dataroom_group.group_name
            # print('end user deleted ')
            #harish march 2
            InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

        # dataroom_member.group_name=dataroom_group.group_name
        dataroom_member.is_deleted = True
        dataroom_member.memberactivestatus=False
        dataroom_member.is_primary_user=False
        dataroom_member.is_q_a_user=False
        dataroom_member.is_q_a_submitter_user=False
        dataroom_member.is_end_user=False
        dataroom_member.date_updated=datetime.now()
        dataroom_member.save()
        return Response({'data': 'User successfully deleted !'}, status=status.HTTP_201_CREATED)


class DeleteDataroomAllAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        for each in request.data['values']:
            user = request.user
            dataroom_member = DataroomMembers.objects.filter(id=each['id']).first()
            if dataroom_member:
                dataroom_member.is_deleted = True
                dataroom_member.save()
#line added by harish for testing purpose 
                # print("no added by harish for testing purpose ")
                InviteUser.objects.filter(invitiation_receiver=dataroom_member[0].member_id,dataroom_invitation=dataroom_member[0].dataroom_id).update(is_invitation_accepted=False)

                return Response({'data': 'Admin successfully deleted !'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'data': 'Already admin deleted'})


# class BulkDeleteTypeDataroomAdmins(APIView):
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def post(self, request, pk, format=None):
#         user = request.user
#         # dataroom_member.request.data['delete_type'] = True
#         # print('//////////////',request.data)
#         if request.data['is_deleted'] == 'is_deleted_la':
#             for i in request.data['group_id']:
#                 dataroom_member = DataroomMembers.objects.get(id=i)
#                 dataroom_member.is_deleted_la = True
#                 dataroom_member.end_user_group.remove(pk)
#                 #added by harish  
#                 # print("value of -----------pk",pk)
#                 # print(dataroom_member.dataroom_id)
#                 InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

#                 # dataroom_member.is_la_user = False
#                 dataroom_member.save()
#             return Response({'data': 'successfully deleted !'}, status=status.HTTP_201_CREATED)









class BulkDeleteTypeDataroomAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk,pk1 ,format=None):
        user = request.user
        # dataroom_member.request.data['delete_type'] = True
        # print('//////////////',request.data)
        from datetime import datetime
        data=request.data
        print('---+++++++++',data)
        for i in data['id']:
            dataroom_member = DataroomMembers.objects.get(id=int(i))
            if data['is_deleted'] == 'is_deleted_la':
                
                dataroom_group=DataroomGroups.objects.get(id=pk1)
                dataroom_member.is_deleted_la = True
                dataroom_member.end_user_group.remove(pk1)
                #added by harish  
                dataroom_member.group_name=dataroom_group.group_name
                dataroom_member.date_updated=datetime.now()
                # print("value of -----------pk",pk)
                # print(dataroom_member.dataroom_id)
                InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

                # dataroom_member.is_la_user = False
                dataroom_member.save()
            if data['is_deleted'] == 'is_deleted_end':
                dataroom_group=DataroomGroups.objects.get(id=pk1)
                dataroom_member.is_deleted_end = True
                dataroom_member.is_end_user = False
                dataroom_member.end_user_group.remove(pk1)
                dataroom_member.group_name=dataroom_group.group_name
                # print('end user deleted ')
                #harish march 2
                InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

            if data['is_deleted'] == 'is_deleted_admin':
                dataroom_member.is_dataroom_admin = False
                dataroom_member.group_name="Admin"
                InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

            # dataroom_member.group_name=dataroom_group.group_name
            dataroom_member.is_deleted = True
            dataroom_member.memberactivestatus=False
            dataroom_member.is_primary_user=False
            dataroom_member.is_q_a_user=False
            dataroom_member.is_q_a_submitter_user=False
            dataroom_member.is_end_user=False
            dataroom_member.date_updated=datetime.now()
            dataroom_member.save()
        # if request.data['is_deleted'] == 'is_deleted_la':
            # for i in request.data['group_id']:
            #     dataroom_member = DataroomMembers.objects.get(id=i)
            #     dataroom_member.is_deleted_la = True
            #     dataroom_member.end_user_group.remove(pk)
            #     #added by harish  
            #     # print("value of -----------pk",pk)
            #     # print(dataroom_member.dataroom_id)
            #     InviteUser.objects.filter(invitiation_receiver=dataroom_member.member_id,dataroom_invitation=dataroom_member.dataroom_id).update(is_invitation_accepted=False)

            #     # dataroom_member.is_la_user = False
            #     dataroom_member.save()
        return Response({'data': 'successfully deleted !'}, status=status.HTTP_201_CREATED)







class CreateDataroomAdmin(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRR',dataroompermission,user.id,pk)
        if dataroompermission==False:
            dataroom = Dataroom.objects.get(id=pk)
            serializer_data = UserSerializer(dataroom.user, many=False).data
            dataroom_members = DataroomMembers.objects.filter(dataroom_id=pk, is_dataroom_admin=True, is_deleted= False)#.exclude(dataroom_id=dataroom.id, member=dataroom.user)
            dataroom_members_serializer = DataroomMembersSerializer(dataroom_members, many=True)
            data =  dataroom_members_serializer.data
            print('----------------------------------------------------------dataaa',data)
            # for da in data:
            #     try:
            #         invite_user = InviteUser.objects.get(invitiation_receiver_id=da['member']['id'],invitiation_sender_id=da['member_added_by']['id'],dataroom_invitation=da['dataroom']['id'])
            #         invitation_serializer = InviteUserSerializer(invite_user)     
            #         da['invitation'] = invitation_serializer.data
            #     except:
            #         da['invitation'] = ""
            return Response(data)
        else:
            return Response(None)

    def post(self, request, pk, format=None):
        user = request.user
        all_new_data = request.data['admin']
        print('----------------------------------------',all_new_data)
        custom_msg=request.data['custom_msg']
        length_newrequest=len(all_new_data)
        dataroom_data = Dataroom.objects.get(id=pk)
        dataroom_memberlimit=int(DataroomMembers.objects.filter(is_deleted=False,dataroom=pk).count())+int(length_newrequest)
        if int(dataroom_data.dataroom_users_permitted)>=dataroom_memberlimit:
            for i in all_new_data:
                if User.objects.filter(email=i.get('email').lower()).exists():
                    usercheckd=User.objects.get(email=i.get('email').lower()).id
                    memberdataaa1 = DataroomMembers.objects.filter(dataroom_id=pk,member_id=usercheckd,is_deleted=False).exists()
                    if memberdataaa1==True:            
                    #     pendinginvitations.objects.create(senderuser_id=user.id,dataroom_id=pk,email=i['email'],dataroom_group_id=i['dataroom_group_id'],first_name=i['first_name'],last_name=i['last_name'],is_la_user=i['is_la_user'])
                    # else:
                        return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)
            for data in all_new_data:
                if user.email != data.get('email').lower():
                    is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                    
                    dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                    #step1
                    """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                    if is_user == False:
                        data['password'] = "Test@1234"
                        data['is_admin'] = False
                        data['is_active'] = True
                        data['is_end_user'] = True
                        data['is_subscriber']=True
                        serializer = UserSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            # If user is saved then make the entry inside InviteUser page
                            
                            # step : 2 -> Make the entry of User inside the DataroomRoles
                            dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                            dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                            if dataroom_roles_serializer.is_valid():
                                dataroom_roles_serializer.save()

                            # make the entry of user inside the data
                            unique_id = get_random_string(length=400)
                            constants.link=constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':serializer.data.get("id"),   
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id, 
                                'dataroom_invitation':pk
                            }
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                invite_user_serializer.save()
                                # if dr_overview.send_daily_email_updates:
                                newinvitedata=User.objects.get(id=serializer.data['id'])
                                emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, serializer.data['email'], dataroom_data,user.email,custom_msg)
                                emailer_utils.send_dataroom_admin_email_if_user_exist(newinvitedata, invite_user_serializer.data, user, dataroom_data,custom_msg)

                                # add the entry of member inside datarooom members table
                                # dataroom_member_data = {'dataroom':int(pk),'member' : User.objects.get(id=serializer.data.get('id')), 'member_type_id':1, 'member_added_by':user, 'is_dataroom_admin': True}
                                # dataroom_member_serializer = DataroomMembersSerializer(data= dataroom_member_data, context={'member_data': dataroom_member_data})
                                # if dataroom_member_serializer.is_valid():
                                #     dataroom_member_serializer.save()
                                    # all dataroom members
                                dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=serializer.data.get("id"), member_added_by_id=user.id)
                                if not created:
                                    dataroom_mem_obj.dataroom_id = serializer.data.get('id')
                                    dataroom_mem_obj.member_id = dataroom_admin.id
                                    dataroom_mem_obj.member_type = 1
                                    dataroom_mem_obj.member_added_by_id = user.id
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_q_a_user = True


                                    dataroom_mem_obj.save()
                                else:
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_q_a_user = True

                                    try:
                                        dataroom_mem_obj.member_type = 1
                                    except:
                                        pass

                                    dataroom_mem_obj.group_name="Admin"
                                    dataroom_mem_obj.save()
                                    dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                    dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                                    # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        print('-----------------------------------------------------------------------------------------------------------------------------------------------')
                        old_user = User.objects.get(email__iexact=data.get("email").lower())
                        print('---------------------',old_user.check_password('Password1#'))
                        if old_user.check_password('Password1#'):
                        # if old_user.password=='Password1#':
                            print('-----------------------------------------------------------------------------------------------------------------------------------------------1111')
                            serializer = UserSerializer(old_user,many=False)
                            unique_id = get_random_string(length=400)
                            constants.link=constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':serializer.data.get("id"),   
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id, 
                                'dataroom_invitation':pk
                            }
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                invite_user_serializer.save()
                                # if dr_overview.send_daily_email_updates:
                                newinvitedata=User.objects.get(id=serializer.data['id'])
                                emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, serializer.data['email'], dataroom_data,user.email,custom_msg)
                                emailer_utils.send_dataroom_admin_email_if_user_exist(newinvitedata, invite_user_serializer.data, user, dataroom_data,custom_msg)

                                # add the entry of member inside datarooom members table
                                # dataroom_member_data = {'dataroom':int(pk),'member' : User.objects.get(id=serializer.data.get('id')), 'member_type_id':1, 'member_added_by':user, 'is_dataroom_admin': True}
                                # dataroom_member_serializer = DataroomMembersSerializer(data= dataroom_member_data, context={'member_data': dataroom_member_data})
                                # if dataroom_member_serializer.is_valid():
                                #     dataroom_member_serializer.save()
                                    # all dataroom members
                                dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_dataroom_admin':True}
                                dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)
                                if not created:
                                    dataroom_mem_obj.dataroom_id = pk
                                    dataroom_mem_obj.member_id = old_user.id
                                    try:
                                        dataroom_mem_obj.member_type = 1
                                    except:
                                        pass
                                    dataroom_mem_obj.member_added_by_id = user.id
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_end_user = False
                                    dataroom_mem_obj.is_la_user = False
                                    dataroom_mem_obj.is_deleted = False
                                    dataroom_mem_obj.is_deleted_end = False
                                    dataroom_mem_obj.is_deleted_la = False
                                    dataroom_mem_obj.is_q_a_user = True
                                    dataroom_mem_obj.group_name="Admin"
                                    dataroom_mem_obj.save()
                                    for mem in request.data['admin']:    
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.limited_access or d_m.end_user:
                                                dataroom_mem_obj.end_user_group.remove(d_m.id)
                                else:
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_q_a_user = True

                                    try:
                                        dataroom_mem_obj.member_type = 1
                                    except:
                                        pass
                                    dataroom_mem_obj.save()

                                    for mem in request.data['admin']:    
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.end_user:
                                                dataroom_mem_obj.end_user_group.remove(d_m.id)
                                # DataroomMembers.objects(**dataroom_member_data)
                                # dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member_data)
                                # dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member__newdata, context={'new_data': dataroom_member__newdata})
                                # if dataroom_member_serializer.is_valid():
                                #   dataroom_member_serializer.save()
                                    # all dataroom members 

                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                        else:
                            print('-----------------------------------------------------------------------------------------------------------------------------------------------elseee')
                            old_user.is_admin = True
                            old_user.save()
                            unique_id = get_random_string(length=400)
                            constants.link=constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':old_user.id, 
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id,
                                'dataroom_invitation':pk

                            }
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                invite_user_serializer.save()
                                # if dr_overview.send_daily_email_updates:
                                emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data,custom_msg)
                                dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_dataroom_admin':True}
                                try:
                                    dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id,member_added_by=user)
                                except:
                                    memb=DataroomMembers.objects.filter(dataroom_id=pk, member_id=old_user.id).order_by('id')[1:]
                                    # for i in memb:
                                    #     DataroomMembers.objects.filter(id=i.id).delete()
                                    dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id,member_added_by=user)


                                print('---------------if upside')
                                if not created:
                                    print('---------------if not creasted')
                                    dataroom_mem_obj.dataroom_id = pk
                                    dataroom_mem_obj.member_id = old_user.id
                                    try:
                                        dataroom_mem_obj.member_type = 1
                                    except:
                                        pass
                                    dataroom_mem_obj.member_added_by_id = user.id
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_end_user = False
                                    dataroom_mem_obj.is_la_user = False
                                    dataroom_mem_obj.is_deleted = False
                                    dataroom_mem_obj.is_deleted_end = False
                                    dataroom_mem_obj.is_deleted_la = False
                                    dataroom_mem_obj.is_q_a_user = True
                                    dataroom_mem_obj.group_name="Admin"
                                    dataroom_mem_obj.save()
                                    print('-----------------firrrrrrr',dataroom_mem_obj.id, '---------is',dataroom_mem_obj.is_dataroom_admin)
                                    for mem in request.data['admin']:    
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.limited_access or d_m.end_user:
                                                dataroom_mem_obj.end_user_group.remove(d_m.id)
                                else:
                                    print('---------------if not creasted elseeee')
                                    dataroom_mem_obj.is_dataroom_admin = True
                                    dataroom_mem_obj.is_q_a_user = True

                                    try:
                                        dataroom_mem_obj.member_type = 1
                                    except:
                                        pass
                                    dataroom_mem_obj.group_name="Admin"
                                    dataroom_mem_obj.save()

                                    for mem in request.data['admin']:    
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.end_user:
                                                dataroom_mem_obj.end_user_group.remove(d_m.id)
                                # DataroomMembers.objects(**dataroom_member_data)
                                # dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member_data)
                                # dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member__newdata, context={'new_data': dataroom_member__newdata})
                                # if dataroom_member_serializer.is_valid():
                                #   dataroom_member_serializer.save()
                                    # all dataroom members 

                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                else:
                    return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
            try:
                return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response({'msg': 'Member Limit exceed !'}, status=status.HTTP_400_BAD_REQUEST)


# Start rajendra code here
class CreateDataroomLaGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        data = request.data
        user = request.user
        dataroom_groups = DataroomGroups.objects.filter(dataroom_id=pk, is_deleted=False)
        dataroom_group_serializer = DataroomGroupsSerializer(dataroom_groups, many=True)
        return Response(dataroom_group_serializer.data)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        dataroom_group_serializer = DataroomGroupsSerializer(data = data, context={'group_created_by': user.id, 'dataroom': int(pk)})
        print(dataroom_group_serializer.is_valid(),dataroom_group_serializer.errors)
        if dataroom_group_serializer.is_valid():
            dataroom_group_serializer.save()
            # print("datagroup id "+str(dataroom_group_serializer.data['id']))
            # print("dataroom id "+str(dataroom_group_serializer.data['dataroom']['id']))
            # change by harish working fine ,issue is fix 
            dataroom_id =dataroom_group_serializer.data['dataroom']['id']
            dataroom_groupid =dataroom_group_serializer.data['id']
            da_g_p = DataroomGroupPermission.objects.filter(Q(dataroom_id=dataroom_id) & Q(dataroom_groups=dataroom_groupid)).exists()
            # print(da_g_p)
            if da_g_p == False:
                # print("TRue")
                DataroomGroupPermission.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
                # DataroomGroupPermission.objects.create(dataroom_id=dataroom_id,dataroom_groups_id=dataroom_groupid,is_watermarking=False,is_doc_as_pdf=False,is_excel_as_pdf=False,is_drm=False,is_edit_index=False,is_overview=False,is_q_and_a=False,is_users_and_permission=False,is_updates=False,is_report=False,is_voting=False)
               
                AllNotifications.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'], user_id=dataroom_group_serializer.data['group_created_by']['id'])
            return Response(dataroom_group_serializer.data, status=status.HTTP_201_CREATED)


class AddDataroomLaUserGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    """docstring for AddDataroomLaUserGroup"""
    # def get(self, request, pk, format=None):
    #     data = request.data
    #     user = request.user
    #     dataroom_groups = DataroomGroups.objects.filter(dataroom_id=pk)
    #     dataroom_group_serializer = DataroomGroupsSerializer(dataroom_groups, many=True)
    #     return Response(dataroom_group_serializer.data)

    def get(self, request, pk, format=None):
        user = request.user
        group = request.GET.get("group_id")
        dataroom_members = DataroomMembers.objects.filter(dataroom_id=pk, is_la_user=True, is_deleted_la=False, end_user_group__in=[group])
        dataroom_group_permission = DataroomGroupPermission.objects.filter(dataroom_groups_id=group,dataroom_id=pk).last()


        dataroom_members_serializer = DataroomMembersSerializer(dataroom_members, many=True)

        data =  dataroom_members_serializer.data
        # raveena's code
        for da in data:
            try:
                invite_user = InviteUser.objects.get(invitiation_receiver_id=da['member']['id'],invitiation_sender_id=da['member_added_by']['id'],dataroom_invitation=da['dataroom']['id'])
                invitation_serializer = InviteUserSerializer(invite_user)     
                da['invitation'] = invitation_serializer.data
            except:
                da['invitation'] = ""
        data.append({'qanda_permission':dataroom_group_permission.is_q_and_a})
        # print(data)
        return Response(data)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        length_newrequest=len(request.data['member'])
        custom_msg=request.data['custom_msg']
        dataroom_data = Dataroom.objects.get(id=pk)
        dataroom_memberlimit=int(DataroomMembers.objects.filter(is_deleted=False,dataroom=pk).count())+int(length_newrequest)
        if int(dataroom_data.dataroom_users_permitted)>=dataroom_memberlimit:
            stateofdataroom=request.data['dataroomstate']
            if stateofdataroom=='Hold':
                all_member = request.data['member']

                for i in all_member:
                    memberdataaa1 =False
                    if User.objects.filter(email=i.get('email').lower()).exists():
                        usercheckd=User.objects.get(email=i.get('email').lower()).id
                        memberdataaa1 = DataroomMembers.objects.filter(dataroom_id=pk,member_id=usercheckd,is_deleted=False).exists()
                        if memberdataaa1==False:            
                            pendinginvitations.objects.create(senderuser_id=user.id,dataroom_id=pk,email=i['email'],dataroom_group_id=i['dataroom_group_id'],first_name=i['first_name'],last_name=i['last_name'],is_la_user=i['is_la_user'])
                        else:
                            return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        pendinginvitations.objects.create(senderuser_id=user.id,dataroom_id=pk,email=i['email'],dataroom_group_id=i['dataroom_group_id'],first_name=i['first_name'],last_name=i['last_name'],is_la_user=i['is_la_user'])


            else:
                    if stateofdataroom=='Holdtolive':
                        membersdata=pendinginvitations.objects.filter(dataroom_id=pk,emailsendflag=False,is_la_user=True)
                        # print(membersdata,'UUUUUUUUUUUUUUUUUUUUUUUUu')

                        all_member=pendinginvitationsSerializer(membersdata,many=True).data
                        # print(all_member,'RURRRRRRRRRRRRRRRRRRRRRRRRR')
                        for i in all_member:
                            i['dataroom_group_id']=i.get('dataroom_group')
                        pendinginvitations.objects.filter(dataroom_id=pk,emailsendflag=False,is_la_user=True).update(emailsendflag=True)
                        

                    else:
                        all_member = request.data['member']



            # print (all_member,'RRRRRRRRRRRRRRRRR4444')
            for data in all_member:
                memberdataaa =False
                if User.objects.filter(email=data.get('email').lower()).exists():
                    usercheckd=User.objects.get(email=data.get('email').lower()).id
                    memberdataaa = DataroomMembers.objects.filter(dataroom_id=pk,member_id=usercheckd,is_deleted=False).exists()
                if stateofdataroom=='Holdtolive':
                    if User.objects.filter(id=data.get('senderuser')).exists():
                        user=User.objects.get(id=data.get('senderuser'))
                if user.email != data.get('email').lower() and (memberdataaa ==False or stateofdataroom=='Holdtolive'):

                    # print (2222222222)
                    is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                    dataroom_data = Dataroom.objects.get(id=pk)
                    dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                    new_invite=all_member[0]['email']
                    # print(new_invite,"new_invite")
                    #step1
                    """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                    if is_user == False:
                        # print (333333333333)
                        data['password'] = get_random_string(length=9)
                        data['is_admin'] = False
                        data['is_active'] = True
                        data['is_end_user'] = True
                        data['is_subscriber']=True

                        serializer = UserSerializer(data=data)
                        if serializer.is_valid():
                            if stateofdataroom!='Holdtolive':
                                serializer.save()

                            dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                            dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                            if stateofdataroom!='Holdtolive':
                                if dataroom_roles_serializer.is_valid():
                                    dataroom_roles_serializer.save()

                            # make the entry of user inside the data
                            unique_id = get_random_string(length=400)
                            constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':serializer.data.get("id"), 
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id, 
                                'dataroom_invitation':pk
                            }
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                if stateofdataroom!='Hold':

                                    invite_user_serializer.save()
                                    # if dr_overview.send_daily_email_updates:
                                    newuserdata=User.objects.get(id=serializer.data['id'])
                                    emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, new_invite, dataroom_data,user.email,custom_msg)
                                    emailer_utils.send_dataroom_admin_email_if_user_exist(newuserdata, invite_user_serializer.data, user, dataroom_data,custom_msg)

                                # add the entry of member inside datarooom members table
                                # dataroom_member_data = {'dataroom':int(pk),'member' : User.objects.get(id=serializer.data.get('id')), 'member_type_id':1, 'member_added_by':user, 'is_dataroom_admin': True}
                                # dataroom_member_serializer = DataroomMembersSerializer(data= dataroom_member_data, context={'member_data': dataroom_member_data})
                                # if dataroom_member_serializer.is_valid():
                                #     dataroom_member_serializer.save()
                                    # all dataroom members
                                dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])
                                if stateofdataroom!='Holdtolive':
                                    dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=serializer.data.get("id"), member_added_by_id=user.id)
                                    if not created:
                                        # print (66666666666)
                                        dataroom_mem_obj.dataroom_id = serializer.data.get('id')
                                        dataroom_mem_obj.member_id = dataroom_admin.id
                                        dataroom_mem_obj.member_type = 1
                                        dataroom_mem_obj.member_added_by_id = user.id
                                        dataroom_mem_obj.is_la_user = True
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                    else:
                                        # print (77777777777777)
                                        dataroom_mem_obj.is_la_user = True
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        try:
                                            dataroom_mem_obj.member_type = 1
                                        except:
                                            pass
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                        dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                        dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                                        # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        
                        old_user = User.objects.get(email__iexact=data.get("email").lower())
                        if old_user.check_password('Password1#'):
                            serializer = UserSerializer(old_user,many=False)
                            dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                            dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                            if stateofdataroom!='Holdtolive':
                                if dataroom_roles_serializer.is_valid():
                                    dataroom_roles_serializer.save()

                            # make the entry of user inside the data
                            unique_id = get_random_string(length=400)
                            constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':serializer.data.get("id"), 
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id, 
                                'dataroom_invitation':pk
                            }
                            dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                if stateofdataroom!='Hold':

                                    invite_user_serializer.save()
                                    # if dr_overview.send_daily_email_updates:
                                    newuserdata=User.objects.get(id=serializer.data['id'])
                                    emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, new_invite, dataroom_data,user.email,custom_msg)
                                    emailer_utils.send_dataroom_admin_email_if_user_exist(newuserdata, invite_user_serializer.data, user, dataroom_data,custom_msg)
                                if stateofdataroom!='Holdtolive':
                                    dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':True}
                                    dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)

                                    if not created:
                                        # print (10101010101010)
                                        dataroom_mem_obj.dataroom_id = pk
                                        dataroom_mem_obj.member_id = old_user.id
                                        try:
                                            dataroom_mem_obj.member_type = 1
                                        except:
                                            pass
                                        dataroom_mem_obj.member_added_by_id = user.id
                                        dataroom_mem_obj.is_la_user = True
                                        dataroom_mem_obj.is_end_user = False
                                        dataroom_mem_obj.is_admin = False
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        dataroom_mem_obj.is_deleted =   False
                                        dataroom_mem_obj.is_deleted_la = False
                                        dataroom_mem_obj.is_deleted_end = False
                                        dataroom_mem_obj.is_end_user = False
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        # dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                                        for each in dataroom_mem_obj.end_user_group.all():
                                            if each.limited_access:
                                                # dataroom_mem_obj.end_user_group.remove(each.id)
                                                dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                        for mem in request.data['member']:
                                            if mem['is_la_user']:
                                                for d_m in dataroom_mem_obj.end_user_group.all():
                                                    if d_m.end_user:
                                                        dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                        pass
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                    else:
                                        # print (12121212121212)
                                        dataroom_mem_obj.is_la_user = True
                                        try:
                                            dataroom_mem_obj.member_type = 1
                                        except:
                                            pass
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        dataroom_mem_obj.is_deleted =   False
                                        dataroom_mem_obj.is_deleted_la = False
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])

                        else:
                            old_user.is_end_user = True
                            old_user.save()
                            unique_id = get_random_string(length=400)
                            constants.link="https://stage.docullyvdr.com/projectName/"
                            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                            new_data = {
                                'invitiation_sender':user.id, 
                                'invitiation_receiver':old_user.id, 
                                'invitation_status':3, 
                                'is_invitation_expired':False, 
                                'invitation_link':link, 
                                'invitation_token':unique_id,
                                'dataroom_invitation':pk

                            }
                            dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])
                            invite_user_serializer = InviteUserSerializer(data=new_data)     
                            if invite_user_serializer.is_valid():
                                if stateofdataroom!='Hold':
                                    invite_user_serializer.save()
                                    # if dr_overview.send_daily_email_updates:
                                    emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data,custom_msg)
                                if stateofdataroom!='Holdtolive':
                                    dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':True}
                                    dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)

                                    if not created:
                                        # print (10101010101010)
                                        dataroom_mem_obj.dataroom_id = pk
                                        dataroom_mem_obj.member_id = old_user.id
                                        try:
                                            dataroom_mem_obj.member_type = 1
                                        except:
                                            pass
                                        dataroom_mem_obj.member_added_by_id = user.id
                                        dataroom_mem_obj.is_la_user = True
                                        dataroom_mem_obj.is_end_user = False
                                        dataroom_mem_obj.is_admin = False
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        dataroom_mem_obj.is_deleted =   False
                                        dataroom_mem_obj.is_deleted_la = False
                                        dataroom_mem_obj.is_deleted_end = False
                                        dataroom_mem_obj.is_end_user = False
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        # dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                                        for each in dataroom_mem_obj.end_user_group.all():
                                            if each.limited_access:
                                                # dataroom_mem_obj.end_user_group.remove(each.id)
                                                dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                        for mem in request.data['member']:
                                            if mem['is_la_user']:
                                                for d_m in dataroom_mem_obj.end_user_group.all():
                                                    if d_m.end_user:
                                                        dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                        pass
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                                    else:
                                        # print (12121212121212)
                                        dataroom_mem_obj.is_la_user = True
                                        try:
                                            dataroom_mem_obj.member_type = 1
                                        except:
                                            pass
                                        # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                        dataroom_mem_obj.is_deleted =   False
                                        dataroom_mem_obj.is_deleted_la = False
                                        dataroom_mem_obj.group_name=dataroom_group.group_name
                                        dataroom_mem_obj.save()
                                        dataroom_mem_obj.end_user_group.add(data['dataroom_group_id'])
                else:
                    # print (13131313131313)
                    return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
            # print('coming till here 787878787')
            try:
                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
            except:
                # print (151515151515)
                return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'msg': 'Member Limit exceed !'}, status=status.HTTP_400_BAD_REQUEST)   
         
        
# End rajendra code here


class CreateDataroomEndUserGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user=request.user
        data = request.data
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRR',dataroompermission,user.id,pk)
        if dataroompermission==False:
            user = request.user
            dataroom_groups = DataroomGroups.objects.filter(dataroom_id=pk, is_deleted=False).order_by('-id')
            dataroom_group_serializer = DataroomGroupsSerializer(dataroom_groups, many=True)
            data = dataroom_group_serializer.data
            for da in data:
                count = 0
                dataroom_members_list = DataroomMembers.objects.filter(dataroom_id = pk,is_deleted=False, is_deleted_end=False, is_deleted_la=False)
                for mem in dataroom_members_list:
                    for each in mem.end_user_group.all():
                        if each.id == da['id']:
                            print(mem.member.first_name,each.group_name,'IIIIIIIIIIIIIIIIIIIIIIIII')
                            count += 1
                da['members_length'] = count
                count = 0
            # print(data,'3333333333333333333333333333333333333333333333')
            return Response(data)
        else:
            return Response(None)

    def post(self, request, pk, format=None):
        data = request.data
        user = request.user
        #step 1:  create enduser group
        dataroom_group_serializer = DataroomGroupsSerializer(data = data, context={'group_created_by': user.id, 'dataroom': int(pk)})
        if dataroom_group_serializer.is_valid():
            dataroom_group_serializer.save()
            # change by harish testing data not inserting in dataroomgroup models 
            dataroom_id =dataroom_group_serializer.data['dataroom']['id']
            dataroom_groupid =dataroom_group_serializer.data['id']
            da_g_p = DataroomGroupPermission.objects.filter(Q(dataroom_id=dataroom_id) & Q(dataroom_groups=dataroom_groupid)).exists()
            # print(da_g_p)
            dataroom=Dataroom.objects.get(id=dataroom_id)
            if da_g_p == False:
                # print("TRue333")
                datagroup=DataroomGroupPermission.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
                # DataroomGroupPermission.objects.create(dataroom_id=dataroom_id,dataroom_groups_id=dataroom_groupid,is_watermarking=False,is_doc_as_pdf=False,is_excel_as_pdf=False,is_drm=False,is_edit_index=False,is_overview=False,is_q_and_a=False,is_users_and_permission=False,is_updates=False,is_report=False,is_voting=False)
                if dataroom.dataroom_version == "Lite":
                    datagroup.is_watermarking=True
                    datagroup.is_doc_as_pdf=True
                    datagroup.is_excel_as_pdf=True
                    datagroup.is_edit_index=True
                    datagroup.is_q_and_a=True
                    datagroup.is_updates=True
                    datagroup.save()
                AllNotifications.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'], user_id=dataroom_group_serializer.data['group_created_by']['id'])
            else:
                datagrp=DataroomGroupPermission.objects.filter(Q(dataroom_id=dataroom_id) & Q(dataroom_groups=dataroom_groupid)).last()
                grp1=DataroomGroupPermission.objects.get(id=datagrp.id)
                if dataroom.dataroom_version == "Lite":
                    grp1.is_watermarking=True
                    grp1.is_doc_as_pdf=True
                    grp1.is_excel_as_pdf=True
                    grp1.is_edit_index=True
                    grp1.is_q_and_a=True
                    grp1.is_updates=True
                    grp1.save()
            # da_g_p = DataroomGroupPermission.objects.filter(dataroom_groups=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
            # if not da_g_p:
                # DataroomGroupPermission.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
                # AllNotifications.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'], user_id=dataroom_group_serializer.data['group_created_by']['id'])            
            return Response(dataroom_group_serializer.data, status=status.HTTP_201_CREATED)   



class GetEndUserGroupInformation(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return DataroomGroups.objects.get(pk=pk)
        except DataroomGroups.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        dataroom_group_permission = DataroomGroupPermission.objects.get(dataroom_groups=pk)
        dataroom_group_permission_data = DataroomGroupPermissionSerializer(dataroom_group_permission, many=False)
        return Response(dataroom_group_permission_data.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = DataroomGroupsSerializer(snippet, data=request.data.get('group'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        # snippet.delete()
        snippet.is_deleted=True
        snippet.save()
        DataroomMembers.objects.filter(end_user_group__in=[pk]).update(is_deleted=True,is_deleted_end=True,is_deleted_la=True,memberactivestatus=False,is_primary_user=False,is_q_a_user=False,is_q_a_submitter_user=False,is_end_user=False)
        members=DataroomMembers.objects.filter(end_user_group__in=[pk])
        for i in members:
            i.end_user_group.remove(int(pk))
        # print('done 455555555555555553333333333333')
        return Response(status=status.HTTP_204_NO_CONTENT)

class GetFirstNameAndLastNameUsingEmail(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        data = request.data
        user = request.user
        new_user = User.objects.get(email__iexact=data.get('email').lower())
        new_user_serializer = UserSerializer(new_user, many=False)
        return Response(new_user_serializer.data, status=status.HTTP_201_CREATED)


#Rajendra Working here
class GetUsersAndPermissionData(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        all_limited_admin_groups = 4
        all_end_user_groups = 7
        all_length_is = DataroomMembers.objects.filter(dataroom_id=pk, is_dataroom_admin=True, is_deleted=False).count()
        dataroom_groups = DataroomGroups.objects.filter(dataroom_id=pk, is_deleted=False)
        dataroom_group_serializer = DataroomGroupsSerializer(dataroom_groups, many=True)

        data = {
            'no_of_admins' : all_length_is, 
            'all_limited_admin_groups': all_limited_admin_groups, 
            'all_end_user_groups' : dataroom_group_serializer.data
        }
        
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        data=request.data.get('data')
        dataroom_group_permission = DataroomGroupPermission.objects.get(dataroom_groups_id=pk)
        # if dataroom_group_permission.dataroom.dataroom_version=="Lite":
        #     if not dataroomProLiteFeatures.objects.filter(dataroom_id=dataroom_group_permission.dataroom.id,module_perm=True).exists():
        # data['is_edit_index']=True
        # data['is_q_and_a']=True
        # data['is_updates']=True
        
                
        serializer = DataroomGroupPermissionSerializer(dataroom_group_permission, data=data)
        if serializer.is_valid():
            serializer.save()
            if serializer.data['is_q_and_a']==False:
                DataroomMembers.objects.filter(dataroom_id=serializer.data['dataroom']['id'], is_la_user=True, is_deleted=False, end_user_group__in=[pk]).update(is_q_a_user=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
#End working

class ResendInvitationLink(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        data = request.data
        user = request.user
        member = User.objects.get(id = data.get('member').get('id'))
        sender = User.objects.get(id = data.get('member_added_by').get('id'))
        dataroom = data.get('dataroom')
        print('-datariim',dataroom, '----',dataroom['id'])
        mem = member.has_usable_password()
        print('-----------',mem)
        custom_msg=' I"d like you to join my secure dataroom.'
        invitationdataa=InviteUser.objects.filter(invitiation_sender_id=sender.id,invitiation_receiver_id=member.id,dataroom_invitation=dataroom['id']).last()
        data['invitation']=invitationdataa
        # print(data,'0000000000000000000')
        if member.check_password('Password1#'):
            print('----insdeideede user emal')
            # is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
            mem = member.has_usable_password()
            print('-----------',mem)
            dataroom_data = Dataroom.objects.get(id=dataroom['id'])
            dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
            new_invite=member.email
            """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
            # if is_user == False:
                # print('coming here 00000000000000000011111111111111111111')
                # data['password'] = get_random_string(length=9)
                # data['is_admin'] = False
                # data['is_active'] = True
                # data['is_end_user'] = True
                # data['is_subscriber']=True
            serializer = UserSerializer(member)

            # if serializer.is_valid():
                # if stateofdataroom!='Holdtolive':
                #     serializer.save()
                # If user is saved then make the entry inside InviteUser page
                
                # step : 2 -> Make the entry of User inside the DataroomRoles
                # dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                # dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                # if stateofdataroom!='Holdtolive':                               
                #     if dataroom_roles_serializer.is_valid():
                #         dataroom_roles_serializer.save()

                # make the entry of user inside the data
            unique_id = get_random_string(length=400)
            constants.link="https://stage.docullyvdr.com/projectName/"
            link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
            new_data = {
                'invitiation_sender':sender.id, 
                'invitiation_receiver':member.id, 
                'invitation_status':3, 
                'is_invitation_expired':False, 
                'invitation_link':link, 
                'invitation_token':unique_id, 
                'dataroom_invitation':dataroom['id']
            }
            # invite_user_serializer = InviteUserSerializer(data=new_data)     
            # if invite_user_serializer.is_valid():
            #     if stateofdataroom!='Hold':
            #         # print('coming here 888888888888888888888888888888')

            #         invite_user_serializer.save()
            #         newuserdataa=User.objects.get(id=serializer.data['id'])
            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, new_invite, dataroom_data,user.email,custom_msg)
            emailer_utils.send_dataroom_admin_email_if_user_exist(member, data.get("invitation"), sender, dataroom,custom_msg)
        else:
            emailer_utils.send_dataroom_admin_email_if_user_exist(member, data.get("invitation"), sender, dataroom,custom_msg)
        return Response(status=status.HTTP_201_CREATED)

class GetAllEndUsers(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    """docstring for GetAllEndUsers"""
    def get(self, request, pk, format=None):
        user = request.user
        group = request.GET.get("group_id")
        dataroom_members = DataroomMembers.objects.filter(dataroom_id=pk, is_end_user=True, is_deleted_end=False, end_user_group__in=[group])
        # dataroom_members.first().end_user_group.add(group)
        dataroom_members_serializer = DataroomMembersSerializer(dataroom_members, many=True)
        data =  dataroom_members_serializer.data
        # raveena's code
        for da in data:
            try:
                invite_user = InviteUser.objects.get(invitiation_receiver_id=da['member']['id'],invitiation_sender_id=da['member_added_by']['id'],dataroom_invitation=da['dataroom']['id'])
                invitation_serializer = InviteUserSerializer(invite_user)     
                da['invitation'] = invitation_serializer.data
            except:
                da['invitation'] = ""
        return Response(data)

    def post(self, request, pk, format=None):
                data = request.data
                user = request.user
                # print(request.data,'VCHCHCHCHCHCHCHCCCCCCCCCC')
                stateofdataroom=request.data['dataroomstate']
                custom_msg=request.data['custom_msg']
                length_newrequest=len(request.data['member'])
                dataroom_data = Dataroom.objects.get(id=pk)
                dataroom_memberlimit=int(DataroomMembers.objects.filter(is_deleted=False,dataroom=pk).count())+int(length_newrequest)
                if int(dataroom_data.dataroom_users_permitted)>=dataroom_memberlimit:
                    if stateofdataroom=='Hold':
                        all_member = request.data['member']

                        for i in all_member:
                            memberdataaa1 =False

                            if User.objects.filter(email=i.get('email').lower()).exists():
                                usercheckd=User.objects.get(email=i.get('email').lower()).id
                                memberdataaa1 = DataroomMembers.objects.filter(dataroom_id=pk,member_id=usercheckd,is_deleted=False).exists()
                                # print(i)
                                if memberdataaa1==False:            
                                    pendinginvitations.objects.create(senderuser_id=user.id,dataroom_id=pk,email=i['email'],dataroom_group_id=i['dataroom_group_id'],first_name=i['first_name'],last_name=i['last_name'],is_end_user=True)
                                else:
                                    return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)

                            else:
                                pendinginvitations.objects.create(senderuser_id=user.id,dataroom_id=pk,email=i['email'],dataroom_group_id=i['dataroom_group_id'],first_name=i['first_name'],last_name=i['last_name'],is_end_user=True)

                    else:
                        
                            if stateofdataroom=='Holdtolive':
                                membersdata=pendinginvitations.objects.filter(dataroom_id=pk,emailsendflag=False,is_end_user=True)
                                # print(membersdata,'UUUUUUUUUUUUUUUUUUUUUUUUu')

                                all_member=pendinginvitationsSerializer(membersdata,many=True).data
                                # print(all_member,'RURRRRRRRRRRRRRRRRRRRRRRRRR')
                                for i in all_member:
                                    i['dataroom_group_id']=i.get('dataroom_group')
                                pendinginvitations.objects.filter(dataroom_id=pk,emailsendflag=False,is_end_user=True).update(emailsendflag=True)
                                

                            else:
                                all_member = request.data['member']



                    # print(all_member,'RRRRRRRRRRRRRRRRRRRRRRR')

                    for data in all_member:
                        memberdataaa =False
                        if User.objects.filter(email=data.get('email').lower()).exists():
                            usercheckd=User.objects.get(email=data.get('email').lower()).id
                            memberdataaa = DataroomMembers.objects.filter(dataroom_id=pk,member_id=usercheckd,is_deleted=False).exists()
                        if stateofdataroom=='Holdtolive':
                            if User.objects.filter(id=data.get('senderuser')).exists():
                                user=User.objects.get(id=data.get('senderuser'))                    
                        if user.email != data.get('email').lower() and (memberdataaa ==False or stateofdataroom=='Holdtolive'):
                            # print('rounds __')
                            # print(data,data.get('dataroom_group_id'),'CHekkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                            is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                            dataroom_data = Dataroom.objects.get(id=pk)
                            dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                            new_invite=data.get('email').lower()
                            """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                            dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])

                            if is_user == False:
                                # print('coming here 00000000000000000011111111111111111111')
                                data['password'] = get_random_string(length=9)
                                data['is_admin'] = False
                                data['is_active'] = True
                                data['is_end_user'] = True
                                data['is_subscriber']=True
                                serializer = UserSerializer(data=data)
                                if serializer.is_valid():
                                    if stateofdataroom!='Holdtolive':
                                        serializer.save()
                                    # If user is saved then make the entry inside InviteUser page
                                    
                                    # step : 2 -> Make the entry of User inside the DataroomRoles
                                    dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                                    dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                                    if stateofdataroom!='Holdtolive':                               
                                        if dataroom_roles_serializer.is_valid():
                                            dataroom_roles_serializer.save()

                                    # make the entry of user inside the data
                                    unique_id = get_random_string(length=400)
                                    constants.link="https://stage.docullyvdr.com/projectName/"
                                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                                    new_data = {
                                        'invitiation_sender':user.id, 
                                        'invitiation_receiver':serializer.data.get("id"), 
                                        'invitation_status':3, 
                                        'is_invitation_expired':False, 
                                        'invitation_link':link, 
                                        'invitation_token':unique_id, 
                                        'dataroom_invitation':pk
                                    }
                                    invite_user_serializer = InviteUserSerializer(data=new_data)     
                                    if invite_user_serializer.is_valid():
                                        if stateofdataroom!='Hold':
                                            # print('coming here 888888888888888888888888888888')

                                            invite_user_serializer.save()
                                            newuserdataa=User.objects.get(id=serializer.data['id'])
                                            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, new_invite, dataroom_data,user.email,custom_msg)
                                            emailer_utils.send_dataroom_admin_email_if_user_exist(newuserdataa, invite_user_serializer.data, user, dataroom_data,custom_msg)

                                        if stateofdataroom!='Holdtolive':
                                        
                                            dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=serializer.data.get("id"), member_added_by_id=user.id)

                                            if not created:
                                                dataroom_mem_obj.dataroom_id = serializer.data.get('id')
                                                dataroom_mem_obj.member_id = dataroom_admin.id
                                                dataroom_mem_obj.member_type = 1
                                                dataroom_mem_obj.member_added_by_id = user.id
                                                dataroom_mem_obj.is_end_user = True
                                                dataroom_mem_obj.is_la_user = False
                                                dataroom_mem_obj.end_user_group_id = data.get('dataroom_group_id')
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                
                                                dataroom_mem_obj.group_name=dataroom_group.group_name
                                                dataroom_mem_obj.save()
                                                for each in dataroom_mem_obj.end_user_group.all():
                                                    if each.end_user:
                                                        # dataroom_mem_obj.end_user_group.remove(each.id)
                                                        dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                for mem in request.data['member']:
                                                    if mem['is_end_user']:
                                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                                            if d_m.end_user:
                                                                # dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                                pass
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                            else:
                                                dataroom_mem_obj.is_end_user = True
                                                try:
                                                    dataroom_mem_obj.member_type = 1
                                                except:
                                                    pass
                                                dataroom_mem_obj.end_user_group_id = data.get('dataroom_group_id')
                                                dataroom_mem_obj.group_name=dataroom_group.group_name
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                
                                                dataroom_mem_obj.save()
                                                for mem in request.data['member']:
                                                    if mem['is_end_user']:
                                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                                            if d_m.end_user:
                                                                pass
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=False)
                                                # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                            else:
                                # print('coming here 555555555555555555555888888888888')
                                usr = User.objects.filter(email__iexact=data.get("email").lower()).first()
                                old_user = User.objects.get(email__iexact=data.get("email").lower())
                                if usr.check_password('Password1#'):
                                    serializer = UserSerializer(usr,many=False)
                                    unique_id = get_random_string(length=400)
                                    constants.link="https://stage.docullyvdr.com/projectName/"
                                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(False)
                                    new_data = {
                                        'invitiation_sender':user.id, 
                                        'invitiation_receiver':serializer.data.get("id"), 
                                        'invitation_status':3, 
                                        'is_invitation_expired':False, 
                                        'invitation_link':link, 
                                        'invitation_token':unique_id, 
                                        'dataroom_invitation':pk
                                    }
                                    invite_user_serializer = InviteUserSerializer(data=new_data) 
                                    dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])    
                                    if invite_user_serializer.is_valid():
                                        if stateofdataroom!='Hold':
                                            # print('coming here 888888888888888888888888888888')

                                            invite_user_serializer.save()
                                            newuserdataa=User.objects.get(id=serializer.data['id'])
                                            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, new_invite, dataroom_data,user.email,custom_msg)
                                            emailer_utils.send_dataroom_admin_email_if_user_exist(newuserdataa, invite_user_serializer.data, user, dataroom_data,custom_msg)
                                        if stateofdataroom!='Holdtolive':
                                            
                                            dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':False}
                                            # print("dataroom_member__newdata",dataroom_member__newdata)
                                            dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)
                                        # print("dataroom_member__newdata",dataroom_mem_obj,)
                                            if not created:
                                                dataroom_mem_obj.dataroom_id = pk
                                                dataroom_mem_obj.member_id = old_user.id
                                                try:
                                                    dataroom_mem_obj.member_type = 1
                                                except:
                                                    pass
                                                dataroom_mem_obj.member_added_by_id = user.id
                                                dataroom_mem_obj.is_end_user = True
                                                dataroom_mem_obj.is_la_user = False
                                                dataroom_mem_obj.is_dataroom_admin = False
                                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                                dataroom_mem_obj.is_deleted =   False  
                                                dataroom_mem_obj.is_deleted_la = False
                                                dataroom_mem_obj.group_name=dataroom_group.group_name
                                                dataroom_mem_obj.is_deleted_end = False   
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                                       
                                                dataroom_mem_obj.save()
                                                for each in dataroom_mem_obj.end_user_group.all():
                                                    if each.end_user:
                                                        # dataroom_mem_obj.end_user_group.remove(each.id)
                                                        dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                # for mem in request.data['member']:
                                                #     if mem['is_end_user']:
                                                #         for d_m in dataroom_mem_obj.end_user_group.all():
                                                #             if d_m.end_user:
                                                #                 # dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                #                 pass
                                                # print(data.get('dataroom_group_id'),'Checking thisssssssssssssss')
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                            else:
                                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                                dataroom_mem_obj.is_end_user = True
                                                dataroom_mem_obj.member_added_by_id = user.id
                                                try:
                                                    dataroom_mem_obj.member_type = 1
                                                except:
                                                    pass
                                                dataroom_mem_obj.is_deleted =   False     
                                                dataroom_mem_obj.group_name=dataroom_group.group_name  
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                                         
                                                dataroom_mem_obj.save()
                                                # dataroom_mem_obj.save()
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                
                                else:
                                    usr.is_end_user = True
                                    usr.save()
                                    
                                    unique_id = get_random_string(length=400)
                                    constants.link="https://stage.docullyvdr.com/projectName/"
                                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                                    new_data = {
                                        'invitiation_sender':user.id, 
                                        'invitiation_receiver':old_user.id, 
                                        'invitation_status':3, 
                                        'is_invitation_expired':False, 
                                        'invitation_link':link, 
                                        'invitation_token':unique_id,
                                        'dataroom_invitation':pk

                                    }
                                    dataroom_group=DataroomGroups.objects.get(id=data['dataroom_group_id'])
                                    invite_user_serializer = InviteUserSerializer(data=new_data)    
                                    if invite_user_serializer.is_valid():
                                        if stateofdataroom!='Hold':
                                            # print('coming here 3333333333333333333333333')

                                            invite_user_serializer.save()
                                            emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data,custom_msg)

                                        # print(invite_user_serializer.data,"invite_user_serializer.........>>>>")
                                        # if dr_overview.send_daily_email_updates:
                                        if stateofdataroom!='Holdtolive':
                                            
                                            dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':False}
                                            # print("dataroom_member__newdata",dataroom_member__newdata)
                                            dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)
                                        # print("dataroom_member__newdata",dataroom_mem_obj,)
                                            if not created:
                                                dataroom_mem_obj.dataroom_id = pk
                                                dataroom_mem_obj.member_id = old_user.id
                                                try:
                                                    dataroom_mem_obj.member_type = 1
                                                except:
                                                    pass
                                                dataroom_mem_obj.member_added_by_id = user.id
                                                dataroom_mem_obj.is_end_user = True
                                                dataroom_mem_obj.is_la_user = False
                                                dataroom_mem_obj.is_dataroom_admin = False
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                
                                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                                dataroom_mem_obj.is_deleted =   False  
                                                dataroom_mem_obj.is_deleted_la = False
                                                dataroom_mem_obj.is_deleted_end = False   
                                                dataroom_mem_obj.group_name=dataroom_group.group_name                       
                                                dataroom_mem_obj.save()
                                                for each in dataroom_mem_obj.end_user_group.all():
                                                    if each.end_user:
                                                        # dataroom_mem_obj.end_user_group.remove(each.id)
                                                        dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                # for mem in request.data['member']:
                                                #     if mem['is_end_user']:
                                                #         for d_m in dataroom_mem_obj.end_user_group.all():
                                                #             if d_m.end_user:
                                                #                 # dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                #                 pass
                                                # print(data.get('dataroom_group_id'),'Checking thisssssssssssssss')
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                            else:
                                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                                dataroom_mem_obj.is_end_user = True
                                                dataroom_mem_obj.member_added_by_id = user.id
                                                try:
                                                    dataroom_mem_obj.member_type = 1
                                                except:
                                                    pass
                                                dataroom_mem_obj.is_deleted =   False
                                                dataroom_mem_obj.group_name=dataroom_group.group_name 
                                                if dataroom_data.dataroom_version == "Lite":
                                                    dataroom_mem_obj.is_q_a_submitter_user = True
                                                                               
                                                dataroom_mem_obj.save()
                                                dataroom_mem_obj.save()
                                                dataroom_mem_obj.end_user_group.add(data.get('dataroom_group_id'))
                                                # for each in dataroom_mem_obj.end_user_group.all():
                                                #     if each.end_user:
                                            #         dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                        else:
                            return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
                    try:
                        dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                        dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                        # print(dataroom_mem_serializer.data,"dataroom_mem_serializer.data>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                    except:
                        return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'msg': 'Member Limit exceed !'}, status=status.HTTP_400_BAD_REQUEST)   

           
class GetMembersPermission(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRR',dataroompermission,user.id,pk)

        if dataroompermission==False:
            data = {}
            dataroom_member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id, is_deleted=False)

            if len(dataroom_member) > 0:
                from . import utils
                for da in dataroom_member:
                    if da.is_end_user == True:
                        for each in da.end_user_group.all():
                            group_permission = DataroomGroupPermission.objects.get(dataroom_groups_id=each.id)
                            data = utils.set_permission(group_permission, data)
                    elif da.is_la_user == True:
                        for each in da.end_user_group.all():
                            # print("each ======>",each)
                            group_permission = DataroomGroupPermission.objects.get(dataroom_groups_id=each.id)
                            data = utils.set_permission(group_permission, data)
                    else:
                        data = {'is_overview':True,'is_q_and_a':True, 'is_reports':True, 'is_updates':True, 'is_users_and_permission':True, 'is_watermarking':True, 'is_drm':True,'is_edit_index':True, 'is_voting':True}
                        break;
            else:
                data = {'is_overview':True,'is_q_and_a':True, 'is_reports':True, 'is_updates':True, 'is_users_and_permission':True, 'is_watermarking':True, 'is_drm':True,'is_edit_index':True, 'is_voting':True}
            # print(data,'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            return Response(data)
        else:
            return Response(None)
# class CreateDataroomGroupFolderPermissions(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )


#   def get_children(self, pk, parent_id, group_id, user, perm):

#       data = []

#       document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=False, parent_folder=parent_id, is_deleted=False).order_by('index')
#       for doc in document:
#           docu = DataroomFolder.objects.get(id = doc.id)
#           docu_serializer = DataroomFolderSerializer(docu)
#           datas = docu_serializer.data
#           # utils.getIndexofFolder(datas)
#           datas['perm'] = {}
#           docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
#           if datas['is_folder']:
#               datas['hasChildren'] = True
#               datas['perm'] = perm
#               datas['children'] = self.get_children(pk, datas.get('id'), group_id, user, perm)
#           else:
#               datas['perm'] = perm
#               if perm['is_upload']:
#                   datas['perm']['is_upload'] = False

#               datas['hasChildren'] = False

#           data.append(datas)
#       return data

#   def update_children(self, data, pk, group_id, user):
#       for da in data:
#           if 'view_indeterminate' in da:
#               if da['view_indeterminate'] == True:
#                   da['perm']['is_view_only']
#           folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
#           # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
#           # print("data ======>",da['perm'])
#           if not folder_permission:
#               serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
#               if serializer.is_valid():
#                   serializer.save()
#           else:
#               serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
#               if serializer.is_valid():
#                   serializer.save()

#           folder_obj = DataroomFolder.objects.get(id=da['id'])
#           flag = True
#           while flag:
#               perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
#               if perm_obj.is_no_access == False:
#                   perm_obj.is_access = True
#                   perm_obj.save()
#                   if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
#                       flag = False
#                   else:
#                       folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
#                       perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=group_id).last()
#                       if perm_obj.is_no_access == False:
#                           perm1_obj.is_access = True
#                           perm1_obj.is_no_access = False
#                       else:
#                           perm1_obj.is_access = False
#                       perm1_obj.save()
#                       folder_obj = folder1_obj
#                       flag = False
#               else:
#                   flag = False

#           if not 'children' in da and da['hasChildren']==True:
#               da['children'] = []
#               da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

#           if 'children' in da:
#               if len(da['children']) > 0:
#                   self.update_children(da['children'],pk, group_id, user)
#       return True
    
#   def post(self, request, pk, format=None):
#       test = []
#       user = request.user
#       data = request.data
#       # print(data,"data for post in update")
#       # print("filtered ======",DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=data['group_id']).values())
#       # print("value of data in post 10_april =======>",data,'___________',data['group_id'])
#       # print(data['file'])
#       # print('this api  _____________1')

#       if 'file' in  data:
#           files = data['file']
#           # print('hello this workig')
#           for da in files:
#               if da['view_indeterminate'] == True:
#                   da['perm']['is_view_only']
#               folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).first()
#               # print("permission_for_document ===>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).values())
#               # print("permissions------",folder_permission)
#               if not folder_permission:
#                   serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': request.data['group_id']})
#                   if serializer.is_valid():
#                       serializer.save()
#               else:
#                   # added by harish
#                   # print("only view print permission ===>",da['perm']['is_view_and_print'])
#                   if da['perm']['is_view_and_print']:
#                       da['perm']['is_view_only'] = True
#                   if da['perm']['is_view_and_print_and_download']:
#                       da['perm']['is_view_only'] = True
#                       da['perm']['is_view_and_print']=True
#                   print("all permissions_10_april =====>",da['perm'],folder_permission.id)
                        

#                   serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
#                   if serializer.is_valid():
#                       serializer.save()
#                       # print(serializer.data,'here kkkk')
#                       # print("false b/lock")

#               folder_obj = DataroomFolder.objects.get(id=da['id'])
#               flag = True
#               while flag:
#                   perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id'])
#                   if perm_obj.is_no_access == False :
#                       perm_obj.is_access = True
#                       perm_obj.save()
#                       #working on this harish
#                       # if perm_obj.is_view_and_print_and_download:
#                       #     perm_obj.is_access = True
#                       #     perm_obj.is_view_only=True
#                       #     perm_obj.is_view_and_print = True
#                           # end 

#                       if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
#                           flag = False
#                       else:
#                           folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
#                           perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
#                           if perm_obj.is_no_access == False:
#                               perm1_obj.is_access = True
#                               perm1_obj.is_no_access = False
#                           else:
#                               perm1_obj.is_access = False
#                           perm1_obj.save()
#                           folder_obj = folder1_obj
#                           flag = False
#                   else:
#                       flag = False

#               if not 'children' in da and da['hasChildren']==True:
#                   da['children'] = []
#                   da['children'] = self.get_children(pk, da['id'], data['group_id'], user, da['perm'])
#                   # print("flag set by ====>",da['perm'])
                        
#               if 'children' in da:
#                   if len(da['children']) > 0:
#                       self.update_children(da['children'],pk, data['group_id'], user)
#                       # print('upfdate children calling ________________________')
#       flagforget=True
#       return Response(flagforget,status=status.HTTP_201_CREATED)

# class CreateDataroomGroupFolderPermissions(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )


#   def get_children(self, pk, parent_id, group_id, user, perm):

#       data = []

#       document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=False, parent_folder=parent_id, is_deleted=False).order_by('index')
#       for doc in document:
#           docu = DataroomFolder.objects.get(id = doc.id)
#           docu_serializer = DataroomFolderSerializer(docu)
#           datas = docu_serializer.data
#           # utils.getIndexofFolder(datas)
#           datas['perm'] = {}
#           docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
#           if datas['is_folder']:
#               datas['hasChildren'] = True
#               datas['perm'] = perm
#               datas['children'] = self.get_children(pk, datas.get('id'), group_id, user, perm)
#           else:
#               datas['perm'] = perm
#               if perm['is_upload']:
#                   datas['perm']['is_upload'] = False

#               datas['hasChildren'] = False

#           data.append(datas)
#       return data

#   def update_children(self, data, pk, group_id, user):
#       for da in data:
#           if 'view_indeterminate' in da:
#               if da['view_indeterminate'] == True:
#                   da['perm']['is_view_only']
#           folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
#           # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
#           # print("data ======>",da['perm'])
#           if not folder_permission:
#               serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
#               if serializer.is_valid():
#                   serializer.save()
#           else:
#               serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
#               if serializer.is_valid():
#                   serializer.save()

#           folder_obj = DataroomFolder.objects.get(id=da['id'])
#           flag = True
#           while flag:
#               perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
#               if perm_obj.is_no_access == False:
#                   perm_obj.is_access = True
#                   perm_obj.is_view_only = True
#                   perm_obj.save()
#                   if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
#                       flag = False
#                   else:
#                       folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
#                       perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=group_id).last()
#                       if perm_obj.is_no_access == False:
#                           perm1_obj.is_access = True
#                           perm1_obj.is_view_only = True
#                           perm1_obj.is_no_access = False
#                       else:
#                           perm1_obj.is_access = False
#                       perm1_obj.save()
#                       folder_obj = folder1_obj
#                       flag = False
#               else:
#                   flag = False

#           if not 'children' in da and da['hasChildren']==True:
#               da['children'] = []
#               da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

#           if 'children' in da:
#               if len(da['children']) > 0:
#                   self.update_children(da['children'],pk, group_id, user)
#       return True
    
#   def post(self, request, pk, format=None):
#       test = []
#       user = request.user
#       data = request.data
#       print(data,"data for post in update")
#       # print("filtered ======",DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=data['group_id']).values())
#       # print("value of data in post 10_april =======>",data,'___________',data['group_id'])
#       # print(data['file'])
#       # print('this api  _____________1')

#       if 'file' in  data:
#           files = data['file']
#           # print('hello this workig')
#           for da in files:
#               if da['view_indeterminate'] == True:
#                   da['perm']['is_view_only']
#               folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).first()
#               # print("permission_for_document ===>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).values())
#               # print("permissions------",folder_permission)
#               if not folder_permission:
#                   serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': request.data['group_id']})
#                   if serializer.is_valid():
#                       serializer.save()
#               else:
#                   # added by harish
#                   # print("only view print permission ===>",da['perm']['is_view_and_print'])
#                   if da['perm']['is_view_and_print']:
#                       da['perm']['is_view_only'] = True
#                   if da['perm']['is_view_and_print_and_download']:
#                       da['perm']['is_view_only'] = True
#                       da['perm']['is_view_and_print']=True
#                   # print("all permissions_10_april =====>",da['perm'],folder_permission.id)
                        

#                   serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
#                   if serializer.is_valid():
#                       serializer.save()
#                       # print(serializer.data,'here kkkk')
#                       # print("false b/lock")

#               folder_obj = DataroomFolder.objects.get(id=da['id'])
#               if folder_obj.is_folder:
#                   da['hasChildren']=True
#               else:
#                   da['hasChildren']=False
#               flag = True
#               parentfoderupdateid=da['id']
#               while flag:
#                   perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=parentfoderupdateid,dataroom_id=pk,dataroom_groups_id=data['group_id'])
#                   if perm_obj.is_no_access == False :
#                       perm_obj.is_access = True
#                       perm_obj.is_view_only = True
#                       perm_obj.save()
#                       #working on this harish
#                       # if perm_obj.is_view_and_print_and_download:
#                       #     perm_obj.is_access = True
#                       #     perm_obj.is_view_only=True
#                       #     perm_obj.is_view_and_print = True
#                           # end 

#                       if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
#                           flag = False
#                       else:
#                           folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
#                           perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
#                           if perm1_obj.exists()==False:
#                               DataroomGroupFolderSpecificPermissions.objects.create(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'],permission_given_by_id=user.id)
#                               perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
#                           else:
#                               perm1_obj=perm1_obj.last()
#                           if perm_obj.is_no_access == False:
#                               perm1_obj.is_access = True
#                               perm1_obj.is_view_only = True
#                               perm1_obj.is_no_access = False
#                           else:
#                               perm1_obj.is_access = False
#                           perm1_obj.save()
#                           folder_obj = folder1_obj
#                           parentfoderupdateid=folder1_obj.id
#                   else:
#                       flag = False

#               if not 'children' in da and da['hasChildren']==True:
#                   da['children'] = []
#                   da['children'] = self.get_children(pk, da['id'], data['group_id'], user, da['perm'])
#                   # print("flag set by ====>",da['perm'])
                        
#               if 'children' in da:
#                   if len(da['children']) > 0:
#                       self.update_children(da['children'],pk, data['group_id'], user)
#                       # print('upfdate children calling ________________________')
#       flagforget=True
#       return Response(flagforget,status=status.HTTP_201_CREATED)


class CreateDataroomGroupFolderPermissions(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


    def get_children(self, pk, parent_id, group_id, user, perm):

        data = []

        document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=False, parent_folder=parent_id, is_deleted=False).order_by('index')
        for doc in document:
            # docu = DataroomFolder.objects.get(id = doc.id)
            # docu_serializer = DataroomFolderSerializer(docu)
            # datas = docu_serializer.data
            # utils.getIndexofFolder(datas)
            datas = {}
            datas['id']=doc.id
            datas['is_folder']=doc.is_folder
            datas['perm'] = {}
            # docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
            if datas['is_folder']:

                datas['hasChildren'] = True
                datas['perm'] = perm
                datas['children'] = self.get_children(pk, datas.get('id'), group_id, user, perm)
            else:

                datas['perm'] = perm
                # if perm['is_upload']:
                #   datas['perm']['is_upload'] = False

                datas['hasChildren'] = False
            # print('------------datas',datas)
            data.append(datas)
        return data


    def update_children(self, data, pk, group_id, user):
        update_permission=data[0]['perm']['is_upload']
        for da in data:
            if 'view_indeterminate' in da:
                if da['view_indeterminate'] == True:
                    da['perm']['is_view_only']
            folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
            # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
            # print("data ======>",da['perm'])
            if update_permission==True:
                if da['is_folder']==False:
                    da['perm']['is_upload']=False 
                    # da['perm']['is_irm_protected']=is_irm_protected 
                else:
                    da['perm']['is_upload']=update_permission  
                    # da['perm']['is_irm_protected']=False 
            if not folder_permission:
                # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
                # if serializer.is_valid():
                #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id,is_no_access=da['perm']['is_no_access'],
                is_view_only=da['perm']['is_view_only'],
                is_view_and_print=da['perm']['is_view_and_print'],
                is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                is_upload=da['perm']['is_upload'],
                is_watermarking=da['perm']['is_watermarking'],
                is_drm=da['perm']['is_drm'],
                is_editor=da['perm']['is_editor'],
                permission_given_by_id=user.id,
                is_shortcut=da['perm']['is_shortcut'],
                # access_revoke=da['perm']['access_revoke']
                )

            else:
                # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                # if serializer.is_valid():
                #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).update(is_no_access=da['perm']['is_no_access'],
                is_view_only=da['perm']['is_view_only'],
                is_view_and_print=da['perm']['is_view_and_print'],
                is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                is_upload=da['perm']['is_upload'],
                is_watermarking=da['perm']['is_watermarking'],
                is_drm=da['perm']['is_drm'],
                is_editor=da['perm']['is_editor'],
                permission_given_by_id=user.id,
                is_shortcut=da['perm']['is_shortcut'],
                # access_revoke=da['perm']['access_revoke']
                )

            # folder_obj = DataroomFolder.objects.get(id=da['id'])
            # flag = True
            # while flag:
            #   perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
            #   if perm_obj.is_no_access == False:
            #       perm_obj.is_access = True
            #       perm_obj.is_view_only = True
            #       perm_obj.save()
            #       if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
            #           flag = False
            #       else:
            #           folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
            #           perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=group_id).last()
            #           if perm_obj.is_no_access == False:
            #               perm1_obj.is_access = True
            #               perm1_obj.is_view_only = True
            #               perm1_obj.is_no_access = False
            #           else:
            #               perm1_obj.is_access = False
            #           perm1_obj.save()
            #           folder_obj = folder1_obj
            #           flag = False
            #   else:
            #       flag = False

            # if not 'children' in da and da['hasChildren']==True:
            #   da['children'] = []
            #   da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

            if 'children' in da:
                if len(da['children']) > 0:
                    self.update_children(da['children'],pk, group_id, user)
        return True
    
    # def update_children(self, data, pk, group_id, user):
    #   for da in data:
    #       if 'view_indeterminate' in da:
    #           if da['view_indeterminate'] == True:
    #               da['perm']['is_view_only']
    #       folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
    #       # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
    #       # print("data ======>",da['perm'])
    #       if not folder_permission:
    #           serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
    #           if serializer.is_valid():
    #               serializer.save()
    #       else:
    #           serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
    #           if serializer.is_valid():
    #               serializer.save()

    #       folder_obj = DataroomFolder.objects.get(id=da['id'])
    #       perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
    #       if perm_obj.is_no_access == False:
    #           perm_obj.is_access = True
    #           perm_obj.is_view_only = True
    #           perm_obj.save()
    #       # if not 'children' in da and da['hasChildren']==True:
    #       #   da['children'] = []
    #       #   da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

    #       # if 'children' in da:
    #       #   if len(da['children']) > 0:
    #       #       self.update_children(da['children'],pk, group_id, user)
    #   return True

    def post(self, request, pk, format=None):
        test = []
        user = request.user
        data = request.data
        # print("filtered ======",DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=data['group_id']).values())
        # print("value of data in post 10_april =======>",data,'___________',data['group_id'])
        # print(data['file'])
        # print('this api  _____________1')

        if 'file' in  data:
            files = data['file']
            # print('hello this workig')
            for da in files:
                if da['view_indeterminate'] == True:
                    da['perm']['is_view_only']
                folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).first()
                # print("permission_for_document ===>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).values())
                # print("permissions------",folder_permission)
                if not folder_permission:
                    # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': request.data['group_id']})
                    # if serializer.is_valid():
                    #     serializer.save()
                    DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id'],is_no_access=da['perm']['is_no_access'],
                    is_view_only=da['perm']['is_view_only'],
                    is_view_and_print=da['perm']['is_view_and_print'],
                    is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                    is_upload=da['perm']['is_upload'],
                    is_watermarking=da['perm']['is_watermarking'],
                    is_drm=da['perm']['is_drm'],
                    is_editor=da['perm']['is_editor'],
                    permission_given_by_id=user.id,
                    is_shortcut=da['perm']['is_shortcut'],
                    is_irm_protected=da['perm']['is_irm_protected']
                    # access_revoke=da['perm']['access_revoke']
                    )
                else:
                    # added by harish
                    # print("only view print permission ===>",da['perm']['is_view_and_print'])
                    if da['perm']['is_view_and_print']:
                        da['perm']['is_view_only'] = True
                    if da['perm']['is_view_and_print_and_download']:
                        da['perm']['is_view_only'] = True
                        da['perm']['is_view_and_print']=True
                    # print("all permissions_10_april =====>",da['perm'],folder_permission.id)
                        

                    # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                    # if serializer.is_valid():
                    #     serializer.save()
                    DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).update(is_no_access=da['perm']['is_no_access'],
                    is_view_only=da['perm']['is_view_only'],
                    is_view_and_print=da['perm']['is_view_and_print'],
                    is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                    is_upload=da['perm']['is_upload'],
                    is_watermarking=da['perm']['is_watermarking'],
                    is_drm=da['perm']['is_drm'],
                    is_editor=da['perm']['is_editor'],
                    permission_given_by_id=user.id,
                    is_shortcut=da['perm']['is_shortcut'],
                    is_irm_protected=da['perm']['is_irm_protected'],
                    # access_revoke=da['perm']['access_revoke']
                    )
                        # print(serializer.data,'here kkkk')
                        # print("false b/lock")

                folder_obj = DataroomFolder.objects.get(id=da['id'])
                if folder_obj.is_folder:
                    da['hasChildren']=True
                else:
                    da['hasChildren']=False
                flag = True
                parentfoderupdateid=da['id']
                while flag:
                    perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=parentfoderupdateid,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                    if perm_obj.is_no_access == False :
                        perm_obj.is_access = True
                        perm_obj.is_view_only = True
                        perm_obj.save()
                        #working on this harish
                        # if perm_obj.is_view_and_print_and_download:
                        #     perm_obj.is_access = True
                        #     perm_obj.is_view_only=True
                        #     perm_obj.is_view_and_print = True
                            # end 

                        if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
                            flag = False
                        else:
                            folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
                            perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                            if perm1_obj.exists()==False:
                                DataroomGroupFolderSpecificPermissions.objects.create(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'],permission_given_by_id=user.id)
                                perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                            else:
                                perm1_obj=perm1_obj.last()
                            if perm_obj.is_no_access == False:
                                perm1_obj.is_access = True
                                perm1_obj.is_view_only = True
                                perm1_obj.is_no_access = False
                            else:
                                perm1_obj.is_access = False
                            perm1_obj.save()
                            folder_obj = folder1_obj
                            parentfoderupdateid=folder1_obj.id
                    else:
                        flag = False

                if not 'children' in da and da['hasChildren']==True:
                    da['children'] = []
                    da['children'] = self.get_children(pk, da['id'], data['group_id'], user, da['perm'])
                    # print("flag set by ====>",da['perm'])
                        
                if 'children' in da:
                    if len(da['children']) > 0:
                        self.update_children(da['children'],pk, data['group_id'], user)
                        # print('upfdate children calling ________________________')
        flagforget=True
        return Response(flagforget,status=status.HTTP_201_CREATED)













class CreateDataroomGroupFolderPermissionsForTime(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


    def get_children(self, pk, parent_id, group_id, user, perm):

        data = []

        document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=False, parent_folder=parent_id, is_deleted=False).order_by('index')
        for doc in document:
            # docu = DataroomFolder.objects.get(id = doc.id)
            # docu_serializer = DataroomFolderSerializer(docu)
            # datas = docu_serializer.data
            # utils.getIndexofFolder(datas)
            datas = {}
            datas['id']=doc.id
            datas['is_folder']=doc.is_folder
            datas['perm'] = {}
            # docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
            if datas['is_folder']:

                datas['hasChildren'] = True
                datas['perm'] = perm
                datas['children'] = self.get_children(pk, datas.get('id'), group_id, user, perm)
            else:

                datas['perm'] = perm
                # if perm['is_upload']:
                #   datas['perm']['is_upload'] = False

                datas['hasChildren'] = False
            # print('------------datas',datas)
            data.append(datas)
        return data


    def update_children(self, data, pk, group_id, user):
        # update_permission=data[0]['perm']['is_upload']
        for da in data:
            # if 'view_indeterminate' in da:
            #     if da['view_indeterminate'] == True:
            #         da['perm']['is_view_only']
            folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
            # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
            # print("data ======>",da['perm'])
            # if update_permission==True:
            #     if da['is_folder']==False:
            #         da['perm']['is_upload']=False   
            #     else:
            #         da['perm']['is_upload']=update_permission   

            if not folder_permission:
                # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
                # if serializer.is_valid():
                #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id,


                folder_timer_upload_ristrict=da['perm']['folder_timer_upload_ristrict'],
                folder_timer_upload_ristrict_date=da['perm']['folder_timer_upload_ristrict_date']
                # is_no_access=da['perm']['is_no_access'],
                # is_view_only=da['perm']['is_view_only'],
                # is_view_and_print=da['perm']['is_view_and_print'],
                # is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                # is_upload=da['perm']['is_upload'],
                # is_watermarking=da['perm']['is_watermarking'],
                # is_drm=da['perm']['is_drm'],
                # is_editor=da['perm']['is_editor'],
                # permission_given_by_id=user.id,
                # is_shortcut=da['perm']['is_shortcut'],
                # access_revoke=da['perm']['access_revoke']
                )

            else:
                # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                # if serializer.is_valid():
                #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).update(
                folder_timer_upload_ristrict=da['perm']['folder_timer_upload_ristrict'],
                folder_timer_upload_ristrict_date=da['perm']['folder_timer_upload_ristrict_date']
                #     is_no_access=da['perm']['is_no_access'],
                # is_view_only=da['perm']['is_view_only'],
                # is_view_and_print=da['perm']['is_view_and_print'],
                # is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                # is_upload=da['perm']['is_upload'],
                # is_watermarking=da['perm']['is_watermarking'],
                # is_drm=da['perm']['is_drm'],
                # is_editor=da['perm']['is_editor'],
                # permission_given_by_id=user.id,
                # is_shortcut=da['perm']['is_shortcut'],
                # access_revoke=da['perm']['access_revoke']
                )

            # folder_obj = DataroomFolder.objects.get(id=da['id'])
            # flag = True
            # while flag:
            #   perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
            #   if perm_obj.is_no_access == False:
            #       perm_obj.is_access = True
            #       perm_obj.is_view_only = True
            #       perm_obj.save()
            #       if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
            #           flag = False
            #       else:
            #           folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
            #           perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=group_id).last()
            #           if perm_obj.is_no_access == False:
            #               perm1_obj.is_access = True
            #               perm1_obj.is_view_only = True
            #               perm1_obj.is_no_access = False
            #           else:
            #               perm1_obj.is_access = False
            #           perm1_obj.save()
            #           folder_obj = folder1_obj
            #           flag = False
            #   else:
            #       flag = False

            # if not 'children' in da and da['hasChildren']==True:
            #   da['children'] = []
            #   da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

            if 'children' in da:
                if len(da['children']) > 0:
                    self.update_children(da['children'],pk, group_id, user)
        return True
    
    # def update_children(self, data, pk, group_id, user):
    #   for da in data:
    #       if 'view_indeterminate' in da:
    #           if da['view_indeterminate'] == True:
    #               da['perm']['is_view_only']
    #       folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
    #       # print("updated ====>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).values())
    #       # print("data ======>",da['perm'])
    #       if not folder_permission:
    #           serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
    #           if serializer.is_valid():
    #               serializer.save()
    #       else:
    #           serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
    #           if serializer.is_valid():
    #               serializer.save()

    #       folder_obj = DataroomFolder.objects.get(id=da['id'])
    #       perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).last()
    #       if perm_obj.is_no_access == False:
    #           perm_obj.is_access = True
    #           perm_obj.is_view_only = True
    #           perm_obj.save()
    #       # if not 'children' in da and da['hasChildren']==True:
    #       #   da['children'] = []
    #       #   da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

    #       # if 'children' in da:
    #       #   if len(da['children']) > 0:
    #       #       self.update_children(da['children'],pk, group_id, user)
    #   return True

    def post(self, request, pk, format=None):
        test = []
        user = request.user
        data = request.data
        # print("filtered ======",DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=data['group_id']).values())
        # print("value of data in post 10_april =======>",data,'___________',data['group_id'])
        # print(data['file'])
        # print('this api  _____________1')

        if 'file' in  data:
            files = data['file']
            # print('hello this workig')
            for da in files:
                # if da['view_indeterminate'] == True:
                #     da['perm']['is_view_only']
                folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).first()
                # print("permission_for_document ===>",DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).values())
                # print("permissions------",folder_permission)
                if not folder_permission:
                    # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': request.data['group_id']})
                    # if serializer.is_valid():
                    #     serializer.save()
                    DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id'],
                    folder_timer_upload_ristrict=da['perm']['folder_timer_upload_ristrict'],
                    folder_timer_upload_ristrict_date=da['perm']['folder_timer_upload_ristrict_date']
                    #     is_no_access=da['perm']['is_no_access'],
                    # is_view_only=da['perm']['is_view_only'],
                    # is_view_and_print=da['perm']['is_view_and_print'],
                    # is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                    # is_upload=da['perm']['is_upload'],
                    # is_watermarking=da['perm']['is_watermarking'],
                    # is_drm=da['perm']['is_drm'],
                    # is_editor=da['perm']['is_editor'],
                    # permission_given_by_id=user.id,
                    # is_shortcut=da['perm']['is_shortcut'],
                    # access_revoke=da['perm']['access_revoke']
                    )
                else:
                    # added by harish
                    # print("only view print permission ===>",da['perm']['is_view_and_print'])
                    # if da['perm']['is_view_and_print']:
                    #     da['perm']['is_view_only'] = True
                    # if da['perm']['is_view_and_print_and_download']:
                    #     da['perm']['is_view_only'] = True
                    #     da['perm']['is_view_and_print']=True
                    # print("all permissions_10_april =====>",da['perm'],folder_permission.id)
                        

                    # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                    # if serializer.is_valid():
                    #     serializer.save()
                    DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).update(
                    folder_timer_upload_ristrict=da['perm']['folder_timer_upload_ristrict'],
                    folder_timer_upload_ristrict_date=da['perm']['folder_timer_upload_ristrict_date']
                        # is_no_access=da['perm']['is_no_access'],
                    # is_view_only=da['perm']['is_view_only'],
                    # is_view_and_print=da['perm']['is_view_and_print'],
                    # is_view_and_print_and_download=da['perm']['is_view_and_print_and_download'],
                    # is_upload=da['perm']['is_upload'],
                    # is_watermarking=da['perm']['is_watermarking'],
                    # is_drm=da['perm']['is_drm'],
                    # is_editor=da['perm']['is_editor'],
                    # permission_given_by_id=user.id,
                    # is_shortcut=da['perm']['is_shortcut'],
                    # access_revoke=da['perm']['access_revoke']
                    )
                        # print(serializer.data,'here kkkk')
                        # print("false b/lock")

                if DataroomGroupPermission.objects.filter(upload_ristrict_with_timer=False,dataroom_id=pk,dataroom_groups_id=data['group_id']).exists():
                    if da['perm']['folder_timer_upload_ristrict']==True:
                        DataroomGroupPermission.objects.filter(upload_ristrict_with_timer=False,dataroom_id=pk,dataroom_groups_id=data['group_id']).update(upload_ristrict_with_timer=True)
                folder_obj = DataroomFolder.objects.get(id=da['id'])
                if folder_obj.is_folder:
                    da['hasChildren']=True
                else:
                    da['hasChildren']=False
                flag = True
                parentfoderupdateid=da['id']
                # while flag:
                #     perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=parentfoderupdateid,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                #     if perm_obj.is_no_access == False :
                #         perm_obj.is_access = True
                #         perm_obj.is_view_only = True
                #         perm_obj.save()
                #         #working on this harish
                #         # if perm_obj.is_view_and_print_and_download:
                #         #     perm_obj.is_access = True
                #         #     perm_obj.is_view_only=True
                #         #     perm_obj.is_view_and_print = True
                #             # end 

                #         if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
                #             flag = False
                #         else:
                #             folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
                #             perm1_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                #             if perm1_obj.exists()==False:
                #                 DataroomGroupFolderSpecificPermissions.objects.create(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'],permission_given_by_id=user.id)
                #                 perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                #             else:
                #                 perm1_obj=perm1_obj.last()
                #             if perm_obj.is_no_access == False:
                #                 perm1_obj.is_access = True
                #                 perm1_obj.is_view_only = True
                #                 perm1_obj.is_no_access = False
                #             else:
                #                 perm1_obj.is_access = False
                #             perm1_obj.save()
                #             folder_obj = folder1_obj
                #             parentfoderupdateid=folder1_obj.id
                #     else:
                #         flag = False

                if not 'children' in da and da['hasChildren']==True:
                    da['children'] = []
                    da['children'] = self.get_children(pk, da['id'], data['group_id'], user, da['perm'])
                    # print("flag set by ====>",da['perm'])
                        
                if 'children' in da:
                    if len(da['children']) > 0:
                        self.update_children(da['children'],pk, data['group_id'], user)
                        # print('upfdate children calling ________________________')
        flagforget=True
        return Response(flagforget,status=status.HTTP_201_CREATED)












class GetGroupReports(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        group = DataroomGroups.objects.filter(dataroom_id=pk)
        serializer = DataroomGroupsSerializer(group, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

   
class GetUsersGroupReports(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom = Dataroom.objects.get(id=pk)
        group_id = int(request.GET.get("group"))
        removed = request.GET.get("removed")
        page = request.GET.get("page")
        # print('----------------',page)
        page1=str(page)+'0'
        # print('-----------------------',page1)
        page2=int(page)-1
        if page2 != 0:
            page2=str(page2)+'0'
        # print('-----------------------',page2)
        page1=int(page1)
        page2=int(page2)
        if removed == 'false':
            removed = False
        else:
            removed = True
        if group_id == 0 :
            if removed==True:
                member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).order_by('-date_updated')
            else:
                member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).order_by('-date_joined')
            member1=member[page2:page1]
        elif group_id == -1:
            if removed==True:
                member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).order_by('-date_updated')
            else:
                member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).order_by('-date_joined')
            member1=member[page2:page1]
        else:
            if removed==True:
                member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).order_by('-date_updated')
            else:
                member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).order_by('-date_joined')
            member1=member[page2:page1]
        serializer = DataroomMembersSerializer(member1, many=True)
        data = serializer.data
        import datetime

        for da in data:
            memb = DataroomMembers.objects.get(id=da['id'])
            da['invitatation_acceptance_date']=''
            if InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).exists():
                invitationdata=InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).last()
                # if memb.memberactivestatus==True:
                tempdateee1 = invitationdata.invitatation_acceptance_date
                # tempdateee1 = datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f')
                da['invitatation_acceptance_date']=tempdateee1
            elif memb:
            # elif memb.memberactivestatus==True and memb.is_dataroom_admin==True:
                tempdateee1 = memb.date_joined
                # tempdateee1 = datetime.datetime.strptime(str(memb.date_joined), '%Y-%m-%d %H:%M:%S.%f')
                
                da['invitatation_acceptance_date']=tempdateee1          
            try:
                group = DataroomGroups.objects.get(id=memb.end_user_group.all().first().id)
                da['group'] = group.group_name
            except:
                if memb.is_dataroom_admin==True:
                    da['group'] = "Admin"
                else:

                    da['group'] = memb.group_name

        datas= {}
        datas['users'] = data
        datas['count']= member.count()
        # if removed == False and (group_id == 0 or group_id == -1):
        #   da = {}
        #   serializer = UserSerializer(dataroom.user, many=False)
        #   serializer_data = serializer.data
        #   da['member'] = serializer_data
        #   da['member_added_by'] = serializer_data
        #   da['group'] = "Admin"
        #   tempdateee = datetime.datetime.strftime(datetime.datetime.strptime(str(dataroom.created_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
        #   da['date_joined'] = tempdateee
        #   datas['users'].append(da)
        # print(datas)          

        return Response(datas, status=status.HTTP_201_CREATED)

class GetLastDataroomView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, user, format=None):

        workspace_view = DataroomView.objects.filter(dataroom_id=pk, user_id=user).order_by('id').reverse().first()
        folder_workspace_data = DataroomViewSerializer(workspace_view, many=False).data
        # print(folder_workspace_data)
        return Response(folder_workspace_data, status=status.HTTP_201_CREATED)
        



# class ExportUsersGroups(APIView):
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def get(self, request, pk, format=None):
#         user = request.user
#         dataroom = Dataroom.objects.get(id=pk)
#         group_id = int(request.GET.get("group"))
#         removed = request.GET.get("removed")

#         if removed == 'false':
#             removed = False
#         else:
#             removed = True
#         print('group----', dataroom.user_id)
#         if group_id == 0 :
#             member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).order_by('-date_joined')
#         elif group_id == -1:
#             member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).order_by('-date_joined')
#         else:
#             member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).order_by('-date_joined')
#         serializer = DataroomMembersSerializer(member, many=True)
#         data = serializer.data
#         import datetime
#         print(data,'  yyyyyyyyyyy uuuuuuuuuuuu')
#         for da in data:

#             memb = DataroomMembers.objects.get(id=da['id'])
#             da['invitatation_acceptance_date']=''
#             if InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).exists():
#                 invitationdata=InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).last()
#                 if memb.memberactivestatus==True:
#                     tempdateee1 = datetime.datetime.strftime(datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
#                     da['invitatation_acceptance_date']=tempdateee1
#                 tempdateee22 = datetime.datetime.strftime(datetime.datetime.strptime(str(invitationdata.invitatation_sent_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')               
#                 da['invitatation_sent_date']=tempdateee22
#             elif memb.memberactivestatus==True and memb.is_dataroom_admin==True:
#                 tempdateee1 = datetime.datetime.strftime(datetime.datetime.strptime(str(memb.date_joined), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
#                 da['invitatation_acceptance_date']=tempdateee1
#                 da['invitatation_sent_date']=tempdateee1

#             try:
#                 group = DataroomGroups.objects.get(id=memb.end_user_group.all().first().id)
#                 da['group'] = group.group_name
#             except:
#                 da['group'] = "Admin"
#             # invituser =InviteUser.objects.filter(dataroom_invitation=pk,invitiation_receiver=memb.member_id).last()
#             # # print("-----------------------",invituser.is_invitation_accepted)
#             # if invituser:
#             #   if invituser.is_invitation_accepted:
#             #       da['date_joined'] = invituser.invitatation_acceptance_date
#             #   else :
#             #       da['date_joined'] = ''
#             # else:
#             #   da['date_joined'] = ''

#         datas= {}
#         datas['users'] = data
#         # if removed == False and (group_id == 0 or group_id == -1):
#         #   da = {}
#         #   serializer = UserSerializer(dataroom.user, many=False)
#         #   serializer_data = serializer.data
#         #   da['member'] = serializer_data
#         #   da['member_added_by'] = serializer_data
#         #   da['group'] = "Admin"

#         #   tempdateee = datetime.datetime.strftime(datetime.datetime.strptime(str(dataroom.created_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')

#         #   da['date_joined'] = tempdateee
#         #   #change made by harish 
#         #   # invituser =InviteUser.objects.filter(dataroom_invitation=pk,invitiation_receiver=memb.member_id).last()
#         #   # # print("-----------------------",invituser.is_invitation_accepted)
#         #   # if invituser:
#         #   #   if invituser.is_invitation_accepted:
#         #   #       da['date_joined'] = invituser.invitatation_acceptance_date
#         #   #   else :
#         #   #       da['date_joined'] = ''
#         #   # else:
#         #   #   da['date_joined'] = ''
#         #   # end
#         #   datas['users'].append(da)

#         from . import utils
#         import csv

#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
#         writer = csv.writer(response)
#         #harish 
#         # print('-------------------------------------------')
#         # print(datas['users'])
#         # print('-------------------------------------------')

#         header_data, datas = utils.getExcelDataUsersGroupsReport(datas['users'])
        
#         writer.writerow(header_data)
#         writer.writerows(datas)
#         return response



from data_documents.models import *
class ExportUsersGroups(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        dataroom = Dataroom.objects.get(id=pk)
        group_id = int(request.GET.get("group"))
        removed = request.GET.get("removed")
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
        
        if removed == 'false':
            removed = False
        else:
            removed = True
        print('group----', dataroom.user_id)
        if group_id == 0 :
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).order_by('-date_joined')
        elif group_id == -1:
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).order_by('-date_joined')
        else:
            member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).order_by('-date_joined')
        serializer = DataroomMembersSerializer(member, many=True)
        data = serializer.data
        import datetime
        timez=''
        if User_time_zone.objects.filter(user_id=user.id).exists():
            user_zone=User_time_zone.objects.filter(user_id=user.id).last()
            timez=user_zone.time_zone.tz
        print(data,'  yyyyyyyyyyy uuuuuuuuuuuu')
        for da in data:

            memb = DataroomMembers.objects.get(id=da['id'])
            da['invitatation_acceptance_date']=''
            if InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).exists():
                invitationdata=InviteUser.objects.filter(invitiation_receiver_id=memb.member,dataroom_invitation=pk).last()
                if memb.memberactivestatus==True:
                    tempdateee1 = datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f')
                    if timez!='':
                        tempdateee1 = convert_to_kolkata(tempdateee1,timez)
                    # else:
                    #     kolkata_time = dateobject                    
                    da['invitatation_acceptance_date']=datetime.datetime.strftime(tempdateee1,'%d/%m/%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                tempdateee22 = datetime.datetime.strptime(str(invitationdata.invitatation_sent_date), '%Y-%m-%d %H:%M:%S.%f')
                tempdateee22 = convert_to_kolkata(tempdateee22,timez)

                da['invitatation_sent_date']=datetime.datetime.strftime(tempdateee22,'%d/%m/%Y %H:%M:%S')+" "+user_zone.time_zone.abbreviation
            elif memb.memberactivestatus==True and memb.is_dataroom_admin==True:
                tempdateee1 = datetime.datetime.strptime(str(memb.date_joined), '%Y-%m-%d %H:%M:%S.%f')
                if timez!='':
                    tempdateee1 = convert_to_kolkata(tempdateee1,timez)
                tempdateee1=datetime.datetime.strftime(tempdateee1,'%d/%m/%Y %H:%M:%S')
                da['invitatation_acceptance_date']=tempdateee1+" "+user_zone.time_zone.abbreviation
                da['invitatation_sent_date']=tempdateee1+" "+user_zone.time_zone.abbreviation

            try:
                group = DataroomGroups.objects.get(id=memb.end_user_group.all().first().id)
                da['group'] = group.group_name
            except:
                da['group'] = "Admin"
            # invituser =InviteUser.objects.filter(dataroom_invitation=pk,invitiation_receiver=memb.member_id).last()
            # # print("-----------------------",invituser.is_invitation_accepted)
            # if invituser:
            #   if invituser.is_invitation_accepted:
            #       da['date_joined'] = invituser.invitatation_acceptance_date
            #   else :
            #       da['date_joined'] = ''
            # else:
            #   da['date_joined'] = ''

        datas= {}
        datas['users'] = data
        # if removed == False and (group_id == 0 or group_id == -1):
        #   da = {}
        #   serializer = UserSerializer(dataroom.user, many=False)
        #   serializer_data = serializer.data
        #   da['member'] = serializer_data
        #   da['member_added_by'] = serializer_data
        #   da['group'] = "Admin"

        #   tempdateee = datetime.datetime.strftime(datetime.datetime.strptime(str(dataroom.created_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')

        #   da['date_joined'] = tempdateee
        #   #change made by harish 
        #   # invituser =InviteUser.objects.filter(dataroom_invitation=pk,invitiation_receiver=memb.member_id).last()
        #   # # print("-----------------------",invituser.is_invitation_accepted)
        #   # if invituser:
        #   #   if invituser.is_invitation_accepted:
        #   #       da['date_joined'] = invituser.invitatation_acceptance_date
        #   #   else :
        #   #       da['date_joined'] = ''
        #   # else:
        #   #   da['date_joined'] = ''
        #   # end
        #   datas['users'].append(da)
        datarooms = Dataroom.objects.get(id=pk)
        # os.chdir('/home/cdms_backend/cdms2/mediaa')
        today = datetime.datetime.today()
        if not os.path.exists(f'/home/cdms_backend/cdms2/media/{file_name_zip}'):
            os.mkdir(f'/home/cdms_backend/cdms2/media/{file_name_zip}')

        file_name = str(datarooms.dataroom_nameFront)+' - User and Groups report .csv'
        from . import utils
        import csv
        with open(f'/home/cdms_backend/cdms2/media/{file_name_zip}/{file_name}', 'w',encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if data == []:
                writer.writerow(['There is no activity performed in this date range']) 

            else:

                datas = []
                for da in data: 
                    status = 'Inactive'
                    if da.get('memberactivestatus'):
                        status = 'Active'
                    if da.get('invitatation_sent_date') == '' or da.get('invitatation_sent_date') == None:
                        date1 = ' '
                    else:
                        # print(da.get('date_joined'))
                        # dateobject=datetime.strptime(str(da.get('date_joined')).replace('T',' '),'%d/%m/%Y %H:%M:%S.%f')
                        date1=da.get('invitatation_sent_date')
                        # date1=datetime.strptime(str(da.get('date_joined')),'%d/%m/%Y %H:%M:%S')

                    act = ()
                    act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'), da.get('group'),date1,da.get('invitatation_acceptance_date'),status,da.get('member_added_by').get('first_name') )
                    datas.append(act)
                header_data = [
                    'User','Group','Invitation Send Date','Dataroom Joining Date','User Status','Invited By'
                    ]
                # return header_data, datas
                # response = HttpResponse(content_type='text/csv')
                # response['Content-Disposition'] = 'attachment; filename='+str(file_name)+''
                # writer = csv.writer(response)
                from . import utils
                import csv

                # response = HttpResponse(content_type='text/csv')
                # response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
                # writer = csv.writer(response)
                # #harish 
                # # print('-------------------------------------------')
                # # print(datas['users'])
                # # print('-------------------------------------------')

                # header_data, datas = utils.getExcelDataUsersGroupsReport(datas['users'])
                
                writer.writerow(header_data)
                writer.writerows(datas)
        # return response
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    # BulkDownloadstatus.objects.filter(id=objid)
        from rest_framework import status
        return Response({"result": True},status=status.HTTP_201_CREATED)






















        # user = request.user
        # group_id = int(request.GET.get("group"))
        # removed = request.GET.get("removed")
        # if removed == 'false':
            # removed = False
        # else:
            # removed = True
        # if group_id == 1 :
            # member = DataroomMembers.objects.filter(dataroom_id=pk, is_dataroom_admin=True, is_deleted=removed)
            # groups = {'group_name':'Admin'}
        # elif group_id == 2 :
            # member = DataroomMembers.objects.filter(dataroom_id=pk, is_la_user=True, is_deleted=removed)
            # groups = DataroomGroups.objects.filter(dataroom_id=pk, limited_access=True)
        # else:
            # member = DataroomMembers.objects.filter(dataroom_id=pk, is_end_user=True, is_deleted=removed)
            # groups = DataroomGroups.objects.filter(dataroom_id=pk, end_user=True)
        # serializer = DataroomMembersSerializer(member, many=True)
        # data = serializer.data
        # for da in data:
            # memb = DataroomMembers.objects.get(id=da['id'])
            # if group_id == 1:
                # da['group'] = 'Admin'
            # else:
                # try:
                    # group = DataroomGroups.objects.get(id=memb.end_user_group_id)
                    # da['group'] = group.group_name
                # except:
                    # da['group'] = ""
        # datas= {}
        # datas['users'] = data
        # from . import utils
        # import csv

        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        # writer = csv.writer(response)
        # #harish 
        # print('-------------------------------------------')
        # print(datas['users'])
        # header_data, datas = utils.getExcelDataUsersGroupsReport(datas['users'])
        
        # writer.writerow(header_data)
        # writer.writerows(datas)
        # return response

class GetUsersStatus(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        data = {}
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        group = int(request.GET.get("type"))
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
        if group == 0:
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False, date_joined__gte=first_date, date_joined__lte=todays_date)
        else:
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False, date_joined__gte=first_date, date_joined__lte=todays_date, end_user_group = group)
        serializer = DataroomMembersSerializer(member, many=True)
        data['data'] = serializer.data
        data['total_users'] = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False,  date_joined__gte=first_date, date_joined__lte=todays_date).count()
        count = 0
        for da in data['data']:
            member_id = da.get("member").get("id")
            # check harish need to fix the issue later 
            # print(user.id)
            # print(member_id)
            # print(pk)
            # status1=User.objects.get(id=member_id).is_active
            #rushi status1=InviteUser.objects.filter(invitiation_receiver=member_id,dataroom_invitation=pk).values_list('is_invitation_accepted',flat=True).last()
            # print('status---------------------------------',status1)
            # print('status')
            # print(da['member']['is_active'])
            #rushi-- if status1 == True :
            #   da['member']['is_active'] = True
            # elif status1 == None:
            #   da['member']['is_active'] = True
            # else:
            # --rushi   da['member']['is_active'] = False
            da['member']['is_active'] = da['memberactivestatus']

            # check end 
            try:
                if da.get('member').get('is_active'):
                    count +=1
                # invite_user = InviteUser.objects.filter(invitiation_receiver_id=member_id).first()
                # if invite_user.is_invitation_accepted == True:
                #     count = count + 1
            except:
                None
            try:
                access_history = AccessHistory.objects.filter(user_id = member_id).last()
                da['last_login'] = access_history.logged_in_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            except:
                da['last_login '] = 'N. A.'
        data['active_users'] = count
        return Response(data, status=status.HTTP_201_CREATED)

# class ExportUsersStatus(APIView):
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def get(self, request, pk, format=None):
#         user = request.user
#         data = {}
#         from_date = request.GET.get('from_date')
#         to_date = request.GET.get('to_date')
#         import datetime
#         todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
#         first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
#         member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False, date_joined__gte=first_date, date_joined__lte=todays_date)
#         serializer = DataroomMembersSerializer(member, many=True)
#         for members in serializer.data:
#             members['invitatation_acceptance_date']=''
#             if InviteUser.objects.filter(invitiation_receiver_id=members['member']['id'],dataroom_invitation=pk).exists():
#                 invitationdata=InviteUser.objects.filter(invitiation_receiver_id=members['member']['id'],dataroom_invitation=pk).last()
#                 if members['memberactivestatus']==True:
#                     tempdateee1 = datetime.datetime.strftime(datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
#                     members['invitatation_acceptance_date']=tempdateee1
#                 tempdateee2 = datetime.datetime.strftime(datetime.datetime.strptime(str(invitationdata.invitatation_sent_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
#                 members['invitatation_sent_date']=tempdateee2

#             elif members['memberactivestatus']==True and members['is_dataroom_admin']==True:
#                 members['invitatation_acceptance_date']=members['date_joined']
#                 members['invitatation_sent_date']=members['date_joined']
                        

#             workspace_view = DataroomView.objects.filter(dataroom_id=pk, user_id=members.get('member').get('id')).order_by('id').reverse().first()
#             folder_workspace_data = DataroomViewSerializer(workspace_view, many=False).data
#             members['last_view'] = folder_workspace_data.get('created_date')
#             # print(folder_workspace_data)
#         data = serializer.data
#         # print(data,'rushikesh____________')
#         from . import utils
#         import csv
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
#         writer = csv.writer(response)

#         header_data, datas = utils.getExcelDataUsersStatusReport(data)

#         writer.writerow(header_data)
#         writer.writerows(datas)
#         return response





class ExportUsersStatus(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        data = {}


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
        datarooms = Dataroom.objects.filter(id=pk).last()



        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
        member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False, date_joined__gte=first_date, date_joined__lte=todays_date)
        serializer = DataroomMembersSerializer(member, many=True)
        for members in serializer.data:
            members['invitatation_acceptance_date']=''
            if InviteUser.objects.filter(invitiation_receiver_id=members['member']['id'],dataroom_invitation=pk).exists():
                invitationdata=InviteUser.objects.filter(invitiation_receiver_id=members['member']['id'],dataroom_invitation=pk).last()
                if members['memberactivestatus']==True:
                    tempdateee1 = datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f')
                    # tempdateee1 = datetime.datetime.strftime(datetime.datetime.strptime(str(invitationdata.invitatation_acceptance_date), '%Y-%m-%d %H:%M:%S.%f'),'%d/%m/%Y %H:%M:%S')
                    members['invitatation_acceptance_date']=tempdateee1
                tempdateee2 = datetime.datetime.strptime(str(invitationdata.invitatation_sent_date), '%Y-%m-%d %H:%M:%S.%f')
                members['invitatation_sent_date']=tempdateee2

            elif members['memberactivestatus']==True and members['is_dataroom_admin']==True:
                members['invitatation_acceptance_date']=datetime.datetime.strptime(str(members['date_joined']), '%Y-%m-%d %H:%M:%S.%f')
                # members['invitatation_acceptance_date']=members['date_joined']
                # members['invitatation_sent_date']=members['date_joined']
                members['invitatation_sent_date']=datetime.datetime.strptime(str(members['date_joined']), '%Y-%m-%d %H:%M:%S.%f')
                        

            workspace_view = DataroomView.objects.filter(dataroom_id=pk, user_id=members.get('member').get('id')).order_by('id').reverse().first()
            folder_workspace_data = DataroomViewSerializer(workspace_view, many=False).data
            members['last_view'] = folder_workspace_data.get('created_date')
            # print(folder_workspace_data)
        data = serializer.data
        # print(data,'rushikesh____________')
        if not os.path.exists(f'/home/cdms_backend/cdms2/media/{file_name_zip}'):
            os.mkdir(f'/home/cdms_backend/cdms2/media/{file_name_zip}')
        # import csv
        file_name = str(datarooms.dataroom_nameFront)+' - User Status Report - '+str(datetime.datetime.strptime( to_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+' -to- '+str(datetime.datetime.strptime( from_date, '%Y-%m-%d').strftime('%Y-%m-%d'))+'.csv'
        


        from . import utils
        import csv
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        # writer = csv.writer(response)

        # header_data, datas = utils.getExcelDataUsersStatusReport(data)
        with open(f'/home/cdms_backend/cdms2/media/{file_name_zip}/{file_name}', 'w',encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if data == []:
                writer.writerow(['There is no activity performed in this date range']) 

            else:
                datas = []
                timez=''
                if User_time_zone.objects.filter(user_id=user.id).exists():
                    user_zone=User_time_zone.objects.filter(user_id=user.id).last()
                    timez=user_zone.time_zone.tz
                for da in data:
                    status = 'Inactive'
                    if da.get('memberactivestatus'):
                        status = 'Active'

                    
                    if da.get('is_dataroom_admin') == True:
                        member_type = 'Admin'
                    elif da.get('is_end_user') == True:
                        member_type = 'End User'
                    else:
                        member_type = 'Limited Access User'
                    act = ()
                    temppp2=da.get('invitatation_sent_date')
                    # temppp2 = datetime.strptime(temppp,"%Y-%m-%dT%H:%M:%S.%f")
                    # print('_____this date___________',temppp2)
                    date22=da.get('last_view')
                    invitatation_acceptance_date=da.get('invitatation_acceptance_date')
                    print('------------------------------typeeeee',type(da.get('invitatation_acceptance_date')))
                    if timez!='':
                        
                        temppp2 = convert_to_kolkata(temppp2,timez)
                        temppp2 = datetime.datetime.strftime(temppp2, '%Y-%m-%d %H:%M:%S')+" "+user_zone.time_zone.abbreviation

                        if da.get('invitatation_acceptance_date')!="":
                            invitatation_acceptance_date = convert_to_kolkata(da.get('invitatation_acceptance_date'),timez)
                            invitatation_acceptance_date=datetime.datetime.strftime(invitatation_acceptance_date, '%Y-%m-%d %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                        if date22:
                            print('---------------adteeeeeeee',date22)
                            date22 = convert_to_kolkata(datetime.datetime.strptime(str(date22), '%Y/%m/%d %H:%M:%S.%f'),timez)
                            date22=datetime.datetime.strftime(date22, '%Y-%m-%d %H:%M:%S')+" "+user_zone.time_zone.abbreviation
                        # invitatation_acceptance_date = convert_to_kolkata(datetime.datetime.strptime(da.get('invitatation_acceptance_date'), '%Y-%m-%d %H:%M:%S.%f'),timez)
                        # da.get('invitatation_acceptance_date')=temp_tz

                    if date22:
                        # date22 = convert_to_kolkata(date22,timez)
                        temppp22 = date22
                        act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'),da.get('member').get('email'), temppp2, da.get('member_added_by').get('first_name')+' '+da.get('member_added_by').get('last_name'),invitatation_acceptance_date, member_type,temppp22, status, )
                    else:
                        act = act + (da.get('member').get('first_name')+' '+da.get('member').get('last_name'),da.get('member').get('email'), temppp2, da.get('member_added_by').get('first_name')+' '+da.get('member_added_by').get('last_name'),invitatation_acceptance_date, member_type,' ', status, )

                    datas.append(act)
                header_data = [
                    'Member','Email Id','Invitation Send Date', 'Invitation By','Dataroom Joining Date', 'Member Type', 'Last View', 'User Status'
                    ]
                writer.writerow(header_data)
                writer.writerows(datas)
        # return response
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
        # return response
        print('---------------------------------------')
        from rest_framework import status
        return Response(status=status.HTTP_201_CREATED)






class DataroomGroupList(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user_id = []
        dataroom_group_list = DataroomGroups.objects.filter(dataroom_id=pk)
        # dataroom_user_list = DataroomMembers.objects.filter(dataroom_id=pk)
        # for dataroom_user in dataroom_user_list:
        #     user_id.append(dataroom_user.member.id)
        # user_list = User.objects.filter(id__in=user_id)
        serializer = DataroomGroupsSerializer(dataroom_group_list, many=True)
        # cat_serializer = CategoriesSerializer(cate_list, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddDataroomPrimaryContact(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        primary_list = request.data
        print(primary_list,'eeeeeeeeeeeeeeeeeeeeeeeevvvvvvvvvvvvvvvvvvvvv')
        for primary in primary_list:
            dataroom_mem = DataroomMembers.objects.filter(id=primary['id']).first() 
            if  dataroom_mem:
                if dataroom_mem.is_dataroom_admin==True:
                    dataroom_mem.is_primary_user = primary['is_primary_user']
                    dataroom_mem.is_q_a_user = primary['is_q_a_user']
                    dataroom_mem.save()
                else:
                    dataroom_mem.is_primary_user = primary['is_primary_user']
                    dataroom_group_permission = DataroomGroupPermission.objects.filter(dataroom_groups_id=dataroom_mem.end_user_group.first().id,dataroom_id=pk).last()
                    if  dataroom_group_permission:
                        if dataroom_group_permission.is_q_and_a==True:
                            dataroom_mem.is_q_a_user = primary['is_q_a_user']
                        else:
                            dataroom_mem.is_q_a_user = False
                    dataroom_mem.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetDataroonContact(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        dataroom_mem = DataroomMembers.objects.filter(dataroom_id=int(pk), is_dataroom_admin=True).first()
        serializer = DataroomMembersSerializer(dataroom_mem, many=False)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class DataroomEndUserSubmitter(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        dataroom_member = DataroomMembers.objects.get(id=request.data['member']['id'])
        grp_perm = DataroomGroupPermission.objects.filter(dataroom_groups_id=dataroom_member.end_user_group.first().id, dataroom_id=dataroom_member.dataroom.id).first()
        if dataroom_member.is_q_a_submitter_user:
            dataroom_member.is_q_a_submitter_user = False
            dataroom_member.save()
            return Response({'data': 'Q&A submitter removed successfully.'}, status=status.HTTP_201_CREATED)
        elif dataroom_member.is_q_a_submitter_user==False and grp_perm.is_q_and_a==True:
            dataroom_member.is_q_a_submitter_user = True
            dataroom_member.save()
            return Response({'data': 'Q&A submitter added successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'data': 'Check Q&A In Group permissions.'}, status=status.HTTP_400_BAD_REQUEST)


class UserByEmail(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        email = str(request.GET.get('email').lower())
        # print("Emaillll", email)
        user_obj = User.objects.filter(email=email).first()
        # print("Userssssssssss", user_obj)
        serializer = UserSerializer(user_obj, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AllGroups(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("pkkkkkkkkkkkk", pk)
        groups = DataroomGroups.objects.filter(dataroom_id = pk)
        serializer = DataroomGroupsSerializer(groups, many = True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class SearchAutoCompleteUser(APIView):
    """docstring for ClassName"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        key = request.GET.get('key')
        user = request.user
        from dataroom.models import Contacts
        # change by harish 28Feb 
        # contact = Contacts.objects.filter(user_id=user.id).values('email')
        all_dataroom_qs = [i.id for i in Dataroom.objects.filter()]
        dataroom_member_qs = [i.dataroom_id for i in DataroomMembers.objects.filter(member_id=user.id,dataroom_id__in=all_dataroom_qs,is_deleted=False)]
        all_member_qs = [i.member_id for i in DataroomMembers.objects.filter(dataroom_id__in=dataroom_member_qs,is_deleted=False)]
        # contact = Contacts.objects.all().values('email')
        # print(all_member_qs)
        dataa=[]
        contacts = Contacts.objects.filter(user_id=user.id)
        for i in contacts:
            dataa.append(i.email)

        # from itertools import chain
        contact2= User.objects.filter(id__in=all_member_qs)
        for i in contact2:
            dataa.append(i.email)
        # print(dataa)
        # contact=list(chain(contacts, contact2))
        # print(contact)
        q_list = [Q(first_name__icontains=key), Q(last_name__icontains=key), Q(email__icontains=key)]
        user = User.objects.filter(email__in=dataa).filter(reduce(operator.or_, q_list)).exclude(id=user.id)
        serializer = UserSerializer(user, many=True)
        # print(serializer.data,'8989888')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class GroupDeactivateactivate(APIView):
    """docstring for ClassName"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request,pk, format=None):
        data=DataroomGroups.objects.filter(id=pk).last()
        if data:
            if data.is_active==True:
                DataroomGroups.objects.filter(id=pk).update(is_active=False)
                drm_grp_perm = DataroomGroupPermission.objects.get(dataroom_groups_id=data.id)
                DataroomGroupPermission.objects.filter(dataroom_groups_id=data.id).update(
                is_watermarking_previous=drm_grp_perm.is_watermarking,
                is_doc_as_pdf_previous=drm_grp_perm.is_doc_as_pdf,
                is_excel_as_pdf_previous=drm_grp_perm.is_excel_as_pdf,
                is_drm_previous=drm_grp_perm.is_drm,
                is_edit_index_previous=drm_grp_perm.is_edit_index,
                is_overview_previous=drm_grp_perm.is_overview,
                is_q_and_a_previous=drm_grp_perm.is_q_and_a,
                is_users_and_permission_previous=drm_grp_perm.is_users_and_permission,
                is_updates_previous=drm_grp_perm.is_updates,
                is_reports_previous=drm_grp_perm.is_reports,
                is_voting_previous=drm_grp_perm.is_voting)
                DataroomGroupPermission.objects.filter(dataroom_groups_id=data.id).update(is_watermarking=False,
                is_doc_as_pdf=False,
                is_excel_as_pdf=False,
                is_drm=False,
                is_edit_index=False,
                is_overview=False,
                is_q_and_a=False,
                is_users_and_permission=False,
                is_updates=False,
                is_reports=False,
                is_voting=False)
                return Response(data=False, status=status.HTTP_201_CREATED)
            else:
                is_notify = request.GET.get("notify")
                DataroomGroups.objects.filter(id=pk).update(is_active=True)
                drm_grp_perm = DataroomGroupPermission.objects.get(dataroom_groups_id=data.id)
                DataroomGroupPermission.objects.filter(dataroom_groups_id=data.id).update(is_watermarking=drm_grp_perm.is_watermarking_previous,
                is_doc_as_pdf=drm_grp_perm.is_doc_as_pdf_previous,
                is_excel_as_pdf=drm_grp_perm.is_excel_as_pdf_previous,
                is_drm=drm_grp_perm.is_drm_previous,
                is_edit_index=drm_grp_perm.is_edit_index_previous,
                is_overview=drm_grp_perm.is_overview_previous,
                is_q_and_a=drm_grp_perm.is_q_and_a_previous,
                is_users_and_permission=drm_grp_perm.is_users_and_permission_previous,
                is_updates=drm_grp_perm.is_updates_previous,
                is_reports=drm_grp_perm.is_reports_previous,
                is_voting=drm_grp_perm.is_voting_previous)
                DataroomGroupPermission.objects.filter(dataroom_groups_id=data.id).update(
                is_watermarking_previous=False,
                is_doc_as_pdf_previous=False,
                is_excel_as_pdf_previous=False,
                is_drm_previous=False,
                is_edit_index_previous=False,
                is_overview_previous=False,
                is_q_and_a_previous=False,
                is_users_and_permission_previous=False,
                is_updates_previous=False,
                is_reports_previous=False,
                is_voting_previous=False)
                if is_notify == "Yes":
                    newuserdataa=DataroomMembers.objects.filter(end_user_group__in=[pk])
                    # print('-------------------new userrrrrr,',newuserdataa)
                    user=request.user
                    for i in newuserdataa:
                        userdataa=User.objects.get(id=i.member.id)
                        print('-----------------------USERRRRRR',userdataa.email)
                        emailer_utils.group_active_mail_send(userdataa, user, data.dataroom)

                return Response(data=True, status=status.HTTP_201_CREATED)
        else:
            return Response(data='Group not found', status=status.HTTP_400_BAD_REQUEST)




class Get_group_details(APIView):
    """docstring for ClassName"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request,pk, format=None):
        data=DataroomGroups.objects.filter(id=pk).values()
        return Response(data=data,status=status.HTTP_201_CREATED)



# New-Label -DisplayName $labelName `
                #           -Name $labelName `
                #           -Tooltip "This information is restricted to internal users only." `
                #           -EncryptionEnabled $true `
                #           -SiteAndGroupProtectionAllowFullAccess $true `
                #           -EncryptionRightsDefinitions $mail `
                #           -SiteAndGroupProtectionEnabled $true `
                #           -EncryptionContentExpiredOnDateInDaysOrNever "" 



                # New-LabelPolicy `
                #          -Name $labelName `
                #          -Labels $labelName `
                #          -ExchangeLocation "All" `
                #          -ModernGroupLocation "All"












class Irm_group_protection(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self,request,pk, format=None):
        days=''
        name=''
        is_active=False
        dgp=DataroomGroupPermission.objects.filter(dataroom_groups_id=pk).last()
        # irm_prot=Irm_group_protection_details.objects.filter(dataroom_groups_id=pk).last()
        if dgp:
            if dgp.is_irm_protected:
                if is_active:
                # if dgp.is_irm_active:
                    irm = Irm_group_protection_details.objects.filter(dataroom_groups_id=pk).last()
                    is_active=dgp.is_irm_active 
                    try:
                        days=irm.expiry_days
                        name=irm.label_name
                    except:
                        pass
                    return Response({'irm_perm':True,'is_active':True,'days':days,'name':name},status=status.HTTP_201_CREATED)
                else:
                    irm_prot=Irm_group_protection_details.objects.filter(dataroom_groups_id=pk).last()
                    try:
                        days=irm.expiry_days
                        name=irm.label_name
                    except:
                        pass
                    is_active=dgp.is_irm_active
                    url1 = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

                    payload1 = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_9QeQo0_rnfMxT9H7dzeVdp2rs2lyfFyXNjo-ZVllgwqdGs9B6pLBo9VuldMkCb64bTR_9ehyO30t0lZQHqTayS-9N88efQKxv0thfRYENOwIxhfb2pSHlXO9XXZkAcEPE2ptWZTiRux6Cywg757Tox0f2GQ96QKMR75Zb9KzwnvjuReI8hqkvaal-Ozy4-3kRvqWM3U26AvZnoZZoamHcT53zxhNKFzYxqR1V6KVxJXnlJPEZQM4p_1IuG0EsJrEE_n3Pnrj0r6BlJkdfslFj1axxhZ4LEO-d-0CYhnn994f5tp5k12i0i1uQm173VhK2K_yUOxP1jYMPnsREe52fn4hOV1EvfGH7VLmrdaAd6sAf6aOlrM7UmAJyZsDAr9PbxMBBUcISofnFD70jFjukyJCrP63WGac4kq1ZNTaE4dMaZw9jT2N7mhj3AQwIovcwEOesbOKHMabK7GufSoC9eIwHKl-qqM5Nbp8ATWwyVNgJcEf5m69OomxEEgAPPW1O1xeXSNMSsSholWfL9X3uQE5G73AIPR_jJTzuQtWER2gtWY0T0gxcIdG0UtLJcr-i4-b49YUOa_7MUHpwniQLf_Oh--8f-DACO7ob4ak_Z-5WxbsmZzDRhbgbepAM9Wjv9OjGIp772FQZFFQt_d_BwdgrXcjxCM2N4Lpi3j2rzFSnwVAsC1Sd5cExP0Q5JEEzWsS3qcv7mv5i9LDERZq0M7nEbD3cluUJTwZJOtUEHUKzA7rYl5lTk00BSo8ePqkBwDKzpFNHXCC6Uu9FKMEspDXXHqX_NOXm2UTQ-9XBpbel_8pRwDuz3IaGZAucUiGw4BsHkh8KElTViXjlCD8zYvgTLOrbyX-XY0sQ03HhhhHqM1sFBuWfhDHhN_71lzGiaJaXxN7npROpcu7EcCZsIHmDsQ5IvX_WDQjkZQm2zKdYHNuy5-88PTiPkP_xyTTnZ30IYtV1zutbD0kkFYMaMTraOGLMzuWVN1R5gh_R3RqcxA0H_fnPx_tLMr5DJTM0n_frr7f2FQUf0u1G6_TzLXlaPSxdGW4WeWfxXtYTzVtameKY1kPBsJ8vVE5PGMBg2AOaTtDRubfayQwRSxXrcc9irdeyvCM3anhrixgCMaSgFthGO9wtq6SLTCboWO1F9MAUw3nH6BB8CQu5s_NHS8rb4ROK6_4AkWnBB-4Ssu--cQ-Fn3NKcLIRnf7YO8_7xWQHu7k7eka9SgLtTmZgWdvnA6hvw1WvC4oD76NNY9ADRwR7MHyCNVb3bP0SGSbtlwsm7C873GABNTpq-xTkVF4_nwQKtp0lnylzi-CBb1NDc-GOFrbu4iiolxvi2nZmpJqlEzzMA6mQ8Elgxh3SLaPK2LCgf9irtEcQDiMVDh5Dc969ZH_508yG-9aTp6Yp2s-fggkaqKOQ'
                    headers1 = {
                      'Content-Type': 'application/x-www-form-urlencoded',
                        'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
                        }

                    response1 = requests.request("GET", url1, headers=headers1, data=payload1)
                    resp1=response1.json()
                    access_token=resp1['access_token']



                    url2 = "https://graph.microsoft.com/v1.0/me/informationProtection/sensitivityLabels"
                    headers2 = {
                      'Authorization': f'Bearer {access_token}',
                      'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url2, headers=headers2)
                    resp2=response2.json()

                    print('----------------22',irm_prot.label_name)
                    # print('----------------2233',resp2['value'])
                    for i in resp2['value']:
                        print('----------------',i['name'])
                        if i['name']==irm_prot.label_name:
                            dgp.is_irm_active=True
                            dgp.save()

                            irm_prot.label_id=i['id']
                            irm_prot.save()

                            return Response({'irm_perm':True,'is_active':True,'days':days,'name':name},status=status.HTTP_201_CREATED)
                        
                    return Response({'irm_perm':True,'is_active':is_active,'days':days,'name':name},status=status.HTTP_201_CREATED)



            else:
                return Response({'irm_perm':False,'is_active':False,'days':days,'name':name}, status=status.HTTP_201_CREATED)
        else:
            return Response({'irm_perm':False,'is_active':False,'days':days,'name':name},status=status.HTTP_201_CREATED)

        return Response({'irm_perm':False,'is_active':False,'days':days,'name':name},status=status.HTTP_201_CREATED)


    def delete(self,request,pk, format=None):
        DataroomGroupPermission.objects.filter(dataroom_groups_id=pk).update(is_irm_protected=False)
        return Response({'msg':done}, status=status.HTTP_201_CREATED)


    def post(self,request,pk, format=None):

        import random
        random_integer = random.randint(1, 100000)
        data=request.data
        print('-=----------------dataaaa',data)
        if data['is_active']==False or data['is_active']=='False':
            DataroomGroupPermission.objects.filter(dataroom_groups=pk).update(is_irm_protected=False)
            return Response({'msg':'False'})
        # print('--------------------',uii)
        if not Irm_group_protection_details.objects.filter(dataroom_groups_id=pk).exists():

            expiry_days=data['days']
            group=DataroomGroups.objects.get(id=pk)
            
            group_name=group.group_name+str(random_integer)
            label_name=group.dataroom.dataroom_name

            label_name='IRM Protected'+label_name+group_name
            print('-------------group_name',group_name)
            print('-------------label_name',label_name)

            import requests
            import json


            url1 = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

            payload1 = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_9QeQo0_rnfMxT9H7dzeVdp2rs2lyfFyXNjo-ZVllgwqdGs9B6pLBo9VuldMkCb64bTR_9ehyO30t0lZQHqTayS-9N88efQKxv0thfRYENOwIxhfb2pSHlXO9XXZkAcEPE2ptWZTiRux6Cywg757Tox0f2GQ96QKMR75Zb9KzwnvjuReI8hqkvaal-Ozy4-3kRvqWM3U26AvZnoZZoamHcT53zxhNKFzYxqR1V6KVxJXnlJPEZQM4p_1IuG0EsJrEE_n3Pnrj0r6BlJkdfslFj1axxhZ4LEO-d-0CYhnn994f5tp5k12i0i1uQm173VhK2K_yUOxP1jYMPnsREe52fn4hOV1EvfGH7VLmrdaAd6sAf6aOlrM7UmAJyZsDAr9PbxMBBUcISofnFD70jFjukyJCrP63WGac4kq1ZNTaE4dMaZw9jT2N7mhj3AQwIovcwEOesbOKHMabK7GufSoC9eIwHKl-qqM5Nbp8ATWwyVNgJcEf5m69OomxEEgAPPW1O1xeXSNMSsSholWfL9X3uQE5G73AIPR_jJTzuQtWER2gtWY0T0gxcIdG0UtLJcr-i4-b49YUOa_7MUHpwniQLf_Oh--8f-DACO7ob4ak_Z-5WxbsmZzDRhbgbepAM9Wjv9OjGIp772FQZFFQt_d_BwdgrXcjxCM2N4Lpi3j2rzFSnwVAsC1Sd5cExP0Q5JEEzWsS3qcv7mv5i9LDERZq0M7nEbD3cluUJTwZJOtUEHUKzA7rYl5lTk00BSo8ePqkBwDKzpFNHXCC6Uu9FKMEspDXXHqX_NOXm2UTQ-9XBpbel_8pRwDuz3IaGZAucUiGw4BsHkh8KElTViXjlCD8zYvgTLOrbyX-XY0sQ03HhhhHqM1sFBuWfhDHhN_71lzGiaJaXxN7npROpcu7EcCZsIHmDsQ5IvX_WDQjkZQm2zKdYHNuy5-88PTiPkP_xyTTnZ30IYtV1zutbD0kkFYMaMTraOGLMzuWVN1R5gh_R3RqcxA0H_fnPx_tLMr5DJTM0n_frr7f2FQUf0u1G6_TzLXlaPSxdGW4WeWfxXtYTzVtameKY1kPBsJ8vVE5PGMBg2AOaTtDRubfayQwRSxXrcc9irdeyvCM3anhrixgCMaSgFthGO9wtq6SLTCboWO1F9MAUw3nH6BB8CQu5s_NHS8rb4ROK6_4AkWnBB-4Ssu--cQ-Fn3NKcLIRnf7YO8_7xWQHu7k7eka9SgLtTmZgWdvnA6hvw1WvC4oD76NNY9ADRwR7MHyCNVb3bP0SGSbtlwsm7C873GABNTpq-xTkVF4_nwQKtp0lnylzi-CBb1NDc-GOFrbu4iiolxvi2nZmpJqlEzzMA6mQ8Elgxh3SLaPK2LCgf9irtEcQDiMVDh5Dc969ZH_508yG-9aTp6Yp2s-fggkaqKOQ'
            headers1 = {
              'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
                }

            response1 = requests.request("GET", url1, headers=headers1, data=payload1)
            resp1=response1.json()
            access_token=resp1['access_token']

            print('-----------------access toeknn',access_token)

            url = "https://graph.microsoft.com/v1.0/groups"
            group_nickname = group_name.replace(" ", "_")
            print('------------------gropip nicl name ',group_nickname)
            payload = json.dumps({
              "description": "IRM-protected group for sensitivity labels",
              "displayName": group_name,
              "groupTypes": [
                "Unified"
              ],
              "mailEnabled": True,
              "mailNickname": group_nickname,
              "securityEnabled": True
            })
            headers = {
              'Authorization': f'Bearer {access_token}',
              'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            resp=response.json()
            print('--------------group response',resp)
            mail=resp['mail']
            group_id=resp['id']


            member=DataroomMembers.objects.filter(dataroom_id=group.dataroom.id, is_end_user=True, is_deleted_end=False, end_user_group__in=[group])
            for i in member:

                url3 = "https://graph.microsoft.com/v1.0/invitations"


                payload3 = json.dumps({
                  "invitedUserEmailAddress": i.member.email,
                  "inviteRedirectUrl": "https://myapps.microsoft.com",
                  "sendInvitationMessage": False
                })
                # headers = {
                #   'Authorization': f'Bearer {access_token}',
                #   'Content-Type': 'application/json'
                # }

                response3 = requests.request("POST", url3, headers=headers, data=payload3)

                resp3=response3.json()

                print('--------------invite response',resp3)
                invite_id=resp3['invitedUser']['id']




                url4 = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"

                payload4 = json.dumps({
                  "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{invite_id}"
                })
                

                response4 = requests.request("POST", url4, headers=headers, data=payload4)


                print('--------------group invite response',response4)






            ps_script = f"""
            try {{
                # Connect to Microsoft 365 Security & Compliance

                Import-Module ExchangeOnlineManagement

                #$appId = "bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09"
                #$thumbprint = "B51A6B1919B67F03E0B31BF6874196D4673A0C47"
                #$organization = "docullyvdr.com"
                
                #Connect-IPPSSession -CertificateThumbprint $thumbprint -AppId $appId -Organization $organization
                #Connect-IPPSSession -CertificateFilePath "/home/cdms_backend/docully_cert.pfx" -CertificatePassword (ConvertTo-SecureString -String "docully" -AsPlainText -Force) -AppId "bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09" -Organization "docullyvdr.com"

                $User = "drm@docullyvdr.com"
                $PWord = ConvertTo-SecureString "121@Axatvdr" -AsPlainText -Force

                $Credential = New-Object System.Management.Automation.PSCredential ($User, $PWord)
                Connect-IPPSSession -Credential $Credential



                $mail = "{mail}:VIEW"


                # Create new sensitivity label
                $labelName = "{label_name}"
                $policy_name= "{label_name}policy"


                #Write-Host "Creating label: $labelName"

                


                New-Label -DisplayName $labelName `
                       -Name $labelName `
                       -Tooltip $labelName `
                       -EncryptionEnabled $true `
                       -EncryptionRightsDefinitions $mail `
                       -EncryptionOfflineAccessDays 0 `
                       -EncryptionContentExpiredOnDateInDaysOrNever "{expiry_days}" 


                New-LabelPolicy -Name $policy_name `
                     -Labels $labelName `
                     -ExchangeLocation "All" `
                     -ModernGroupLocation "All" `
                     -AdvancedSettings @{{ "EnableInSharePoint"="True"; "EnableInOneDrive"="True" }}




            }}
            catch {{
                Write-Error "Error: $($_.Exception.Message)"
            }}
            """


            # # process = subprocess.run(
            # #     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            # #     capture_output=True,
            # #     text=True
            # # )
            # process = subprocess.run(
            #     ["pwsh", "-Command", ps_script],
            #     capture_output=True,
            #     text=True
            # )

            # # -------------------------------
            # # 3. Print Outputs
            # # -------------------------------
            # print("=== STDOUT ===")
            # print(process.stdout)
            # print("=== STDERR ===")
            # print(process.stderr)

            import subprocess
    #         ps_commands = """
    #         pwsh -Command "Import-Module ExchangeOnlineManagement"

    #         """

    # # Run Bash, which runs pwsh inside it
    #         result = subprocess.run(["bash", "-c", ps_commands])
            # ps_script = """
            # Import-Module ExchangeOnlineManagement

            # """

            result = subprocess.run(
                ["pwsh", "-Command", ps_script],
            capture_output=True,
            universal_newlines=True,
            encoding="utf-8"
            )

            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            DataroomGroupPermission.objects.filter(dataroom_groups=group).update(is_irm_protected=True)
            Irm_group_protection_details.objects.create(dataroom_groups_id=pk,label_name=label_name,group_id=group_id,group_name=group_name,expiry_days=expiry_days)

            return Response({"data":"done"},status=status.HTTP_201_CREATED)
        DataroomGroupPermission.objects.filter(dataroom_groups=pk).update(is_irm_protected=True)
        return Response({'data':'already exits'},status=status.HTTP_201_CREATED)














