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
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FileUploadParser
from django.core.mail import send_mail
from random import randint
from userauth.serializers import UserSerializer, AccessHistorySerializer, InviteUserSerializer
from userauth import constants, utils
from userauth.models import Profile, AccessHistory, User, InvitationStatus, InviteUser
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

from .models import DataroomGroups, DataroomGroupPermission, DataroomGroupFolderSpecificPermissions, DataroomMembers
from .serializers import DataroomGroupsSerializer, DataroomGroupPermissionSerializer, DataroomGroupFolderSpecificPermissionsSerializer
from data_documents.models import DataroomFolder
from notifications.models import AllNotifications


class ChangeDisclaimerStatus(APIView):
    serializers = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
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
        print("____________________________________________")
        print(user.id)
        dataroom_primary_user = DataroomMembers.objects.filter(dataroom_id=pk,is_deleted=False,is_primary_user=True)
        serializer = DataroomMembersSerializer(dataroom_primary_user, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)


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
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        dataroom_group_id = request.data['dataroom_group_id']
        print("dataroom", dataroom_group_id)        
        dataroom = Dataroom.objects.filter(id=int(dataroom_group_id)).first()
        count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.my_team.id, is_deleted=False).count()
        print("dataroom",dataroom.my_team.dataroom_admin_allowed, count)
        if dataroom.my_team.dataroom_admin_allowed > count:
            if dataroom_group_id:
                dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group_id, is_dataroom_admin=True).first()
                # print("dataroom-Meme", dataroom_mem)
                if dataroom_mem == None:
                    return Response({"result": True, 'msg':'Added successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"result": False, 'msg':'This is user already exist in this dataroom!'}, status=status.HTTP_400_BAD_REQUEST)                
        else:
            return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": False, 'msg':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class CheckAdmin(APIView):
    serializers = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        print("Request Data", request.data)
        dataroom_group_id = request.data['dataroom_group_id']        
        dataroom = DataroomGroups.objects.filter(id=int(dataroom_group_id)).first()
        count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.dataroom.my_team.id, is_deleted=False).count()
        print("dataroom",dataroom.dataroom.my_team.dataroom_admin_allowed, count)
        if dataroom.dataroom.my_team.dataroom_admin_allowed > count:
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
                    print("Dataroom Member", dataroom_mem, dataroom_la_check)
                    if not dataroom_mem and not dataroom_la_check:
                        return Response({"result": True}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"result": False,'msg':'This user already exist in this group!!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)
                


class CheckLaUser(APIView):
    serializers = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        print("Request Data", request.data)
        dataroom_group_id = request.data['dataroom_group_id']        
        dataroom = DataroomGroups.objects.filter(id=int(dataroom_group_id)).first()
        count = DataroomMembers.objects.filter(dataroom__my_team_id=dataroom.dataroom.my_team.id, is_deleted=False).count()
        print("dataroom",dataroom.dataroom.my_team.dataroom_admin_allowed, count)
        if dataroom.dataroom.my_team.dataroom_admin_allowed > count:
            if dataroom_group_id:
                dataroom_group = DataroomGroups.objects.filter(id=dataroom_group_id)           
                dataroom_mem = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_dataroom_admin=True)
                print("dataroom_mem.", dataroom_mem)
                try:
                    if request.data['is_end_user']:
                        dataroom_la_check = DataroomMembers.objects.filter(member__email=request.data['email'].lower(), dataroom_id=dataroom_group.first().dataroom_id, is_deleted=False)
                        print("dataroooom", dataroom_la_check)
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
        else:
            return Response({"result": False, 'msg':'Your Team members allowed limit exceeded!! Contact Support!!'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteDataroomAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom_member = DataroomMembers.objects.get(id=pk)
        dataroom_member.is_deleted = True
        dataroom_member.is_dataroom_admin = False
        dataroom_member.save()
        #changes added by harish 
        InviteUser.objects.filter(invitiation_sender=user.id,invitiation_receiver=pk).update(is_invitation_accepted=False)

        return Response({'data': 'Admin successfully deleted !'}, status=status.HTTP_201_CREATED)


class DeleteTypeDataroomAdmins(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        dataroom_member = DataroomMembers.objects.get(id=pk)
        # dataroom_member.request.data['delete_type'] = True
        if request.data['is_deleted'] == 'is_deleted_la':
            dataroom_member.is_deleted_la = True
            dataroom_member.end_user_group.remove(request.data['group_id'])
            # dataroom_member.is_la_user = False
            dataroom_member.save()
        if request.data['is_deleted'] == 'is_deleted_end':
            dataroom_member.is_deleted_end = True
            dataroom_member.is_end_user = False
            dataroom_member.end_user_group.remove(request.data['group_id'])
        dataroom_member.is_deleted = True
        dataroom_member.save()
        return Response({'data': 'Admin successfully deleted !'}, status=status.HTTP_201_CREATED)


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
                return Response({'data': 'Admin successfully deleted !'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'data': 'Already admin deleted'})


class CreateDataroomAdmin(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        
        dataroom = Dataroom.objects.get(id=pk)
        serializer_data = UserSerializer(dataroom.user, many=False).data
        dataroom_members = DataroomMembers.objects.filter(dataroom_id=pk, is_dataroom_admin=True, is_deleted= False)#.exclude(dataroom_id=dataroom.id, member=dataroom.user)
        dataroom_members_serializer = DataroomMembersSerializer(dataroom_members, many=True)
        data =  dataroom_members_serializer.data
        # for da in data:
        #     try:
        #         invite_user = InviteUser.objects.get(invitiation_receiver_id=da['member']['id'],invitiation_sender_id=da['member_added_by']['id'],dataroom_invitation=da['dataroom']['id'])
        #         invitation_serializer = InviteUserSerializer(invite_user)     
        #         da['invitation'] = invitation_serializer.data
        #     except:
        #         da['invitation'] = ""
        return Response(data)

    def post(self, request, pk, format=None):
        user = request.user
        all_new_data = request.data['admin']
        for data in all_new_data:
            if user.email != data.get('email').lower():
                is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                dataroom_data = Dataroom.objects.get(id=pk)
                dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                #step1
                """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                if is_user == False:
                    data['password'] = "Password1#"
                    data['is_admin'] = False
                    data['is_active'] = True
                    data['is_end_user'] = True
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
                            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, user, dataroom_data)
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
                                dataroom_mem_obj.save()
                            else:
                                dataroom_mem_obj.is_dataroom_admin = True
                                try:
                                    dataroom_mem_obj.member_type = 1
                                except:
                                    pass
                                dataroom_mem_obj.save()
                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                                # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    old_user = User.objects.get(email__iexact=data.get("email").lower())
                    old_user.is_admin = True
                    old_user.save()
                    unique_id = get_random_string(length=400)
                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                    new_data = {
                        'invitiation_sender':user.id, 
                        'invitiation_receiver':old_user.id, 
                        'invitation_status':3, 
                        'is_invitation_expired':False, 
                        'invitation_link':link, 
                        'invitation_token':unique_id 
                    }
                    invite_user_serializer = InviteUserSerializer(data=new_data)     
                    if invite_user_serializer.is_valid():
                        invite_user_serializer.save()
                        # if dr_overview.send_daily_email_updates:
                        emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data)
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
                            dataroom_mem_obj.save()
                            for mem in request.data['admin']:    
                                for d_m in dataroom_mem_obj.end_user_group.all():
                                    if d_m.limited_access or d_m.end_user:
                                        dataroom_mem_obj.end_user_group.remove(d_m.id)
                        else:
                            dataroom_mem_obj.is_dataroom_admin = True
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
                return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)


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
        if dataroom_group_serializer.is_valid():
            dataroom_group_serializer.save()
            print("datagroup id "+str(dataroom_group_serializer.data['id']))
            print("dataroom id "+str(dataroom_group_serializer.data['dataroom']['id']))
            # change by harish working fine ,issue is fix 
            dataroom_id =dataroom_group_serializer.data['dataroom']['id']
            dataroom_groupid =dataroom_group_serializer.data['id']
            da_g_p = DataroomGroupPermission.objects.filter(Q(dataroom_id=dataroom_id) & Q(dataroom_groups=dataroom_groupid)).exists()
            print(da_g_p)
            if da_g_p == False:
                print("TRue")
                DataroomGroupPermission.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
                # DataroomGroupPermission.objects.create(dataroom_id=dataroom_id,dataroom_groups_id=dataroom_groupid,is_watermarking=False,is_doc_as_pdf=False,is_excel_as_pdf=False,is_drm=False,is_edit_index=False,is_overview=False,is_q_and_a=False,is_users_and_permission=False,is_updates=False,is_report=False,is_voting=False)
               
                AllNotifications.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'], user_id=dataroom_group_serializer.data['group_created_by']['id'])
            return Response(dataroom_group_serializer.data, status=status.HTTP_201_CREATED)


class AddDataroomLaUserGroup(APIView):
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
        all_member = request.data['member']
        print (111111111111)
        for data in all_member:
            if user.email != data.get('email').lower():
                print (2222222222)
                is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                dataroom_data = Dataroom.objects.get(id=pk)
                dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                #step1
                """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                if is_user == False:
                    print (333333333333)
                    data['password'] = "Password1#"
                    data['is_admin'] = False
                    data['is_active'] = True
                    data['is_end_user'] = True
                    serializer = UserSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        print (4444444444)
                        # If user is saved then make the entry inside InviteUser page
                        
                        # step : 2 -> Make the entry of User inside the DataroomRoles
                        dataroom_roles_data = {'user':serializer.data.get("id"), 'dataroom':pk, 'roles':2}
                        dataroom_roles_serializer = DataroomRolesSerializer(data=dataroom_roles_data)
                        if dataroom_roles_serializer.is_valid():
                            dataroom_roles_serializer.save()

                        # make the entry of user inside the data
                        unique_id = get_random_string(length=400)
                        link = constants.link+"invitation_link_admin    /"+unique_id+"/?user_exist="+str(False)
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
                            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, user, dataroom_data)
                            # add the entry of member inside datarooom members table
                            # dataroom_member_data = {'dataroom':int(pk),'member' : User.objects.get(id=serializer.data.get('id')), 'member_type_id':1, 'member_added_by':user, 'is_dataroom_admin': True}
                            # dataroom_member_serializer = DataroomMembersSerializer(data= dataroom_member_data, context={'member_data': dataroom_member_data})
                            # if dataroom_member_serializer.is_valid():
                            #     dataroom_member_serializer.save()
                                # all dataroom members
                            dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=serializer.data.get("id"), member_added_by_id=user.id)
                            if not created:
                                print (66666666666)
                                dataroom_mem_obj.dataroom_id = serializer.data.get('id')
                                dataroom_mem_obj.member_id = dataroom_admin.id
                                dataroom_mem_obj.member_type = 1
                                dataroom_mem_obj.member_added_by_id = user.id
                                dataroom_mem_obj.is_la_user = True
                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                dataroom_mem_obj.save()
                                dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            else:
                                print (77777777777777)
                                dataroom_mem_obj.is_la_user = True
                                # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                try:
                                    dataroom_mem_obj.member_type = 1
                                except:
                                    pass
                                dataroom_mem_obj.save()
                                dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
                                # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print (8888888888888)
                    old_user = User.objects.get(email__iexact=data.get("email").lower())
                    old_user.is_end_user = True
                    old_user.save()
                    unique_id = get_random_string(length=400)
                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                    new_data = {
                        'invitiation_sender':user.id, 
                        'invitiation_receiver':old_user.id, 
                        'invitation_status':3, 
                        'is_invitation_expired':False, 
                        'invitation_link':link, 
                        'invitation_token':unique_id 
                    }
                    invite_user_serializer = InviteUserSerializer(data=new_data)     
                    if invite_user_serializer.is_valid():
                        print (9999999999999999)
                        invite_user_serializer.save()
                        # if dr_overview.send_daily_email_updates:
                        emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data)
                        dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':True}
                        dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)

                        if not created:
                            print (10101010101010)
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
                            dataroom_mem_obj.save()
                            # dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            for each in dataroom_mem_obj.end_user_group.all():
                                if each.limited_access:
                                    # dataroom_mem_obj.end_user_group.remove(each.id)
                                    dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            for mem in request.data['member']:
                                if mem['is_la_user']:
                                    for d_m in dataroom_mem_obj.end_user_group.all():
                                        if d_m.end_user:
                                            dataroom_mem_obj.end_user_group.remove(d_m.id)
                                            pass
                            dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                        else:
                            print (12121212121212)
                            dataroom_mem_obj.is_la_user = True
                            try:
                                dataroom_mem_obj.member_type = 1
                            except:
                                pass
                            # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                            dataroom_mem_obj.is_deleted =   False
                            dataroom_mem_obj.is_deleted_la = False
                            dataroom_mem_obj.save()
                            dataroom_mem_obj.end_user_group.add(request.data['group_id'])
            else:
                # print (13131313131313)
                return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            # print (14141414141414)
            dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
            dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
            return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
        except:
            # print (151515151515)
            return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)
         
        
