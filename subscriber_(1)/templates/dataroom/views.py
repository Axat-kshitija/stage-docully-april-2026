import os
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
# from oauth2_provider.models import *

# from oauth2_provider.views.generic import ProtectedResourceView
from rest_framework import permissions, routers, serializers, viewsets
from rest_framework.parsers import JSONParser

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# import requests
from rest_framework.response import Response
# from oauthlib.common import generate_token
from rest_framework import status
from datetime import datetime
from django.utils import timezone 
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.crypto import get_random_string
import datetime
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    ListCreateAPIView)

from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FileUploadParser
from django.core.mail import send_mail
from random import randint

from userauth.serializers import UserSerializer, AccessHistorySerializer
from userauth import constants, utils
from userauth.models import Profile, AccessHistory, User
from . import utils as dataroom_utils

from .serializers import DataroomSerializer, DataroomOverviewSerializer,\
        DataroomModulesSerializer, ContactSerializer, DataroomDisclaimerSerializer, \
        ContactGroupSerializer, ContactGroupMembersSerializer
from .models import Dataroom, DataroomOverview, Contacts, DataroomDisclaimer, \
    ContactGroup, ContactGroupMembers, DataroomView, DataroomModules, Watermarking

from myteams.models import MyTeams, TeamMembers

# import data_documents module 
from data_documents.models import DataroomFolder, IndexDownload

from myteams.serializers import MyTeamsSerializer
from users_and_permission.models import DataroomMembers, DataroomGroups 
from users_and_permission.serializers import DataroomMembersSerializer
from emailer import utils as emailer_utils
import json
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete
import requests
import urllib.request
from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework.renderers import JSONRenderer
from django.db.models import Count, Min, Sum, Avg
import csv
import pdb
import codecs
from data_documents.serializers import DataroomFolderSerializer
from .serializers import WatermarkingSerializer

def create_parent_folder(folder, serializer):
    create_folder = DataroomFolder()
    create_folder.user_id = folder.user.id
    create_folder.dataroom_id = serializer.data['id']
    create_folder.name = folder.name
    create_folder.path = folder.path
    create_folder.index = folder.index
    create_folder.is_file_index = folder.is_file_index
    create_folder.last_updated_user = folder.last_updated_user
    create_folder.parent_path = folder.parent_path
    create_folder.is_root_folder = folder.is_root_folder
    create_folder.is_folder = folder.is_folder
    create_folder.is_infected = folder.is_infected
    create_folder.file_content_type = folder.file_content_type
    create_folder.file_size = folder.file_size
    create_folder.parent_folder = folder.parent_folder
    create_folder.pages = folder.pages
    create_folder.version = folder.version
    create_folder.dataroom_folder_uuid = folder.dataroom_folder_uuid
    create_folder.uploaded_by = folder.uploaded_by
    create_folder.selected = folder.selected
    create_folder.is_deleted = folder.is_deleted
    create_folder.deleted_by = folder.deleted_by
    create_folder.deleted_by_date = folder.deleted_by_date
    create_folder.is_view = folder.is_view
    create_folder.is_print = folder.is_print
    create_folder.is_download = folder.is_download
    create_folder.save()
    return create_folder


def create_sub_folder1(c_p_f, folder, serializer):
    create_folder = DataroomFolder()
    create_folder.user_id = folder.user.id
    create_folder.dataroom_id = serializer.data['id']
    create_folder.name = folder.name
    create_folder.path = folder.path
    create_folder.index = folder.index
    create_folder.is_file_index = folder.is_file_index
    create_folder.last_updated_user = folder.last_updated_user
    create_folder.parent_path = folder.parent_path
    create_folder.is_root_folder = folder.is_root_folder
    create_folder.is_folder = folder.is_folder
    create_folder.is_infected = folder.is_infected
    create_folder.file_content_type = folder.file_content_type
    create_folder.file_size = folder.file_size
    create_folder.parent_folder = c_p_f
    create_folder.pages = folder.pages
    create_folder.version = folder.version
    create_folder.dataroom_folder_uuid = folder.dataroom_folder_uuid
    create_folder.uploaded_by = folder.uploaded_by
    create_folder.selected = folder.selected
    create_folder.is_deleted = folder.is_deleted
    create_folder.deleted_by = folder.deleted_by
    create_folder.deleted_by_date = folder.deleted_by_date
    create_folder.is_view = folder.is_view
    create_folder.is_print = folder.is_print
    create_folder.is_download = folder.is_download
    create_folder.save()    


def create_sub_folder2(folder, serializer):
    create_folder = DataroomFolder()
    create_folder.user_id = folder.user.id
    create_folder.dataroom_id = serializer.data['id']
    create_folder.name = folder.name
    create_folder.path = folder.path
    create_folder.index = folder.index
    create_folder.is_file_index = folder.is_file_index
    create_folder.last_updated_user = folder.last_updated_user
    create_folder.parent_path = folder.parent_path
    create_folder.is_root_folder = folder.is_root_folder
    create_folder.is_folder = folder.is_folder
    create_folder.is_infected = folder.is_infected
    create_folder.file_content_type = folder.file_content_type
    create_folder.file_size = folder.file_size
    create_folder.parent_folder = folder.parent_folder
    create_folder.pages = folder.pages
    create_folder.version = folder.version
    create_folder.dataroom_folder_uuid = folder.dataroom_folder_uuid
    create_folder.uploaded_by = folder.uploaded_by
    create_folder.selected = folder.selected
    create_folder.is_deleted = folder.is_deleted
    create_folder.deleted_by = folder.deleted_by
    create_folder.deleted_by_date = folder.deleted_by_date
    create_folder.is_view = folder.is_view
    create_folder.is_print = folder.is_print
    create_folder.is_download = folder.is_download
    create_folder.save() 


class CloneDataroomApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        data = {}
        user = request.user
        dataroom = Dataroom.objects.filter(id=request.data['dataroom']).first()
        data['dataroom_name'] = request.data['dataroom_name']
        data['dataroom_modules'] = {}
        data['dataroom_modules']['is_watermarking'] = dataroom.dataroom_modules.is_watermarking
        data['dataroom_modules']['is_drm'] = dataroom.dataroom_modules.is_drm
        data['dataroom_modules']['is_question_and_answers'] = dataroom.dataroom_modules.is_question_and_answers
        data['dataroom_modules']['is_collabration'] = dataroom.dataroom_modules.is_collabration
        data['dataroom_modules']['is_ocr'] = dataroom.dataroom_modules.is_ocr
        data['dataroom_modules']['is_editor'] = dataroom.dataroom_modules.is_editor
        data['dataroom_admin'] = {}
        dataroom_mem = DataroomMembers.objects.filter(dataroom_id=request.data['dataroom']).first()
        if dataroom_mem:
            data['dataroom_admin']['first_name'] = dataroom_mem.member.first_name
            data['dataroom_admin']['last_name'] = dataroom_mem.member.last_name
            data['dataroom_admin']['email'] = dataroom_mem.member.email

        data['is_account_level_branding'] = False
        data['dataroom_storage_allocated'] = dataroom.dataroom_storage_allocated
        data['user'] = dataroom.user_id
        dataroom_admin_data = data.get('dataroom_admin')
        serializer = DataroomSerializer(data=data, context={'dataroom_modules': data.get("dataroom_modules")})        
        if serializer.is_valid():
            serializer.save()
            c_d_object = CreateOverviewHeading()
            create_nested_data = c_d_object.create_dataroom_overiview_headings_links(request, serializer.data)
            if request.data['user_group']:
                pass
                groups = DataroomGroups.objects.filter(dataroom_id=dataroom.id)
                if groups:
                    for group in groups:
                        g = DataroomGroups()
                        g.group_name = group.group_name
                        g.dataroom_id = serializer.data['id']
                        g.group_created_by_id = group.group_created_by_id
                        g.limited_access = group.limited_access
                        g.end_user = group.end_user
                        g.is_deleted = group.is_deleted
                        g.save()
                        dataroom_mems = DataroomMembers.objects.filter(dataroom_id=group.dataroom_id)
                        for dataroom_mem in dataroom_mems:
                            g_obj = dataroom_mem.end_user_group.filter(id=group.id)
                            if g_obj:
                                dataroom_mem_create = DataroomMembers()
                                d_ava = DataroomMembers.objects.filter(dataroom_id=serializer.data['id'], member_id=dataroom_mem.member.id).first()
                                if not d_ava:
                                    dataroom_mem_create.dataroom_id = serializer.data['id']
                                    dataroom_mem_create.member_id = dataroom_mem.member.id
                                    try:
                                        dataroom_mem_create.member_type_id = dataroom_mem.member_type.id
                                    except:
                                        pass
                                    try:                                
                                        dataroom_mem_create.member_added_by_id = dataroom_mem.member_added_by.id
                                    except:
                                        pass
                                    dataroom_mem_create.is_dataroom_admin = dataroom_mem.is_dataroom_admin
                                    dataroom_mem_create.is_la_user = dataroom_mem.is_la_user
                                    dataroom_mem_create.is_end_user = dataroom_mem.is_end_user
                                    dataroom_mem_create.is_deleted = dataroom_mem.is_deleted
                                    dataroom_mem_create.is_deleted_end = dataroom_mem.is_deleted_end
                                    dataroom_mem_create.is_deleted_la = dataroom_mem.is_deleted_la
                                    dataroom_mem_create.save()
                                    dataroom_mem_create.end_user_group.add(g)
                                else:
                                    d_ava.end_user_group.add(g)
            #create_nested_data = self.create_dataroom_overiview_headings_links(request, serializer.data)
            if request.data['clone_data']:
                folder = DataroomFolder.objects.filter(id=request.data['clone_data']).first()
                if folder:
                    c_p_f1 = create_parent_folder(folder, serializer)
                    clone_data_id = request.data['clone_data']
                    while True:
                        print ("clone_data_id:-", clone_data_id)
                        if clone_data_id:
                            sub_folder_list1 = DataroomFolder.objects.filter(parent_folder_id=clone_data_id)
                            if sub_folder_list1:
                                for sub_folder in sub_folder_list1:
                                    c_p_f = create_sub_folder1(c_p_f1, sub_folder, serializer)
                                    clone_data_id = sub_folder.id
                            else:
                                clone_data_id = 0
                        else:
                            break
                        #     sub_folder_list2 = DataroomFolder.objects.filter(parent_folder_id=sub_folder.id)
                        #     for sub_folder2 in sub_folder_list2:
                        #         c_p_f = create_sub_folder2(sub_folder2, serializer)
                        #         sub_folder_list2 = DataroomFolder.objects.filter(parent_folder_id=sub_folder2.id)

            if create_nested_data:
                # send email and update the Dataroom Members table
                # assign admin only once the data
                _new_dataroom_admin = DataroomAdmin()
                # create dataroom admin first and then send the user data to the dataroom
                dataroom_admin, is_exist_user, __dataroom_admin_password = _new_dataroom_admin.create_dataroom_admins(request, dataroom_admin_data)
                if dataroom_mem:
                    print ("dataroom_admin is", dataroom_admin.email)
                    print ("is_exist_user", is_exist_user)
                    print ("__dataroom_admin_password", __dataroom_admin_password)
                    #dataroom_admin = User.objects.get(email__iexact = dataroom_admin)
                    dataroom_member_data = {
                        'dataroom':serializer.data.get('id'), 
                        'member' :dataroom_admin.id, 
                        'member_type':1, 
                        'member_added_by':user.id
                    }
                    dataroom_admin.is_admin = True
                    dataroom_admin.is_end_user = True
                    dataroom_admin.save()
                    dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member_data)
                    print ("dataroom_member is valid", dataroom_member_serializer.is_valid())
                    print ("dataroom_member errors", dataroom_member_serializer.errors)
                    
                    if dataroom_member_serializer.is_valid():
                        dataroom_member_serializer.save()
                        admin_user = User.objects.filter(email=data['dataroom_admin']['email']).first()
                        if admin_user:
                            obj, created = DataroomMembers.objects.get_or_create(dataroom_id=serializer.data['id'], member_id=admin_user.id)
                            obj.is_dataroom_admin = True
                            obj.save()
                        # send email to the dataroom member
                        if is_exist_user:
                            print ("is_exist_user", is_exist_user)
                            print ("send email to already exist should called")
                            dataroom_utils.send_email_to_already_exist_admin_or_end_user(dataroom_admin, serializer.data,  subject = "Welcome to Confiex Dataroom")
                            print ("Email sucessfully send")
                        else:
                            print ("is_exist_user", is_exist_user)
                            print ("create new user send password method should called")
                            dataroom_utils.send_password_to_dataroom_admin_or_end_user(dataroom_admin , serializer.data, __dataroom_admin_password , subject = "Welcome to Confiex Dataroom" )                     
                            print ("Email successfully send")
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                # update the dataroom_members table 
            return Response({"errors":'Error in creating nested data'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
        

class DataroomApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = request.user
        datarooms = []
        if user.is_superadmin:
            datarooms = Dataroom.objects.filter(user_id = user.id)
        elif user.is_admin:
            dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id)]
            # print ("dataroom ids", dataroom_ids)
            datarooms = Dataroom.objects.filter(id__in=dataroom_ids)

            # my_team_ids = [team.myteam.id for team in TeamMembers.objects.filter(member_id=user.id)]
            # print ("my team ids ", my_team_ids)
            # datarooms = Dataroom.objects.filter(my_team_id__in = my_team_ids)
        elif user.is_end_user:
            dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id)]
            # print ("dataroom ids", dataroom_ids)
            datarooms = Dataroom.objects.filter(id__in=dataroom_ids)
        serializer = DataroomSerializer(datarooms, many=True)
        data = serializer.data
        # print ("datarooms are", serializer.data)
        for da in data:
            da['document_count'] = DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=False, is_folder=False).count()
            da_over = DataroomOverview.objects.filter(dataroom_id=da['id'],).first()
            da['send_daily_email_updates'] = da_over.send_daily_email_updates
            da['choose_overview_default_page'] = da_over.choose_overview_default_page
            da['hide_file_indexing'] = da_over.hide_file_indexing
        return Response(data, status=status.HTTP_201_CREATED)       

    def post(self, request, format=None):
        data = request.data
        user = request.user
        data["user"] = user.id
        # print ("data is", data)
        dataroom_admin_data = data.get('dataroom_admin')
        serializer = DataroomSerializer(data=data, context={'dataroom_modules': data.get("dataroom_modules")})        
        if serializer.is_valid():
            serializer.save()
            c_d_object = CreateOverviewHeading()
            create_nested_data = c_d_object.create_dataroom_overiview_headings_links(request, serializer.data)
            #create_nested_data = self.create_dataroom_overiview_headings_links(request, serializer.data)
            if create_nested_data:
                # send email and update the Dataroom Members table
                # assign admin only once the data
                _new_dataroom_admin = DataroomAdmin()
                # create dataroom admin first and then send the user data to the dataroom
                dataroom_admin, is_exist_user, __dataroom_admin_password = _new_dataroom_admin.create_dataroom_admins(request, dataroom_admin_data)
                # print ("dataroom_admin is", dataroom_admin.email)
                # print ("is_exist_user", is_exist_user)
                # print ("__dataroom_admin_password", __dataroom_admin_password)
                #dataroom_admin = User.objects.get(email__iexact = dataroom_admin)
                dataroom_member_data = {
                    'dataroom':serializer.data.get('id'), 
                    'member' :dataroom_admin.id, 
                    'member_type':1, 
                    'member_added_by':user.id
                }
                dataroom_admin.is_admin = True
                dataroom_admin.is_end_user = True
                dataroom_admin.save()
                dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member_data)
                # print ("dataroom_member is valid", dataroom_member_serializer.is_valid())
                # print ("dataroom_member errors", dataroom_member_serializer.errors)
                
                if dataroom_member_serializer.is_valid():
                    dataroom_member_serializer.save()
                    admin_user = User.objects.filter(email=request.data['dataroom_admin']['email']).first()
                    if admin_user:
                        obj, created = DataroomMembers.objects.get_or_create(dataroom_id=serializer.data['id'], member_id=admin_user.id, member_added_by_id=user.id)
                        obj.is_dataroom_admin = True
                        obj.save()
                    # send email to the dataroom member
                    if is_exist_user:
                        # print ("is_exist_user", is_exist_user)
                        # print ("send email to already exist should called")
                        dataroom_utils.send_email_to_already_exist_admin_or_end_user(dataroom_admin, serializer.data,  subject = "Welcome to Confiex Dataroom")
                        # print ("Email sucessfully send")
                    else:
                        # print ("is_exist_user", is_exist_user)
                        # print ("create new user send password method should called")
                        dataroom_utils.send_password_to_dataroom_admin_or_end_user(dataroom_admin , serializer.data, __dataroom_admin_password , subject = "Welcome to Confiex Dataroom" )                     
                        # print ("Email successfully send")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                # update the dataroom_members table 
            return Response({"errors":'Error in creating nested data'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


class DataroomFolderApi(APIView):
    """docstring for DataroomFolderApi"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        dataroom_folder_list = DataroomFolder.objects.filter(is_root_folder=True, is_deleted=False)
        serializer = DataroomFolderSerializer(dataroom_folder_list, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)       


def create_dataroom_overiview_headings_links(request , data):

    dataroom_overview_heading = []

    dataroom_custom_links = []
    
    dataroom_overview_data = {
        'dataroom': data.get('id'),
        'send_daily_email_updates': True,
        'choose_overview_default_page': True,
        'hide_file_indexing':True,
        'user': request.user.id, 
        'dataroom_overview_heading':json.dumps(dataroom_overview_heading), 
        'dataroom_custom_links':json.dumps(dataroom_custom_links)
    }

    dataroom_overview_serializer = DataroomOverviewSerializer(data=dataroom_overview_data)
    # print ("dataroom dataroom_overview_serializer", dataroom_overview_serializer.is_valid())
    # print ("dataroom dataroom_overview_serializer erros", dataroom_overview_serializer.errors)
    
    if dataroom_overview_serializer.is_valid():
        dataroom_overview_serializer.save()

    return True

class DataroomDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk, request):
        try:
            user = request.user
            return Dataroom.objects.get(id=pk)
        except Dataroom.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # print ("pk is", pk)
        dataroom = self.get_object(pk, request)
        serializer = DataroomSerializer(dataroom)
        data = serializer.data
        dataroom_mem = DataroomMembers.objects.filter(dataroom_id=int(pk), is_dataroom_admin=True, is_primary_user=True).first()
        serializer = DataroomMembersSerializer(dataroom_mem, many=False)
        print ("Here add admin data")
        if dataroom_mem:
            data['dataroom_admin_data'] = serializer.data
            data['is_primary_user'] = True
        else:
            data['is_primary_user'] = False
        # data['modules'] = DataroomModules.objects.filter(id=data['dataroom_modules']).first()
        return Response(data)

    def put(self, request, pk, format=None):
        dataroom = self.get_object(pk, request)
        # print ("data is", request.data)
        data = request.data
        del data["dataroom_logo"]
        serializer = DataroomSerializer(dataroom, data=data)
        print ("serializer is valid", serializer.is_valid())
        print ("serializer errors ", serializer.errors)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        dataroom = self.get_object(pk, request)
        # dataroom.delete()
        dataroom.is_request_for_deletion = True 
        dataroom.save()
        dataroom_serializer = DataroomSerializer(dataroom, many=False)
        #send email to Super admin that we have recived the request for deletaion of dataroom
        emailer_utils.send_deletion_dataroom_email(dataroom, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DataroomOverviewApi(APIView):
    """docstring for DataroomOverviewAll"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DataroomOverviewSerializer
    
    def get(self, request, format=None):
        user = request.user
        datarooms_overview = DataroomOverview.objects.filter(user_id = user.id)
        serializer = DataroomOverviewSerializer(datarooms_overview, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def post(self, request, format=None):
        data = request.data
        user = request.user
        data["user"] = user.id
        print("dataaaaaaaaaa",data)
        dataroom_overview = DataroomOverview.objects.get(dataroom_id= data.get("dataroomId"))
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        return Response(dataroom_overview_serializer.data, status=status.HTTP_201_CREATED)

class ArchiveRequestApi(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk, request):
        try:
            user = request.user
            return Dataroom.objects.get(user_id=user.id, pk=pk)
        except Dataroom.DoesNotExist:
            raise Http404


    def delete(self, request, pk, format=None):
        dataroom = self.get_object(pk, request)
        dataroom.is_request_for_archive = True
        dataroom.save()
        
        dataroom_serializer = DataroomSerializer(dataroom, many=False)
        emailer_utils.send_archive_dataroom_email(dataroom, request.user)
        return Response(dataroom_serializer.data, status=status.HTTP_201_CREATED)


class DeleteRequestApi(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk, request):
        try:
            user = request.user
            return Dataroom.objects.get(user_id=user.id, pk=pk)
        except Dataroom.DoesNotExist:
            raise Http404


    def delete(self, request, pk, format=None):
        # Change the dataroom api status 
        dataroom = self.get_object(pk, request)
        dataroom.is_request_for_deletion = True 
        dataroom.save()
        dataroom_serializer = DataroomSerializer(dataroom, many=False)
        #send email to Super admin that we have recived the request for deletaion of dataroom
        emailer_utils.send_deletion_dataroom_email(dataroom, request.user)
        return Response(dataroom_serializer.data, status=status.HTTP_204_NO_CONTENT)


class UpdateDataroomOverviewSettingApi(APIView):

    def put(self, request, pk, format=None):
        print ("pk is", pk)
        data = request.data
        user = request.user
        dataroom = Dataroom.objects.get(user_id=user.id, id=pk)
        data["dataroom"] = dataroom.id
        print ("data is ", data)
        print ("dataroom overview id is:", )
        # data["user"] = user.id
        # overview_links_data = data.get('overview_links')
        # overview_headings_data = data.get('overview_headings')
        # print ("pk is:", pk)
        # print ("data is:", data)
        # print ("user is:", user.email)
        # print ("overview_links_data", overview_links_data)
        # print ("overview_headings_data", overview_headings_data)
        dataroom_overview = DataroomOverview.objects.get(id=data.get("id"))
        del data["change_video_ppt"]
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, data=data)
        
        print ("dataroom_overview_serializer.isvalid", dataroom_overview_serializer.is_valid())
        print ("dataroom_overview_serializer.errors", dataroom_overview_serializer.errors)
        
        if dataroom_overview_serializer.is_valid():
            dataroom_overview_serializer.save()
            print ("dataroom overview successfully saved")
        # for link in overview_links_data:
        #   link['user']= user.id
        #   link['dataroom']= dataroom.id
        #   link_serializer = CustomLinkSerializer(data=link)

        #   print ("link is valid", link_serializer.is_valid())
        #   print ("link errors", link_serializer.errors)
            
        #   if link_serializer.is_valid():
        #       link_serializer.save()
        #       print ("link sucessfully saved")
        # for paragraph in overview_headings_data:
        #   paragraph['user'] = user.id
        #   paragraph['dataroom']=dataroom.id
        #   paragraph_serializer = DataroomOverviewHeadingSerializer(data=paragraph)
            

        #   print ("paragraph is valid", paragraph_serializer.is_valid())
        #   print ("paragraph errors", paragraph_serializer.errors)
            
        #   if paragraph_serializer.is_valid():
        #       paragraph_serializer.save()
        #       print ("paragraph successfully saved")

        return Response(dataroom_overview_serializer.data, status=status.HTTP_204_NO_CONTENT)


class CreateContactApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = request.user
        contacts = Contacts.objects.filter(user_id=user.id)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def post(self, request, format=None):
        print ("Create Contact Api called")
        data = request.data
        print ("request data is ", data)
        user = request.user
        data["user"] = user.id

        serializer = ContactSerializer(data=data)
        print ("serializer", serializer.is_valid())
        print ("serializer", serializer.errors)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllAdminApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        if user.is_superadmin:
            users = User.objects.filter()
        elif user.is_admin:
            users = User.objects.filter(user_id = user.id)

        users = User.objects.filter()


class UploadDataroomPic(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk, format=None):
        user = request.user
        dataroom_pic = request.FILES.getlist('profile_pic')
        dataroom = Dataroom.objects.get(user_id=user.id,id=pk)
        if dataroom.dataroom_logo.url != "/media/default_images/dataroom-icon.png":
            dataroom.dataroom_logo.delete(save=True)
        dataroom.dataroom_logo = dataroom_pic[0]
        dataroom.save()
        serializer = DataroomSerializer(dataroom, many=False)
        data = {
        "data": serializer.data, 
        "msg" : "Dataroom picture successfully added!"
        }
        return Response(data)


class SetDefaultDataroomPic(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk, format=None):
        user = request.user
        dataroom = Dataroom.objects.get(user_id=user.id,id=pk)
        print ("dataroom logo url ", dataroom.dataroom_logo.url)
        if dataroom.dataroom_logo.url != "/media/default_images/dataroom-icon.png":
            print ("dont delete the url")
            dataroom.dataroom_logo.delete(save=True)
    
        dataroom.dataroom_logo = "default_images/dataroom-icon.png"
        dataroom.save()
        serializer = DataroomSerializer(dataroom, many=False)
        data = {
            "data": serializer.data, 
            "msg" : "Default dataroom picture successfully added!"
        }
        return Response(data)

class UploadDataroomOverviewVideo(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        overview_video = request.FILES.getlist('overview_video')
        data = request.data
        dataroom_id = data.get("dataroom_id")
        overview_video_file = data.get("file")
        dataroom_overview = DataroomOverview.objects.get(dataroom_id=dataroom_id)
        dataroom_overview.change_video_ppt.delete(save=True)
        dataroom_overview.change_video_ppt = overview_video_file
        dataroom_overview.save()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        
        data = {
            'msg': "Overview video successfully uploaded !", 
            'data':dataroom_overview_serializer.data
        }
        return Response(data)

class RemoveDataroomOverviewVideo(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        print ("remove dataroom overview api method called")
        user = request.user
        dataroom_overview = DataroomOverview.objects.get(user_id=user.id, dataroom_id=pk)
        dataroom_overview.change_video_ppt.delete()
        dataroom_overview.save()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        return Response({"data":dataroom_overview_serializer.data, "msg":"Overview video successfully removed !"})

class AddNewDataroomDisclaimer(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, pk, format=None):
        print ("get method called", pk)
        user = request.user
        data = request.data
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(user_id=user.id, dataroom_id=pk)
        dataroom_disclaimer_serilizer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=True)
        print ("dataroom_disclaimer_serilizer data", dataroom_disclaimer_serilizer.data)
        return Response(dataroom_disclaimer_serilizer.data)

    def post(self, request, pk, format=None):
        #data = request.data
        user = request.user
        print ("request files", request.FILES)
        disclaimer = request.FILES.get('fileKey')
        if disclaimer == None:
            disclaimer = request.FILES.getlist('file')[0]
        print ("request files", disclaimer)
        print ("file name is", disclaimer.name)

        new_data = {
            'user':user.id, 
            'dataroom': pk, 
            'is_dataroom_disclaimer_default': False, 
            'dataroom_disclaimer_preview_status': 1,
            'dataroom_disclaimer_name': disclaimer.name 
        }

        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(data=new_data)
        print ("dataroom disclaimer serializer", dataroom_disclaimer_serializer.is_valid())
        print ("dataroom disclaimer errors", dataroom_disclaimer_serializer.errors)
        if dataroom_disclaimer_serializer.is_valid():
            dataroom_disclaimer_serializer.save()
            dataroom_disclaimer = DataroomDisclaimer.objects.get(id=dataroom_disclaimer_serializer.data.get("id"))
            dataroom_disclaimer.dataroom_disclaimer.delete(save=True)
            dataroom_disclaimer.dataroom_disclaimer = disclaimer
            dataroom_disclaimer.save()
            dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
            data = {
            'data': dataroom_disclaimer_serializer.data, 
            'msg': 'Disclaimer successfully added !'
            }
            d_m = DataroomMembers.objects.filter(dataroom_id=pk)
            for each in d_m:
                each.disclaimer_status = False
                each.save()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class DataroomDisclaimerApiView(APIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk , format=None):
        user = request.user
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk, user_id=user.id)
        filename = dataroom_disclaimer.dataroom_disclaimer.file.name.split('/')[-1]
        filename_name = dataroom_disclaimer.dataroom_disclaimer.name
        
        file_path = os.path.join(settings.MEDIA_ROOT, filename_name)
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename='+filename
            return response
            
        
    def put(self, request, pk, format=None):
        user = request.user
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk)
        if dataroom_disclaimer:
            print ("dataroom disclaimer default", dataroom_disclaimer.is_dataroom_disclaimer_default)
            if not dataroom_disclaimer.is_dataroom_disclaimer_default:
                dataroom_disclaimer.is_dataroom_disclaimer_default = True
                dataroom_disclaimer.save()
            else:
                dataroom_disclaimer.is_dataroom_disclaimer_default = False
                dataroom_disclaimer.save()
            dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        return Response(dataroom_disclaimer_serializer.data)

    def delete(self, request, pk, format=None):
        user = request.user
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk)
        dataroom_disclaimer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      


class CreateContactGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        print("get method called")
        user = request.user
        contact_groups = ContactGroup.objects.filter(user_id=user.id)
        contact_serializer = ContactGroupSerializer(contact_groups, many=True)
        print ("contact serializer data", contact_serializer.data)
        return Response(contact_serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        print ("create contact group")
        user = request.user
        data = request.data
        data["user"] = user.id
        print ("data is", data)
        contact_serializer = ContactGroupSerializer(data=data)
        print ("Contact Serilizer ", contact_serializer.is_valid())
        print ("Contact errors ", contact_serializer.errors)
        
        if contact_serializer.is_valid():
            contact_serializer.save()

            data ={
            'data': contact_serializer.data, 
            'msg' : 'Contact group successfully added !'
            }
            return Response(contact_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateDataroomContactGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("get method called")
        # print ("dataroom id is", pk)
        user = request.user
        contact_groups = ContactGroup.objects.filter(user_id=user.id, dataroom_id=pk)
        contact_serializer = ContactGroupSerializer(contact_groups, many=True)
        return Response(contact_serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        # print ("create contact group")
        user = request.user
        data = request.data
        # print ("dataroom id is:",pk)
        data["user"] = user.id
        # print ("data is", data)
        data["dataroom"] = pk
        contact_serializer = ContactGroupSerializer(data=data)
        # print ("Contact Serilizer ", contact_serializer.is_valid())
        # print ("Contact errors ", contact_serializer.errors)
        
        if contact_serializer.is_valid():
            contact_serializer.save()

            data ={
                'data': contact_serializer.data, 
                'msg' : 'Contact group successfully added !'
            }
            return Response(contact_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        group_obj = ContactGroup.objects.get(id=pk)
        group_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)        



class AddNewMemberToContactGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        data = request.data
        selected_group_id = data.get("selected_group_id")
        selected_members = data.get("selected_members")
        if len(selected_members) > 1:
            for res in selected_members:
                try :
                    contact_group_member = ContactGroupMembers.objects.get(contact_group_id=selected_group_id, contact_id=res["id"])
                    print ("Dont insert the contact in group , beause this contact already exist")
                except:
                    new_data = {
                        'user' : user.id, 
                        'contact_group' : selected_group_id, 
                        'contact' : res["id"]
                    }
                    print ("new data is", new_data)
                    contact_group_members_serializer = ContactGroupMembersSerializer(data= new_data)
                    print ("contact group serializer ", contact_group_members_serializer.is_valid())
                    print ("contact group errors", contact_group_members_serializer.errors)
                    if contact_group_members_serializer.is_valid():
                        contact_group_members_serializer.save()
            return Response({'msg':"Contact added !"}, status=status.HTTP_201_CREATED)
        elif len(selected_members) == 1:
            print ("if selected_members length is equal to 1 ")
            new_data = {
                'user' : user.id, 
                'contact_group' : selected_group_id, 
                'contact' : selected_members[0]["id"]
            }
            try :
                contact_group_member = ContactGroupMembers.objects.get(contact_group_id=selected_group_id, contact_id=new_data.get("contact"))
                if contact_group_member :
                    return Response({'msg':"Contact added !"}, status=status.HTTP_201_CREATED)
            except:
                print ("new data is ", new_data)
                contact_group_members_serializer = ContactGroupMembersSerializer(data= new_data)
                print ("contact group serializer ", contact_group_members_serializer.is_valid())
                print ("contact group errors", contact_group_members_serializer.errors)
                if contact_group_members_serializer.is_valid():
                    contact_group_members_serializer.save()        
                    return Response({'msg':"Contact added !"}, status=status.HTTP_201_CREATED)
        else:
            print("There is no member is selceted")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetAllContactsAssocitaedWithTheGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        contact_group_members = [contact.contact.id for contact in ContactGroupMembers.objects.filter(contact_group_id=pk)]
        print ("contact_group_members", contact_group_members)
        all_contact_members = Contacts.objects.filter(id__in=contact_group_members)
        all_contact_members_serializer = ContactSerializer(all_contact_members, many=True)
        print ("All contacts member serializer", all_contact_members_serializer.data)
        return Response(all_contact_members_serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        user = request.user
        data = request.data
        #print ("pk is", pk)
        if pk == 0:
            #print ("data is", data)
            #print ("primary key is", pk)
            contact_group_member = ContactGroupMembers.objects.get(contact_id=data.get("contact"))
            contact_group_member.delete()
            return Response({'msg':'Contact successfully deleted !'},status=status.HTTP_201_CREATED)
        else:
            #print ("data is", data)
            #print ("primary key is", pk)
            contact = Contacts.objects.get(id=data.get("contact"))
            contact.delete()
            return Response({'msg':'Contact deleted from group.'},status=status.HTTP_201_CREATED)
           

class CreateDataroomFromMyTeam(APIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        print ("post method called")
        user = request.user
        data = request.data
        my_team_id = data.get("my_team_id")
        print ("my team id is", my_team_id)
        print ("data is" , data)
        # 1 ) check if dataroom is exceed the allowed limit or not

        dataroom_count = Dataroom.objects.filter(my_team=my_team_id).count()
        my_team_allowed_datarooms = MyTeams.objects.get(id=my_team_id)
        print ("dataroom count ", dataroom_count)
        print ("my_team_allowed_datarooms", my_team_allowed_datarooms.dataroom_allowed)
        print ("dataroom coutnt is", dataroom_count <= my_team_allowed_datarooms.dataroom_allowed)
        if dataroom_count < my_team_allowed_datarooms.dataroom_allowed:

            print ("dataroom count is", dataroom_count)
            dataroom_modules = (data.get("dataroom")).get('dataroom_modules')
            dataroom_data = data.get('dataroom')
            dataroom_data["user"] = user.id
            dataroom_data["my_team"] = int(my_team_id)
            serializer = DataroomSerializer(data=dataroom_data, context={'dataroom_modules': dataroom_modules})
            print ("serailizer valid", serializer.is_valid())
            print ("serailizer errors", serializer.errors)
            
            if serializer.is_valid():
                serializer.save()
                c_d_object = CreateOverviewHeading()
                create_nested_data = c_d_object.create_dataroom_overiview_headings_links(request, serializer.data)
                if create_nested_data:
                    data = {
                        'message' : " Dataroom successfully created",
                        'data' : serializer.data, 
                        'success': True  
                    }
                    return Response(data, status=status.HTTP_201_CREATED)
                return Response({"errors":'Error in creating nested data'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else :
            print ("dataroom limit is exceed")
            data = {
                'message': "Dataroom limit is exceed !", 
                'success': False
            }
            return Response(data, status=status.HTTP_201_CREATED)

class CreateOverviewHeading:
    def __init__(self):
        print ("Created overview heading class called")
        #self.name = name

    def create_dataroom_overiview_headings_links(self, request, data):
        dataroom_overview_heading = []
        dataroom_custom_links = []

        dataroom_overview_data = {
            'dataroom': data.get('id'),
            'send_daily_email_updates': True,
            'choose_overview_default_page': True,
            'hide_file_indexing':True,
            'user': request.user.id, 
            'dataroom_overview_heading':json.dumps(dataroom_overview_heading), 
            'dataroom_custom_links':json.dumps(dataroom_custom_links)
        }

        dataroom_overview_serializer = DataroomOverviewSerializer(data=dataroom_overview_data)
        print ("dataroom dataroom_overview_serializer", dataroom_overview_serializer.is_valid())
        print ("dataroom dataroom_overview_serializer erros", dataroom_overview_serializer.errors)
    
        if dataroom_overview_serializer.is_valid():
            dataroom_overview_serializer.save()
        return True

class DataroomAdmin:
    def __init__(self):
        print ("Create dataroom admin")

    def create_dataroom_admins(self, request, data):
        print ("create dataroom admins")
        user = request.user
        data = data
        is_user_existing = User.objects.filter(email__iexact=data.get('email')).exists()#.exist()
        #Condition 1 : if user is exist with particular email then skip the 
        #creating new admin functionality and only assign that particular 
        #email to datarooms
        new_data = {}
        if is_user_existing:
            user = User.objects.get(email__iexact=data.get('email'))
            return user, True, user
        else:
        #Condition 2 : 
            #step 1: if user does not exist with that particular 
            #email then create new dataroom admin and sent the password to user
            
            print ("add new user")
            "generate random pasword for user"

            password = User.objects.make_random_password() # 7Gjk2kd4T9
            password = User.objects.make_random_password(length=14) # FTELhrNFdRbSgy
            passwrod = User.objects.make_random_password(length=14, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889") # zvk0hawf8m6394
            #user.set_password(password)
                        
            #password = "Password1#"#User.objects.make_random_password(length=14, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
            data["password"] = password
            data["is_active"] = True
            data["is_staff"] = True
            data["is_end_user"] = True
            create_new_user_serializer = UserSerializer(data=data)
            if create_new_user_serializer.is_valid():
                create_new_user_serializer.save()
            #step 2:
            #send email to user
                user = User.objects.get(email__iexact = data.get("email"))
                return user, False, password


class DataroomUsageDetailsForGraph(APIView):
   authentication_classes = (TokenAuthentication, )
   permission_classes = (IsAuthenticated, )

   def get(self, request, pk,  format=None):
       print ("post method called")
       print ("primary key is", pk)
       from_date = request.GET.get('from_date')
       to_date = request.GET.get('to_date')
       print("-------", from_date, to_date)
       dataroom_storage = Dataroom.objects.get(pk=pk)
       import datetime
       if from_date == '' and to_date == '':
           dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk).aggregate(total_consumed_space = Sum('file_size'))
       else:
           todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
           first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
           dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date).aggregate(total_consumed_space = Sum('file_size'))
       dataroom_consumed = dataroom_consumed.get('total_consumed_space')
       document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False).count()
       print ("document count is ", document_count)
       print ("dataroom dataroom_consumed", dataroom_consumed)
       if document_count is None:
           document_count = 0
       if dataroom_consumed is None:
           dataroom_consumed = 0
       # total dataroom storage
       total_dataroom_storage  = dataroom_storage.dataroom_storage_allocated*1024 # all data in MBS
       dataroom_consumed = (dataroom_consumed/1024)/1024  # all data in mbs
       dataroom_free = total_dataroom_storage - dataroom_consumed
       data = {
           'total_dataroom_storage' : total_dataroom_storage, 
           'dataroom_consumed' : dataroom_consumed, 
           'dataroom_free'  : dataroom_free, 
           'document': document_count
       }

       print ("data is", data)
       storage = data['dataroom_consumed']
       # print("Storage", str(storage)[3])
       # if int(str(storage)[3]) < 5:
       #     data['dataroom_consumed'] = int(str(storage)[0:1])
       # else:
       #     storage = storage + 0.1
       data['dataroom_consumed'] = round(data['dataroom_consumed'],0)#int(str(storage)[0:1])
       data['dataroom_free'] = round(data['dataroom_free'],0)
       return Response(data=data, status=status.HTTP_201_CREATED)


class DownloadDataroomIndexReport(APIView):
    authentication_classes = ( TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user 
        print ("Download dataroom index report")
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="index_report.csv"'
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_Date')
        print("-------", from_date, to_date)
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

        writer = csv.writer(response)
        writer.writerow(['Index', 'Name', 'Type', 'Size(in MB)', 'Date Uploaded', 'Path'])
        root_folder_data = DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_root_folder=True, is_folder=True, created_date__gte=first_date, created_date__lte=todays_date).values('id', 'index', 'name', 'is_folder', 'file_size', 'created_date', 'path').order_by('index')
        for root_folder in root_folder_data:
            writer.writerow([root_folder.get('index'), root_folder.get('name'), root_folder.get('is_folder'), root_folder.get('file_size'), root_folder.get('created_date'), root_folder.get('path')])
        
            print ("root folder is", root_folder)

            sub_folder_list = DataroomFolder.objects.filter(parent_folder= root_folder.get('id'), is_deleted=False, is_root_folder=False).values('index', 'name', 'is_folder', 'file_size', 'created_date', 'path').order_by('index')
            #print ("root_folder dtaa", root_folder)
            print ("subfolder list count is", sub_folder_list.count())
            subfolder_index = str(root_folder.get('index'))
            if sub_folder_list.count() >0:
                self.recursively_add_indexes_for_files_and_folders(writer, subfolder_index, root_folder, sub_folder_list)     
            else:
                print ("no need to write row")
        index = IndexDownload()
        index.user_id  = user.id
        index.dataroom_id = pk
        index.save()
        return response

    def recursively_add_indexes_for_files_and_folders(self, writer, subfolder_index, root_folder, sub_folder_list):
        print ("recursively add indexes")
        #pdb.set_trace()
        sub_folder_list = DataroomFolder.objects.filter(parent_folder= root_folder.get('id'), is_deleted=False, is_root_folder=False).values('index', 'name', 'is_folder', 'file_size', 'created_date', 'path').order_by('index')
        #print ("root_folder dtaa", root_folder)
        print ("subfolder list count is", sub_folder_list.count())
        subfolder_index = str(root_folder.get('index'))
        if sub_folder_list.count() >0:
            # categorize  folder and files indexes

            #1 show only file indexes
            file_sub_folder_list = DataroomFolder.objects.filter(parent_folder= root_folder.get('id'), is_deleted=False, is_root_folder=False, is_folder=False).values('index', 'name', 'is_folder', 'file_size', 'created_date', 'path').order_by('index')#sub_folder_list#[folder for folder in sub_folder_list if folder.get("is_folder") == False]
            print ("file_sub_folder_list count", file_sub_folder_list)          
            if len(file_sub_folder_list) > 0:
                for file_sub in file_sub_folder_list:
                    subfolder_index = subfolder_index+"."+str(0)+"."+str(file_sub.get('index'))
                    writer.writerow([subfolder_index, file_sub.get('name'), file_sub.get('is_folder'), file_sub.get('file_size'), file_sub.get('created_date'), file_sub.get('path')])            
                    subfolder_index = str(root_folder.get('index'))
            else:
                print ("skip writing of row in csv")
                pass

            #2 show only folder indexes
            folder_sub_folder_list = DataroomFolder.objects.filter(parent_folder= root_folder.get('id'), is_deleted=False, is_root_folder=False, is_folder=True).values('index', 'name', 'is_folder', 'file_size', 'created_date', 'path').order_by('index')#[folder for folder in sub_folder_list if folder.get("is_folder") == False]
            #print ("folder_sub_folder_list", folder_sub_folder_list)
            if len(folder_sub_folder_list) > 0 :
                #print ("sub file list have elemenet")
                for sub_folder in folder_sub_folder_list:
                    subfolder_index = subfolder_index+"."+str(sub_folder.get('index'))
                    writer.writerow([subfolder_index, sub_folder.get('name'), sub_folder.get('is_folder'), sub_folder.get('file_size'), sub_folder.get('created_date'), sub_folder.get('path')])            
                    return self.recursively_add_indexes_for_files_and_folders(writer, subfolder_index, sub_folder, sub_folder_list)
            else:
                print ("skip writing of row in csv")
                pass
                #continue
        else:
            print ("no need to write row")
            pass
            #continue

class UploadNewContactCSV(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        print ("user_id is", user.id)
        file = request.FILES['csv_file'] 
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        #print ("reader data is", reader.__dict__)
        all_contacts = []
        for row in reader:
            row["user"] = user.id
            contact_serializer = ContactSerializer(data=row)
            print ("contact serializer", contact_serializer.is_valid())
            print ("contact errors", contact_serializer.errors)
            if contact_serializer.is_valid():
                contact_serializer.save()

        all_contacts = Contacts.objects.filter(user_id=user.id)
        all_contacts_serializer = ContactSerializer(all_contacts, many=True)
        return Response(all_contacts_serializer.data, status=status.HTTP_201_CREATED)

class DownloadSampleContactCsv(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        print ("donwload contact csv")
        user = request.user
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        writer = csv.writer(response)
        writer.writerow(['first_name', 'last_name', 'email'])
        writer.writerow(['John', 'Doe', 'john.doe@example.com'])

        return response

class GetDataroomContactApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        
        print ("dataroom id is", pk)
        contacts = Contacts.objects.filter(user_id=user.id, dataroom_id = pk)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CreateDataroomContactApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def post(self, request, format=None):
        print ("post method called")
        user = request.user
        new_data = request.data
        print ("request data is ", new_data)
        data = new_data.get('contact')
        user = request.user
        data["user"] = user.id
        data["dataroom"] = new_data.get('dataroom')#
        serializer = ContactSerializer(data=data)
        print ("serializer", serializer.is_valid())
        print ("serializer", serializer.errors)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status= status.HTTP_201_CREATED)

#Write new api rajendra for disply graph
from collections import OrderedDict
class GetDataroomUsageApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = request.user
        datarooms = []
        if user.is_superadmin:
            datarooms = Dataroom.objects.filter(user_id = user.id)
        elif user.is_admin:
            my_team_ids = [team.myteam.id for team in TeamMembers.objects.filter(member_id=user.id)]
            print ("my team ids ", my_team_ids)
            datarooms = Dataroom.objects.filter(my_team_id__in = my_team_ids)
        elif user.is_end_user:
            dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id)]
            print ("dataroom ids", dataroom_ids)
            datarooms = Dataroom.objects.filter(id__in=dataroom_ids)
        # print ("datarooms are", serializer.data)
        storage = [{
            'name': 'Storage',
            'data': []
        }]
        document = [
            # {'name': 'Proprietary or Undetectable','y': 0.2,'dataLabels': {'enabled': False}}
        ]
        for dataroom in datarooms:
            if dataroom:
                for stor in storage:
                    stor['data'].append({'name': dataroom.dataroom_name, 'y': dataroom.dataroom_storage_allocated})
                    dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom.id).aggregate(total_consumed_space = Sum('file_size')).get('total_consumed_space')

                    if dataroom_consumed is None:
                        dataroom_consumed = 0
                    dataroom_consumed = round(((dataroom_consumed/1024)/1024),0)  # all data in mbs

                    print("Dataroom Consumedddddddddddddddddd", dataroom_consumed)
                    document.append([dataroom.dataroom_name, dataroom_consumed])
        # [{name: 'Storage', data: [{name: 'Microsoft Internet Explorer',y: 56.33}]
        # data_dict = json.loads(json.dumps(serializer.data))
        return Response({'storage': storage, 'document': document}, status=status.HTTP_201_CREATED)

class GetDataroomViewed(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroom_obj = DataroomView()
        dataroom_obj.dataroom_id = pk
        dataroom_obj.user_id = user.id
        dataroom_obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class getBarChartDataroomViews(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        data={}
        user  = request.user
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        import datetime
        todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d')
        first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d')
        print("FROMDATE", first_date, type(first_date), "TODATE", todays_date, type(todays_date))
        from . import utils
        dataroom = DataroomView.objects.filter(dataroom_id=pk)
        data = utils.getStartEndDateofWeek(dataroom, first_date, todays_date)
        return Response(data,status=status.HTTP_201_CREATED)


class GetDetaroomAllUsers(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        users_id = []
        data = []
        dataroom_obj = DataroomMembers.objects.filter(dataroom_id=pk)
        for dataroom in dataroom_obj:
            # users_id.append(dataroom.member_id)
            # for user in users_id:
                # users = User.objects.filter(id__in=users_id)
            # DataroomGroups.objects.filter()
            users = User.objects.filter(id=dataroom.member_id).first()
            serializer = UserSerializer(users,)
            usr_data = serializer.data
            usr_data['is_dataroom_admin'] = dataroom.is_dataroom_admin
            usr_data['is_la_user'] = dataroom.is_la_user
            usr_data['is_end_user'] = dataroom.is_end_user
            try:
                usr_data['group_name'] = []
                for each in dataroom.end_user_group.all():
                    # import pdb;pdb.set_trace();
                    usr_data['group_name'].append(each.group_name)
            except:
                usr_data['group_name'] = ""
            data.append(usr_data)
        return Response(data, status=status.HTTP_201_CREATED)


class WatermarkingSettings(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        watermarking = Watermarking.objects.filter(dataroom_id=pk).order_by('id')
        serializer = WatermarkingSerializer(watermarking,many=True)
        data = serializer.data
        for da in data:
            watermark_obj = Watermarking.objects.get(id = int(da.get('id')))
            if watermark_obj.attachments:
                da['attachments'] = watermark_obj.attachments.url
            else:
                da['attachments'] = ''
        return Response(data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        user = request.user
        data = request.data
        for da in data:
            da['user'] = user.id
            da['dataroom'] = pk
            serializer = WatermarkingSerializer(data=da)
            print ("serializer", serializer.is_valid())
            print ("serializer", serializer.errors)
            if serializer.is_valid():
                serializer.save()
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
        from userauth import utils
        ip = utils.get_client_ip(request)
        watermarking = Watermarking.objects.filter(dataroom_id=pk)
        dataroom_utils.WatermarkingImage(watermarking, ip)
        return Response({'msg':'Watermarking Setting Update successfully'},status=status.HTTP_201_CREATED)

class UpdateWatermarkingSettings(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, format=None):
        user = request.user
        data = request.data
        for da in data:
            dataroom = da.get('dataroom')
            watermarking = Watermarking.objects.get(id=int(da.get('id')))
            serializer = WatermarkingSerializer(watermarking, data=da)
            print ("serializer", serializer.is_valid())
            print ("serializer", serializer.errors)
            if serializer.is_valid():
                serializer.save()
        from userauth import utils
        ip = utils.get_client_ip(request)
        watermarking = Watermarking.objects.filter(dataroom_id=dataroom)
        dataroom_utils.WatermarkingImage(watermarking, ip)
        return Response({'msg':'Watermarking Setting Update successfully'},status=status.HTTP_201_CREATED)


class DataroomDisclaimerApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, pk, format=None):
        print ("get method called", pk)
        user = request.user
        data = request.data
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk)
        dataroom_disclaimer_serilizer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        print ("dataroom_disclaimer_serilizer data", dataroom_disclaimer_serilizer.data)
        return Response(dataroom_disclaimer_serilizer.data)


class MakeMultipleDisclaimersOverview(APIView):
    """docstring for DataroomOverviewAll"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DataroomOverviewSerializer

    
    def put(self, request, format=None):
        data = request.data
        user = request.user
        data["user"] = user.id
        # print("dataaaaaaaaaa",data)
        dataroom_overview = DataroomOverview.objects.get(id= data.get("id"))
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, data=data)
        if dataroom_overview_serializer.is_valid():
            dataroom_overview_serializer.save()
            data = dataroom_overview_serializer.data
            if data.get('show_multiple_times_disclaimer') == True:
                DataroomMembers.objects.filter(dataroom_id = data.get('dataroom_id')).update(disclaimer_status=False)
            return Response(dataroom_overview_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetDataroomDisclaimer(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        data = {}
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk, is_dataroom_disclaimer_default=True).first()
        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        data['disclaimer'] = dataroom_disclaimer_serializer.data

        dataroom_member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).first()
        print("DataroomOverviewApi--------", dataroom_member)
        if dataroom_member == None:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data
            data['member']['disclaimer_status'] = None
        else:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data

        dataroom_overview = DataroomOverview.objects.filter(dataroom_id=pk).first()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        data['overview'] = dataroom_overview_serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        user = request.user
        print("user", user.id, pk)
        member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).update(disclaimer_status=True)
        print("Members", member)
        dataroom_overview = DataroomOverview.objects.filter(dataroom_id=pk).first()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        return Response(dataroom_overview_serializer.data, status=status.HTTP_201_CREATED)

class ArchiveDataroom(APIView):
    """docstring for ArchiveDataroom"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        data = {}
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk, is_dataroom_disclaimer_default=True).first()
        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        data['disclaimer'] = dataroom_disclaimer_serializer.data

        dataroom_member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).first()
        print("DataroomOverviewApi--------", dataroom_member)
        if dataroom_member == None:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data
            data['member']['disclaimer_status'] = None
        else:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data

        dataroom_overview = DataroomOverview.objects.filter(dataroom_id=pk).first()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        data['overview'] = dataroom_overview_serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

        