# End rajendra code here


class CreateDataroomEndUserGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        data = request.data
        user = request.user
        dataroom_groups = DataroomGroups.objects.filter(dataroom_id=pk, is_deleted=False)
        dataroom_group_serializer = DataroomGroupsSerializer(dataroom_groups, many=True)
        data = dataroom_group_serializer.data
        for da in data:
            count = 0
            dataroom_members_list = DataroomMembers.objects.filter(dataroom_id = pk,is_deleted=False, is_deleted_end=False, is_deleted_la=False)
            for mem in dataroom_members_list:
                for each in mem.end_user_group.all():
                    if each.id == da['id']:
                        count += 1
            da['members_length'] = count
            count = 0
        return Response(data)

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
            print(da_g_p)
            if da_g_p == False:
                print("TRue333")
                DataroomGroupPermission.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'])
                # DataroomGroupPermission.objects.create(dataroom_id=dataroom_id,dataroom_groups_id=dataroom_groupid,is_watermarking=False,is_doc_as_pdf=False,is_excel_as_pdf=False,is_drm=False,is_edit_index=False,is_overview=False,is_q_and_a=False,is_users_and_permission=False,is_updates=False,is_report=False,is_voting=False)
               
                AllNotifications.objects.create(dataroom_groups_id=dataroom_group_serializer.data['id'], dataroom_id=dataroom_group_serializer.data['dataroom']['id'], user_id=dataroom_group_serializer.data['group_created_by']['id'])

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
        snippet.delete()
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
        dataroom_group_permission = DataroomGroupPermission.objects.get(dataroom_groups_id=pk)
        serializer = DataroomGroupPermissionSerializer(dataroom_group_permission, data=request.data.get('data'))
        if serializer.is_valid():
            serializer.save()
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
        emailer_utils.send_dataroom_admin_email_if_user_exist(member, data.get("invitation"), sender, dataroom)
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
        all_member = request.data['member']
        for data in all_member:
            if user.email != data.get('email').lower():
                is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
                dataroom_data = Dataroom.objects.get(id=pk)
                dr_overview = DataroomOverview.objects.filter(dataroom=dataroom_data).first()
                #step1
                """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
                if is_user == False:
                    data['password'] = "Password1#"
                    data['is_admin'] = False
                    data['is_active'] = False
                    data['is_end_user'] = True
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
                            # add the entry of member inside datarooom members table
                            # dataroom_member_data = {'dataroom':int(pk),'member' : User.objects.get(id=serializer.data.get('id')), 'member_type_id':1, 'member_added_by':user, 'is_dataroom_admin': True}
                            # dataroom_member_serializer = DataroomMembersSerializer(data= dataroom_member_data, context={'member_data': dataroom_member_data})
                            # if dataroom_member_serializer.is_valid():
                            #     dataroom_member_serializer.save()
                            dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=serializer.data.get("id"), member_added_by_id=user.id)
                            emailer_utils.send_dataroom_admin_email_if_user_is_not_exist(serializer.data, new_data, user, dataroom_data)
                            if not created:
                                dataroom_mem_obj.dataroom_id = serializer.data.get('id')
                                dataroom_mem_obj.member_id = dataroom_admin.id
                                dataroom_mem_obj.member_type = 1
                                dataroom_mem_obj.member_added_by_id = user.id
                                dataroom_mem_obj.is_end_user = True
                                dataroom_mem_obj.is_la_user = False
                                dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                dataroom_mem_obj.save()
                                for each in dataroom_mem_obj.end_user_group.all():
                                    if each.end_user:
                                        # dataroom_mem_obj.end_user_group.remove(each.id)
                                        dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                                for mem in request.data['member']:
                                    if mem['is_end_user']:
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.end_user:
                                                # dataroom_mem_obj.end_user_group.remove(d_m.id)
                                                pass
                                dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            else:
                                dataroom_mem_obj.is_end_user = True
                                try:
                                    dataroom_mem_obj.member_type = 1
                                except:
                                    pass
                                dataroom_mem_obj.end_user_group_id = request.data['group_id']
                                dataroom_mem_obj.save()
                                for mem in request.data['member']:
                                    if mem['is_end_user']:
                                        for d_m in dataroom_mem_obj.end_user_group.all():
                                            if d_m.end_user:
                                                pass
                                dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                                dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
                                dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=False)
                                # return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    usr = User.objects.filter(email__iexact=data.get("email").lower()).first()
                    usr.is_end_user = True
                    usr.save()
                    old_user = User.objects.get(email__iexact=data.get("email").lower())
                    unique_id = get_random_string(length=400)
                    link = constants.link+"invitation_link_admin/"+unique_id+"/?user_exist="+str(True)
                    new_data = {
                        'invitiation_sender':user.id, 
                        'invitiation_receiver':old_user.id, 
                        'invitation_status':3, 
                        'is_invitation_expired':False, 
                        'invitation_link':link, 
                        'invitation_token':unique_id 
                    }
                    invite_user_serializer = InviteUserSerializer(data=new_data)     
                    if invite_user_serializer.is_valid():
                        invite_user_serializer.save()
                        # if dr_overview.send_daily_email_updates:
                        
                        dataroom_member__newdata = {'dataroom':pk,'member' :old_user.id, 'member_type':1, 'member_added_by':user.id, 'is_la_user':False}
                        # print("dataroom_member__newdata",dataroom_member__newdata)
                        dataroom_mem_obj, created = DataroomMembers.objects.get_or_create(dataroom_id=pk, member_id=old_user.id, member_added_by_id=user.id)
                        emailer_utils.send_dataroom_admin_email_if_user_exist(old_user, invite_user_serializer.data, user, dataroom_data)
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
                            dataroom_mem_obj.is_deleted_end = False                          
                            dataroom_mem_obj.save()
                            for each in dataroom_mem_obj.end_user_group.all():
                                if each.end_user:
                                    # dataroom_mem_obj.end_user_group.remove(each.id)
                                    dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            # for mem in request.data['member']:
                            #     if mem['is_end_user']:
                            #         for d_m in dataroom_mem_obj.end_user_group.all():
                            #             if d_m.end_user:
                            #                 # dataroom_mem_obj.end_user_group.remove(d_m.id)
                            #                 pass
                            dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                        else:
                            # dataroom_mem_obj.end_user_group_id = request.data['group_id']
                            dataroom_mem_obj.is_end_user = True
                            dataroom_mem_obj.member_added_by_id = user.id
                            try:
                                dataroom_mem_obj.member_type = 1
                            except:
                                pass
                            dataroom_mem_obj.is_deleted =   False                                
                            dataroom_mem_obj.save()
                            dataroom_mem_obj.save()
                            dataroom_mem_obj.end_user_group.add(request.data['group_id'])
                            # for each in dataroom_mem_obj.end_user_group.all():
                            #     if each.end_user:
                            #         dataroom_mem_obj.end_user_group.add(request.data['group_id'])
            else:
                return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            dataroom_mem = DataroomMembers.objects.filter(dataroom_id=pk)
            dataroom_mem_serializer = DataroomMembersSerializer(dataroom_mem, many=True)
            return Response(dataroom_mem_serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({'msg': 'User already exist !'}, status=status.HTTP_400_BAD_REQUEST)
           
class GetMembersPermission(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
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
                        group_permission = DataroomGroupPermission.objects.get(dataroom_groups_id=each.id)
                        data = utils.set_permission(group_permission, data)
                else:
                    data = {'is_overview':True,'is_q_and_a':True, 'is_reports':True, 'is_updates':True, 'is_users_and_permission':True, 'is_watermarking':True, 'is_drm':True,'is_edit_index':True, 'is_voting':True}
                    break;
        else:
            data = {'is_overview':True,'is_q_and_a':True, 'is_reports':True, 'is_updates':True, 'is_users_and_permission':True, 'is_watermarking':True, 'is_drm':True,'is_edit_index':True, 'is_voting':True}
        return Response(data)

class CreateDataroomGroupFolderPermissions(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


    def get_children(self, pk, parent_id, group_id, user, perm):

        data = []

        document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=False, parent_folder=parent_id, is_deleted=False).order_by('index')
        for doc in document:
            docu = DataroomFolder.objects.get(id = doc.id)
            docu_serializer = DataroomFolderSerializer(docu)
            datas = docu_serializer.data
            # utils.getIndexofFolder(datas)
            datas['perm'] = {}
            docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
            if datas['is_folder']:
                datas['hasChildren'] = True
                datas['perm'] = perm
                datas['children'] = self.get_children(pk, datas.get('id'), group_id, user, perm)
            else:
                datas['perm'] = perm
                if perm['is_upload']:
                    datas['perm']['is_upload'] = False

                datas['hasChildren'] = False

            data.append(datas)
        return data

    def update_children(self, data, pk, group_id, user):
        for da in data:

            if 'view_indeterminate' in da:
                if da['view_indeterminate'] == True:
                    da['perm']['is_view_only']
            folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id).first()
            if not folder_permission:
                serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
                if serializer.is_valid():
                    serializer.save()
            else:
                serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                if serializer.is_valid():
                    serializer.save()

            folder_obj = DataroomFolder.objects.get(id=da['id'])
            flag = True
            while flag:
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=group_id)
                if perm_obj.is_no_access == False:
                    perm_obj.is_access = True
                    perm_obj.save()
                    if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
                        flag = False
                    else:
                        folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
                        perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=group_id)
                        if perm_obj.is_no_access == False:
                            perm1_obj.is_access = True
                            perm1_obj.is_no_access = False
                        else:
                            perm1_obj.is_access = False
                        perm1_obj.save()
                        folder_obj = folder1_obj
                        flag = False
                else:
                    flag = False

            if not 'children' in da and da['hasChildren']==True:
                da['children'] = []
                da['children'] = self.get_children(pk, da['id'], group_id, user, da['perm'])

            if 'children' in da:
                if len(da['children']) > 0:
                    self.update_children(da['children'],pk, group_id, user)
        return True
    
    def post(self, request, pk, format=None):
        test = []
        user = request.user
        data = request.data
        files = data['file']
        for da in files:
            if da['view_indeterminate'] == True:
                da['perm']['is_view_only']
            folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id']).first()
            if not folder_permission:
                serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': request.data['group_id']})
                if serializer.is_valid():
                    serializer.save()
            else:
                serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
                if serializer.is_valid():
                    serializer.save()

            folder_obj = DataroomFolder.objects.get(id=da['id'])
            flag = True
            while flag:
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=da['id'],dataroom_id=pk,dataroom_groups_id=data['group_id'])
                if perm_obj.is_no_access == False:
                    perm_obj.is_access = True
                    perm_obj.save()
                    if folder_obj.parent_folder_id == None or folder_obj.is_root_folder == True:
                        flag = False
                    else:
                        folder1_obj = DataroomFolder.objects.get(id = folder_obj.parent_folder_id)
                        perm1_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folder1_obj.id,dataroom_id=pk,dataroom_groups_id=data['group_id'])
                        if perm_obj.is_no_access == False:
                            perm1_obj.is_access = True
                            perm1_obj.is_no_access = False
                        else:
                            perm1_obj.is_access = False
                        perm1_obj.save()
                        folder_obj = folder1_obj
                        flag = False
                else:
                    flag = False

            if not 'children' in da and da['hasChildren']==True:
                da['children'] = []
                da['children'] = self.get_children(pk, da['id'], data['group_id'], user, da['perm'])
                    
            if 'children' in da:
                if len(da['children']) > 0:

                    self.update_children(da['children'],pk, data['group_id'], user)
        return Response(status=status.HTTP_204_NO_CONTENT)


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

        if removed == 'false':
            removed = False
        else:
            removed = True
        print('group----', group_id)
        if group_id == 0 :
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)
        elif group_id == -1:
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)
        else:
            member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)       
        serializer = DataroomMembersSerializer(member, many=True)
        data = serializer.data
        for da in data:
            memb = DataroomMembers.objects.get(id=da['id'])
            try:
                group = DataroomGroups.objects.get(id=memb.end_user_group.all().first().id)
                da['group'] = group.group_name
            except:
                da['group'] = "Admin"
        datas= {}
        datas['users'] = data
        if removed == False and (group_id == 0 or group_id == -1):
            da = {}
            serializer = UserSerializer(dataroom.user, many=False)
            serializer_data = serializer.data
            da['member'] = serializer_data
            da['member_added_by'] = serializer_data
            da['group'] = "Admin"
            da['date_joined'] = user.date_joined.strftime('%d/%m/%Y %H:%M:%S')
            datas['users'].append(da)
        return Response(datas, status=status.HTTP_201_CREATED)

class GetLastDataroomView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, user, format=None):

        workspace_view = DataroomView.objects.filter(dataroom_id=pk, user_id=user).order_by('id').reverse().first()
        folder_workspace_data = DataroomViewSerializer(workspace_view, many=False).data
        print(folder_workspace_data)
        return Response(folder_workspace_data, status=status.HTTP_201_CREATED)
        



class ExportUsersGroups(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom = Dataroom.objects.get(id=pk)
        group_id = int(request.GET.get("group"))
        removed = request.GET.get("removed")

        if removed == 'false':
            removed = False
        else:
            removed = True
        print('group----', group_id)
        if group_id == 0 :
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)
        elif group_id == -1:
            member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=removed, is_dataroom_admin=True).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)
        else:
            member = DataroomMembers.objects.filter(dataroom_id=pk, end_user_group__in=[int(group_id)], is_deleted=removed).exclude(dataroom_id=dataroom.id, member_id=dataroom.user_id)       
        serializer = DataroomMembersSerializer(member, many=True)
        data = serializer.data

        for da in data:
            memb = DataroomMembers.objects.get(id=da['id'])
            try:
                group = DataroomGroups.objects.get(id=memb.end_user_group.all().first().id)
                da['group'] = group.group_name
            except:
                da['group'] = "Admin"
        datas= {}
        datas['users'] = data
        if removed == False and (group_id == 0 or group_id == -1):
            da = {}
            serializer = UserSerializer(dataroom.user, many=False)
            serializer_data = serializer.data
            da['member'] = serializer_data
            da['member_added_by'] = serializer_data
            da['group'] = "Admin"
            da['date_joined'] = user.date_joined.strftime('%d/%m/%Y %H:%M:%S')
            datas['users'].append(da)

        from . import utils
        import csv

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        writer = csv.writer(response)
        #harish 
        print('-------------------------------------------')
        print(datas['users'])
        print('-------------------------------------------')

        header_data, datas = utils.getExcelDataUsersGroupsReport(datas['users'])
        
        writer.writerow(header_data)
        writer.writerows(datas)
        return response






















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
            print(user.id)
            print(member_id)
            status1=InviteUser.objects.filter(invitiation_receiver=member_id).values_list('is_invitation_accepted',flat=True).last()
            print('status---------------------------------',status1)
            print('status')
            print(da['member']['is_active'])
            if status1 == True or da.get("member").get("is_admin"):
                da['member']['is_active'] = True
            elif status1 == None:
                da['member']['is_active'] = True
            else:
                da['member']['is_active'] = False
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
                da['last_login'] = access_history.logged_in_time.strftime('%d/%m/%Y %H:%M:%S')
            except:
                da['last_login '] = 'N. A.'
        data['active_users'] = count
        return Response(data, status=status.HTTP_201_CREATED)

class ExportUsersStatus(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        data = {}
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

        member = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False, date_joined__gte=first_date, date_joined__lte=todays_date)
        serializer = DataroomMembersSerializer(member, many=True)
        for members in serializer.data:
            workspace_view = DataroomView.objects.filter(dataroom_id=pk, user_id=members.get('member').get('id')).order_by('id').reverse().first()
            folder_workspace_data = DataroomViewSerializer(workspace_view, many=False).data
            members['last_view'] = folder_workspace_data.get('created_date')
            print(folder_workspace_data)
        data = serializer.data

        from . import utils
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Activity.csv"'
        writer = csv.writer(response)

        header_data, datas = utils.getExcelDataUsersStatusReport(data)

        writer.writerow(header_data)
        writer.writerows(datas)
        return response



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
        for primary in primary_list:
            dataroom_mem = DataroomMembers.objects.filter(id=primary['id']).first()
            dataroom_mem.is_primary_user = primary['is_primary_user']
            dataroom_mem.is_q_a_user = primary['is_q_a_user']
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
        if dataroom_member.is_q_a_submitter_user:
            dataroom_member.is_q_a_submitter_user = False
            dataroom_member.save()
            return Response({'data': 'Q&A submitter removed successfully.'}, status=status.HTTP_201_CREATED)
        else:
            dataroom_member.is_q_a_submitter_user = True
            dataroom_member.save()
            return Response({'data': 'Q&A submitter added successfully.'}, status=status.HTTP_201_CREATED)

class UserByEmail(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        email = str(request.GET.get('email').lower())
        print("Emaillll", email)
        user_obj = User.objects.filter(email=email).first()
        print("Userssssssssss", user_obj)
        serializer = UserSerializer(user_obj, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AllGroups(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        print("pkkkkkkkkkkkk", pk)
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
        contact = Contacts.objects.filter(user_id=user.id).values('email')
        q_list = [Q(first_name__icontains=key), Q(last_name__icontains=key), Q(email__icontains=key)]
        user = User.objects.filter(email__in=contact).filter(reduce(operator.or_, q_list))
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        