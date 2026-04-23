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
from decimal import Decimal
from azure.storage.blob import (BlockBlobService,ContainerPermissions,ContentSettings,BlobPermissions,PublicAccess,)
# from azure.storage.blob import (BlobServiceClient as BlockBlobService,ContainerClient as ContainerPermissions,ContentSettings,BlobSasPermissions as BlobPermissions,PublicAccess,)
from rest_framework import permissions
from userauth.models import TokenAuthentication,Token
# from rest_framework.authtoken.models import Token
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FileUploadParser
from django.core.mail import send_mail
from random import randint
from dms.settings import *
from dms.settings import sas_url

from userauth.serializers import UserSerializer, AccessHistorySerializer
from userauth import constants, utils
from userauth.models import Profile, AccessHistory, User, InviteUser,planinvoiceuserwise
from . import utils as dataroom_utils

from .serializers import DataroomSerializer, DataroomdashboardSerializer,DataroomOverviewSerializer,DataroomModulesSerializer, ContactSerializer,DataroomDisclaimerSerializer,ContactGroupSerializer, ContactGroupMembersSerializer ,DataroomDisclaimerSerializerupload,DataroomSerializertwo
from .models import Dataroom, DataroomOverview, Contacts, DataroomDisclaimer, \
    ContactGroup, ContactGroupMembers, DataroomView, DataroomModules, Watermarking,dataroomProLiteFeatures

from myteams.models import MyTeams, TeamMembers
from qna.models import QuestionAnswer
# import data_documents module 
from data_documents.models import *

from myteams.serializers import MyTeamsSerializer
from users_and_permission.models import DataroomMembers, DataroomGroups,DataroomGroupPermission,DataroomGroupFolderSpecificPermissions
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
from django.db.models import Q
from notifications.models import AllNotifications


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

class UpdateAddon(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):

        # if 'dataroom_id' in request.GET:
        #     objects = Dataroom.objects.filter(id=request.GET['dataroom_id']).first()
        #     size = DataroomSerializer(objects, many=False).data.get('dataroom_storage_allocated')
        #     print(size)
        #     dataroom = Dataroom.objects.get(id=request.GET['dataroom_id'])
        #     dataroom.dataroom_storage_allocated = float(size)+float(request.GET['dataroom_storage_allocated'])
        #     dataroom.save()

        if 'dataroom_allowed' in request.GET:
            team = MyTeams.objects.filter(id=request.GET['team_id']).first()
            myTeams = MyTeamsSerializer(team, many=False).data
            if myTeams:
                dataroom_allowed = myTeams.get('dataroom_allowed')
                dataroom_storage_allowed = myTeams.get('dataroom_storage_allowed')
                team = MyTeams.objects.get(id=request.GET['team_id'])
                
                team.dataroom_allowed = int(dataroom_allowed)+int(request.GET['dataroom_allowed'])

                team.dataroom_storage_allowed = float(dataroom_storage_allowed)+float(request.GET['dataroom_storage_allocated'])
                # print(dataroom_allowed, request.GET['dataroom_allowed'], dataroom_storage_allowed, request.GET['dataroom_storage_allocated'])
                team.save()

        return Response([], status=status.HTTP_201_CREATED)

class CloneDataroomApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        data = {}
        user = request.user
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$',request.data)
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
        data['is_dataroom_cloned']=True     
        data['dataroom_cloned_from']=request.data['dataroom']
        data['my_team']=    request.data['myteam']
        data['is_paid']=True
        # print(data['my_team_id'],data['dataroom_cloned_from_id'],'))))))))))))))))))))))')
        dataroom_admin_data = data.get('dataroom_admin')
        serializer = DataroomSerializer(data=data, context={'dataroom_modules': data.get("dataroom_modules")})        
        if serializer.is_valid():
            serializer.save()
            # print('2222222222222222222222222222')

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
                        # print ("clone_data_id:-", clone_data_id)
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
                        admin_user = User.objects.filter(email=data['dataroom_admin']['email']).first()
                        if admin_user:
                            obj, created = DataroomMembers.objects.get_or_create(dataroom_id=serializer.data['id'], member_id=admin_user.id,member_added_by_id=user.id)
                            obj.is_dataroom_admin = True
                            obj.save()
                        # send email to the dataroom member
                        if is_exist_user:
                            # print ("is_exist_user", is_exist_user)
                            # print ("send email to already exist should called")
                            dataroom_utils.send_email_to_already_exist_admin_or_end_user(dataroom_admin, serializer.data,  subject = "Welcome to DocullyVDR")
                            # print ("Email sucessfully send")
                        else:
                            # print ("is_exist_user", is_exist_user)
                            # print ("create new user send password method should called")
                            dataroom_utils.send_password_to_dataroom_admin_or_end_user(dataroom_admin , serializer.data, __dataroom_admin_password , subject = "Welcome to DocullyVDR" )                     
                            # print ("Email successfully send")
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                # update the dataroom_members table 
            return Response({"errors":'Error in creating nested data'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
        
from Vote.models import Vote
class DataroomApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = request.user
        datarooms = []
        # if user.is_superadmin:
        #     dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id, is_deleted=False)]
        #     print ("dataroom ids", dataroom_ids)
        #     datarooms = Dataroom.objects.filter(id__in=dataroom_ids)
        # elif user.is_admin:
        #     dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id, is_deleted=False)]
        #     # print ("dataroom ids", dataroom_ids)
        #     datarooms = Dataroom.objects.filter(id__in=dataroom_ids)

        #     # my_team_ids = [team.myteam.id for team in TeamMembers.objects.filter(member_id=user.id)]
        #     # print ("my team ids ", my_team_ids)
        #     # datarooms = Dataroom.objects.filter(my_team_id__in = my_team_ids)
        # elif user.is_end_user:
        # print("dataroom / view / dataroomApi is called ")
        dataroom_ids1 = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id, is_deleted=False,end_user_group__in=[a.id for a in DataroomGroups.objects.filter()]).order_by('-event_timestamp')]
        # dataroom_ids =dataroom_ids.append([dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id, is_deleted=False).order_by('-event_timestamp')])
        dataroom_ids2 = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id, is_deleted=False,is_dataroom_admin=True).order_by('-event_timestamp')]
        # print(dataroom_ids1,'----------------',request.user.id)
        # print(dataroom_ids2,'----------------')
        dataroom_ids=dataroom_ids1+dataroom_ids2
        # print(dataroom_ids,'=============')
        datarooms = Dataroom.objects.filter(id__in=dataroom_ids,is_deleted=False).order_by('-event_timestamp')
        print(request.session.get('id'),'11111111111')
        # invitation_ids = [i.dataroom_invitation for i in InviteUser.objects.filter(invitiation_receiver_id=user.id,is_invitation_accepted=True,is_invitation_expired=False,is_shifted=False)]     
        # import copy
        # if len(invitation_ids) > 0:
        #   new_change_list = copy.deepcopy(dataroom_ids)
        #   for i in new_change_list:
        #       if i in invitation_ids:
        #           index_no = new_change_list.index(i)
        #           new_change_list.pop(index_no)

        #   reverse_list = new_change_list[::-1]
        #   for i in invitation_ids:
        #       reverse_list.append(i)

        #   dataroom_ids = reverse_list[::-1]
        # else:
        #   pass
        serializer = DataroomdashboardSerializer(datarooms, many=True)
        data = serializer.data
        for da in data:
            # for i in dataroom_ids:
                # if dataroom_ids == int(da['id']):
                #   da['sort_condition'] = dataroom_ids.index(i)
                print(da['id'],da['dataroom_nameFront'],da['user'],'000000000')
                da['document_count'] = DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=False,is_deleted_permanent=False, is_folder=False).count()
                dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=False,is_root_folder=False ,is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=False, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                print('------111',dataroom_consumed)
                trash_consumed = round((DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=True,is_root_folder=False, is_folder=False,is_deleted_permanent=False ).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=da['id'], is_deleted=True, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                print('------22',dataroom_consumed)
                vote_consumed = round((Vote.objects.filter(dataroom_id=da['id'],is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=da['id'],is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                print('------33',dataroom_consumed)
                disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=da['id']).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=da['id']).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                print('------111',dataroom_consumed)
                if int(dataroom_consumed)<dataroom_consumed:
                       dataroom_consumed=int(dataroom_consumed)+1   
                if int(trash_consumed)<trash_consumed:
                       trash_consumed=int(trash_consumed)+1 
                if int(vote_consumed)<vote_consumed:
                       vote_consumed=int(vote_consumed)+1   
                if int(disclaimer_consumed)<disclaimer_consumed:
                       disclaimer_consumed=int(disclaimer_consumed)+1   
                tempvar11 = dataroom_consumed+trash_consumed+vote_consumed+disclaimer_consumed
                if int(tempvar11)<tempvar11:
                    tempvar11=int(tempvar11)+1
                if int(tempvar11)==0 and tempvar11>0:
                    tempvar11=1
                tempvar11=tempvar11/1024
                format_float = "{:.2f}".format(tempvar11)
                da['storage_size']= format_float        
                
                da_over = DataroomOverview.objects.filter(dataroom_id=da['id'],).first()
                # da['send_daily_email_updates'] = da_over.send_daily_email_updates
                da['choose_overview_default_page'] = da_over.choose_overview_default_page
                # da['hide_file_indexing'] = da_over.hide_file_indexing
                da['member'] = DataroomMembers.objects.filter(dataroom_id=da.get('id'), member_id=user.id).values().last()
                is_active_group = DataroomMembers.objects.filter(dataroom_id=da.get('id'), member_id=user.id).first()
                if is_active_group.end_user_group.last():
                    # for i in is_active_group.end_user_group.all():
                    # print('---------------',is_active_group.end_user_group.last().is_active)
                    da['is_active_group'] = is_active_group.end_user_group.last().is_active
                
                # da['subscription_flag'] = planinvoiceuserwise.objects.filter(user_id=user.id,dataroom_id=da['id'],is_latest_invoice=True).exists()
                # from . import utils
                # diff, expiry_date = utils.date_difference(da.get('created_date'))
                # if diff > da.get('trial_days'):
                #   if da.get('trial_expired') == False:
                #       dataroom = Dataroom.objects.get(id=da.get('id'))
                #       dataroom.trial_expired = True
                #       dataroom.is_expired = True
                #       dataroom.trial_expiry_date = expiry_date
                #       dataroom.is_dataroom_on_live = False
                #       dataroom.save()
                date_list=[]
                if DataroomFolder.objects.filter(dataroom_id=da['id']).exists():
                    file=DataroomFolder.objects.filter(dataroom_id=da['id']).order_by('updated_date').last()
                    date_list.append(file.updated_date)

                if FolderTrash.objects.filter(dataroom_id=da['id']).exists():
                    trash=FolderTrash.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(trash.created_date)
                
                if FolderView.objects.filter(dataroom_id=da['id']).exists():
                    view=FolderView.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(view.created_date)

                if BulkActivityTracker.objects.filter(dataroom_id=da['id']).exists():
                    bulk=BulkActivityTracker.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(bulk.created_date)

                if FolderDownload.objects.filter(dataroom_id=da['id']).exists():
                    download=FolderDownload.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(download.created_date)

                if FolderDrmDownload.objects.filter(dataroom_id=da['id']).exists():
                    print1=FolderDrmDownload.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(print1.created_date)

                if FolderDeleteDownload.objects.filter(dataroom_id=da['id']).exists():
                    delete_down=FolderDeleteDownload.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(delete_down.created_date)

                if FolderOrFileCopy.objects.filter(dataroom_id=da['id']).exists():
                    copy=FolderOrFileCopy.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(copy.created_date)

                if FolderOrFileMove.objects.filter(dataroom_id=da['id']).exists():
                    move=FolderOrFileMove.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(move.created_date)

                if RestoreFiles.objects.filter(dataroom_id=da['id']).exists():
                    restore=RestoreFiles.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(restore.created_date)

                if Vote.objects.filter(dataroom_id=da['id']).exists():
                    vote=Vote.objects.filter(dataroom_id=da['id']).order_by('vote_updated').last()
                    date_list.append(vote.vote_updated)

                if QuestionAnswer.objects.filter(dataroom_id=da['id']).exists():
                    qaa=QuestionAnswer.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(qaa.created_date)

                if DataroomMembers.objects.filter(dataroom_id=da['id']).exists():
                    member = DataroomMembers.objects.filter(dataroom_id=da['id']).order_by('date_updated').last()
                    date_list.append(member.date_updated)

                if DataroomView.objects.filter(dataroom_id=da['id']).exists():
                    data_view = DataroomView.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(data_view.created_date)

                if RedactorVersion.objects.filter(dataroom_id=da['id']).exists():
                    redact_=RedactorVersion.objects.filter(dataroom_id=da['id']).order_by('created_date').last()
                    date_list.append(redact_.created_date)

                # date_list=[,,view.created_date,bulk.created_date,download.created_date,
                # print1.created_date,delete_down.created_date,copy.created_date,move.created_date,
                #restore.created_date,vote.vote_updated,qaa.created_date]

                test_date=datetime.datetime.now()

                print('----------------------soreted lisy11111',date_list)
                sorted_list = sorted(date_list)
                print('----------------------soreted lisy',sorted_list)
                if len(sorted_list)>0:
                    da['last_updated'] = sorted_list[-1]
                else:
                    da['last_updated'] = None
                # for date in sorted_list:
                #     if date >= test_date:
                #         if abs((date - test_date).days) < abs((previous_date - test_date).days):
                #             print('------------------++++++@@@@@@@@@@@',date) 
                #         else:
                #             # return previous_date
                #             print('------------------++++++@@@@@@@@@@@previous_date',previous_date) 
                #     previous_date = date
                # print("----------------lasttt****************", sorted_list[-1])







        ########
        # print("value check --->",data)
        # dataroom_qs = []
        # print("all id sorted -->",dataroom_ids)
        # for i in dataroom_ids:
        #   dataroom_qs.append(Dataroom.objects.filter(id=i).values())

        

        # for da in dataroom_qs:
        #   da[0]['document_count'] = DataroomFolder.objects.filter(dataroom_id=da[0]['id'], is_deleted=False, is_folder=False).count()
        #   da[0]['storage_size'] = round((DataroomFolder.objects.filter(dataroom_id=da[0]['id'], is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=da[0]['id'], is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
                                    
        #   da_over = DataroomOverview.objects.filter(dataroom_id=da[0]['id'],).first()
        #   da[0]['send_daily_email_updates'] = da_over.send_daily_email_updates
        #   da[0]['choose_overview_default_page'] = da_over.choose_overview_default_page
        #   da[0]['hide_file_indexing'] = da_over.hide_file_indexing
        #   da[0]['member'] = DataroomMembersSerializer(DataroomMembers.objects.filter(dataroom_id=da[0]['id'], member_id=user.id).first(),many=False).data
        #   from . import utils
        #   diff, expiry_date = utils.date_difference_new(str(da[0]['created_date']))
        #   if diff > da[0]['trial_days']:
        #       if da[0]['trial_days'] == False:
        #           dataroom = Dataroom.objects.get(id=da[0]['id'])
        #           dataroom.trial_expired = True
        #           dataroom.is_expired = True
        #           dataroom.trial_expiry_date = expiry_date
        #           dataroom.is_dataroom_on_live = False
        #           dataroom.save()

        # print(type(dataroom_qs),"=====",len(dataroom_qs))

        data = sorted(data, key=lambda k: k['event_timestamp'])
        count=len(data)
        return Response({'data':data,'size':count} , status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        data = request.data
        user = request.user
        data["user"] = user.id
        # print ("data is", data)

        dataroom_admin_data = data.get('dataroom_admin')
        if dataroomProLiteFeatures.objects.filter(dataroom_id=data['id']).exists():
            dataroomProLiteFeatures.objects.filter(dataroom_id=data['id']).update(dataroom_id=data['id'],
            custom_watermarking=data['dataroom_features']['custom_watermarking'],
            two_factor_auth=data['dataroom_features']['two_factor_auth'],
            proj_overview=data['dataroom_features']['proj_overview'],
            proj_video_intro=data['dataroom_features']['proj_video_intro'],
            custom_logo=data['dataroom_features']['custom_logo'],
            custom_external_link=data['dataroom_features']['custom_external_link'],
            email_to_dataroom_upload=data['dataroom_features']['email_to_dataroom_upload'],
            google_drive_upload=data['dataroom_features']['google_drive_upload'],
            one_drive_upload=data['dataroom_features']['one_drive_upload'],
            sharepoint_upload=data['dataroom_features']['sharepoint_upload'],
            dropbox_upload=data['dataroom_features']['dropbox_upload'],
            favourites=data['dataroom_features']['favourites'],
            redaction=data['dataroom_features']['redaction'],
            la_admin_access=data['dataroom_features']['la_admin_access'],
            bulk_users_upload=data['dataroom_features']['bulk_users_upload'],
            doculink_perm=data['dataroom_features']['doculink_perm'],
            auto_expire=data['dataroom_features']['auto_expire'],
            module_perm=data['dataroom_features']['module_perm'],
            qa_with_cat=data['dataroom_features']['qa_with_cat'],
            qa_submit=data['dataroom_features']['qa_submit'],
            desktop_unlimit_upload=data['dataroom_features']['desktop_unlimit_upload'],
            proj_management=data['dataroom_features']['proj_management'],
            voting_perm=data['dataroom_features']['voting_perm'],
            proj_updates=data['dataroom_features']['proj_updates'],
            country_perm=data['dataroom_features']['country_perm'])
        else:
            dataroomProLiteFeatures.objects.create(dataroom_id=data['id'],
            custom_watermarking=data['dataroom_features']['custom_watermarking'],
            two_factor_auth=data['dataroom_features']['two_factor_auth'],
            proj_overview=data['dataroom_features']['proj_overview'],
            proj_video_intro=data['dataroom_features']['proj_video_intro'],
            custom_logo=data['dataroom_features']['custom_logo'],
            custom_external_link=data['dataroom_features']['custom_external_link'],
            email_to_dataroom_upload=data['dataroom_features']['email_to_dataroom_upload'],
            google_drive_upload=data['dataroom_features']['google_drive_upload'],
            one_drive_upload=data['dataroom_features']['one_drive_upload'],
            sharepoint_upload=data['dataroom_features']['sharepoint_upload'],
            dropbox_upload=data['dataroom_features']['dropbox_upload'],
            favourites=data['dataroom_features']['favourites'],
            redaction=data['dataroom_features']['redaction'],
            la_admin_access=data['dataroom_features']['la_admin_access'],
            bulk_users_upload=data['dataroom_features']['bulk_users_upload'],
            doculink_perm=data['dataroom_features']['doculink_perm'],
            auto_expire=data['dataroom_features']['auto_expire'],
            module_perm=data['dataroom_features']['module_perm'],
            qa_with_cat=data['dataroom_features']['qa_with_cat'],
            qa_submit=data['dataroom_features']['qa_submit'],
            desktop_unlimit_upload=data['dataroom_features']['desktop_unlimit_upload'],
            proj_management=data['dataroom_features']['proj_management'],
            voting_perm=data['dataroom_features']['voting_perm'],
            proj_updates=data['dataroom_features']['proj_updates'],
            country_perm=data['dataroom_features']['country_perm'])

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
                        dataroom_utils.send_email_to_already_exist_admin_or_end_user(dataroom_admin, serializer.data,  subject = "Welcome to DocullyVDR")
                        # print ("Email sucessfully send")
                    else:
                        # print ("is_exist_user", is_exist_user)
                        # print ("create new user send password method should called")
                        dataroom_utils.send_password_to_dataroom_admin_or_end_user(dataroom_admin , serializer.data, __dataroom_admin_password , subject = "Welcome to DocullyVDR" )                     
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
        # print("dataroom / view / dataroomfolderapi get is called ")

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
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
        user=request.user
        dataroom = self.get_object(pk, request)
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        if dataroompermission==False:
            serializer = DataroomSerializer(dataroom)
            data = serializer.data
            dataroom_memmm = DataroomMembers.objects.filter(dataroom_id=int(pk),is_deleted=False,member_id=user.id).first()
            if dataroom_memmm:
                if dataroom_memmm.memberactivestatus==False:
                    dataroom_memmm.memberactivestatus=True
                    dataroom_memmm.save()
            dataroom_mem = DataroomMembers.objects.filter(dataroom_id=int(pk), is_dataroom_admin=True, is_primary_user=True).first()
            serializer = DataroomMembersSerializer(dataroom_mem, many=False)
            # print ("Here add admin data date")
            # print("====================================================================")
            # print("dataroom /view/ dataroom details / get method is called ")
            if InviteUser.objects.filter(invitiation_receiver_id=user.id,dataroom_invitation=pk).exists():
                invitationdata=InviteUser.objects.filter(invitiation_receiver_id=user.id,dataroom_invitation=pk).last()
                if invitationdata.is_invitation_accepted==False:
                    invitationdata.invitation_status_id=3
                    invitationdata.is_invitation_accepted=True
                    invitationdata.is_invitation_expired=False
                    invitationdata.invitatation_acceptance_date=datetime.datetime.now()
                    invitationdata.save()
            if dataroom_mem:
                data['dataroom_admin_data'] = serializer.data
                data['is_primary_user'] = True
                # print("========================================================is_primary_user True")
            else:
                data['is_primary_user'] = False
                # print("========================================================is_primary_user False")
            # data['modules'] = DataroomModules.objects.filter(id=data['dataroom_modules']).first()
            # SAS token already appended by serializer
            print('------------------------------picccccc',dataroom.dataroom_logo.url)
            da_over = DataroomOverview.objects.filter(dataroom_id=pk).last()
            data['hide_file_indexing'] = da_over.hide_file_indexing
            
            return Response(data)

            # return Response({'dataroomaccesscheck': 'access', 'data': data})
        else:
            return Response({'dataroomaccesscheck': 'noaccess'})



    def put(self, request, pk, format=None):
        data = request.data
        from decimal import Decimal
        dataroom = self.get_object(pk, request)
        dataroom_storage = Dataroom.objects.filter(my_team=dataroom.my_team).exclude(id=pk).aggregate(Sum('dataroom_storage_allocated')).get('dataroom_storage_allocated__sum') 
        dataroom_storage = dataroom_storage + Decimal(data.get('dataroom_storage_allocated')) if dataroom_storage != None else Decimal(0.00)  + Decimal(data.get('dataroom_storage_allocated'))
        myteams = MyTeams.objects.get(id=dataroom.my_team_id)
        del data["dataroom_logo"]
        # print("dataroom_storage", dataroom_storage, 'My Teams Storage allowed', myteams.dataroom_storage_allowed)
        if dataroom_storage <= myteams.dataroom_storage_allowed:
            serializer = DataroomSerializer(dataroom, data=data)
            # print ("serializer is valid", serializer.is_valid())
            # print ("serializer errors ", serializer.errors)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response({'error':serializer.errors, 'success':False}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':'Dataroom Storage limit exceed!!', 'success':False}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk, format=None):
        dataroom = self.get_object(pk, request)
        maillist=[]
        member=DataroomMembers.objects.filter(dataroom_id=pk,is_dataroom_admin=True,is_deleted=False,memberactivestatus=True)
        member2=DataroomMembers.objects.filter(dataroom_id=pk,is_la_user=True,is_deleted=False,memberactivestatus=True) 
        # for j in member2:
        #     # group_perm = DataroomGroupPermission.objects.filter(dataroom_groups_id=j.end_user_group.first().id,dataroom=pk).last().is_overview
        #     # if group_perm==True:
        #     maillist.append(j.member.email)

    
        # for i in member:
        #     maillist.append(i.member.email)

        if dataroom.is_request_for_deletion== True:
            dataroom.delete_request_at=None
            dataroom.is_request_for_deletion= False
            dataroom.save()
            dataroom_serializer = DataroomSerializer(dataroom, many=False)
            emailer_utils.send_deletion_dataroom_cancel_email(dataroom, request.user,maillist)
        else:
            dataroom.is_request_for_deletion = True 
            dataroom.delete_request_at=datetime.datetime.now()
            dataroom.is_dataroom_on_live=False
            dataroom.save()
            dataroom_serializer = DataroomSerializer(dataroom, many=False)
            emailer_utils.send_deletion_dataroom_email(dataroom, request.user,maillist)

        # print(dataroom_serializer.data['delete_request_at'],'OOOOOOOOOOOOOOOOOOOOOOOOOO')
        return Response(dataroom_serializer.data, status=status.HTTP_201_CREATED)

        
    def post(self, request, pk, format=None):
        # print('y8787',request.data,'7878')
        if request.data:
            dataroom = Dataroom.objects.get(id=request.data['id'])
            dataroom.dataroom_nameFront = request.data['dataroom_name']
            dataroom.is_dataroom_on_live = request.data['is_dataroom_on_live']

            dataroom.save()
            # print(dataroom)

        return Response(status=status.HTTP_204_NO_CONTENT)



class DataroomFeatures(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request,pk,format=None):
        data=dataroomProLiteFeatures.objects.filter(dataroom_id=pk)
        if data:
            if data.last().dataroom.dataroom_version =="Pro":
                data={}
            else:
                data=data.values()
        else:
            data={}
        return Response(data,status=status.HTTP_201_CREATED)


    def post(self,request,pk,format=None):
        data = request.data
        
        return Response(status=status.HTTP_201_CREATED)




class DataroomOverviewApi(APIView):
    """docstring for DataroomOverviewAll"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DataroomOverviewSerializer
    
    def get(self, request, format=None):
        user = request.user
        # print("dataroom /view/ dataroom overview Api / get method is called ")

        datarooms_overview = DataroomOverview.objects.filter(user_id = user.id)
        serializer = DataroomOverviewSerializer(datarooms_overview, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def post(self, request, format=None):
        data = request.data
        user = request.user
        data["user"] = user.id
        # print("dataaaaaaaaaa",data)
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
            return Dataroom.objects.get(id=pk)
        except Dataroom.DoesNotExist:
            raise Http404


    def delete(self, request, pk, format=None):
        dataroom = self.get_object(pk, request)
        maillist=[]
        member=DataroomMembers.objects.filter(dataroom_id=pk,is_dataroom_admin=True, is_deleted=False,memberactivestatus=True)
        member2=DataroomMembers.objects.filter(dataroom_id=pk,is_la_user=True,is_deleted=False,memberactivestatus=True) 
        for j in member2:
            # group_perm = DataroomGroupPermission.objects.filter(dataroom_groups_id=j.end_user_group.first().id,dataroom=pk).last().is_overview
            # if group_perm==True:
            maillist.append(j.member.email)

        for i in member:
            maillist.append(i.member.email)
        if dataroom.is_request_for_archive == True:
            dataroom.is_request_for_archive = False
            dataroom.save()
            dataroom_serializer = DataroomSerializer(dataroom, many=False)
            emailer_utils.send_archive_dataroom_cancel_email(dataroom, request.user,maillist)

        else:
            dataroom.is_request_for_archive = True
            dataroom.save()
            dataroom_serializer = DataroomSerializer(dataroom, many=False)      
            emailer_utils.send_archive_dataroom_email(dataroom, request.user,maillist)
        return Response(dataroom_serializer.data, status=status.HTTP_201_CREATED)

    # def get(self, request, pk, format=None):
    #   dataroom = self.get_object(pk, request)
    #   dataroom.is_request_for_archive = False
    #   dataroom.save()
    #   maillist=[]
    #   member=DataroomMembers.objects.filter(dataroom_id=pk,is_dataroom_admin=True,is_deleted=False)
    #   for i in member:
    #       maillist.append(i.member.email)
    #   dataroom_serializer = DataroomSerializer(dataroom, many=False)
    #   emailer_utils.send_archive_dataroom_cancel_email(dataroom, request.user,maillist)
    #   return Response(dataroom_serializer.data, status=status.HTTP_201_CREATED)


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


    # def get(self, request, pk, format=None):
    #   # Change the dataroom api status 
    #   dataroom = self.get_object(pk, request)
    #   dataroom.is_request_for_deletion = False 
    #   dataroom.save()
    #   maillist=[]
    #   member=DataroomMembers.objects.filter(dataroom_id=pk,is_dataroom_admin=True,is_deleted=False)
    #   for i in member:
    #       maillist.append(i.member.email)
    #   dataroom_serializer = DataroomSerializer(dataroom, many=False)
    #   #send email to Super admin that we have recived the request for deletaion of dataroom
    #   emailer_utils.send_deletion_dataroom_cancel_email(dataroom, request.user,maillist)
    #   return Response(dataroom_serializer.data, status=status.HTTP_204_NO_CONTENT)

class UpdateDataroomOverviewSettingApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        # print ("pk is", pk)
        data = request.data
        user = request.user
        dataroom = Dataroom.objects.get(id=pk)
        data["dataroom"] = dataroom.id
        # print ("data is ", data)
        # print ("dataroom overview id is:", )
        data["user"] = user.id
        # overview_links_data = data.get('overview_links')
        # overview_headings_data = data.get('overview_headings')
        # print ("pk is:", pk)
        # print ("data is:", data)
        # print ("user is:", user.email)
        # print ("overview_links_data", overview_links_data)
        # print ("overview_headings_data", overview_headings_data)
        dataroom_overview_update = DataroomOverview.objects.filter(id=data.get("id")).update(send_daily_email_updates=data.get("send_daily_email_updates"),choose_overview_default_page=data.get("choose_overview_default_page"),hide_file_indexing=data.get("hide_file_indexing"),dataroom=data.get("dataroom"))
        dataroom_overview = DataroomOverview.objects.get(id=data.get("id"))
        del data["change_video_ppt"]
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, data=data)
        
        # print ("dataroom_overview_serializer.isvalid", dataroom_overview_serializer.is_valid())
        # print ("dataroom_overview_serializer.errors", dataroom_overview_serializer.errors)
        
        if dataroom_overview_serializer.is_valid():
            dataroom_overview_serializer.save()
            # print ("dataroom overview successfully saved")
        temppp=str(data['hide_file_indexing'])
        # print(temppp,'*************************')

        # DataroomOverview.objects.filter(dataroom_id=dataroom.id).update(hide_file_indexing=temppp)
        dataroom_overview_update = DataroomOverview.objects.filter(id=data.get("id")).update(send_daily_email_updates=data.get("send_daily_email_updates"),choose_overview_default_page=data.get("choose_overview_default_page"),hide_file_indexing=data.get("hide_file_indexing"),dataroom=data.get("dataroom"))
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
        # print ("Create Contact Api called")
        data = request.data
        # print ("request data is ", data)
        user = request.user
        data["user"] = user.id

        serializer = ContactSerializer(data=data)
        # print ("serializer", serializer.is_valid())
        # print ("serializer", serializer.errors)
        
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

from django.core.files.storage import FileSystemStorage
from django.conf import settings
private_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)
class UploadDataroomPic(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk, format=None):
        user = request.user
        dataroom_pic = request.FILES.get('profile_pic')
        dataroom = Dataroom.objects.get(id=pk)
        import magic
        file12=dataroom_pic
        
        mime = magic.from_buffer(file12.read(), mime=True)
        if dataroom_pic.content_type==mime:
            if dataroom.dataroom_logo.url != "default_images/dataroom-icon.png":
                pass
                # dataroom.dataroom_logo.delete(save=True)
            dataroom.dataroom_logo = dataroom_pic
            # print(private_storage.location)

            dataroom.save()
            serializer = DataroomSerializer(dataroom, many=False)
            data1=serializer.data
            data1['dataroom_logo']= str(data1['dataroom_logo'])
            data = {
            "data": data1, 
            "msg" : "Dataroom picture successfully added!"
            }
            # print(data)
            return Response(data)
        else:
            return Response({"msg" : "cannot upload this type of file"},status=status.HTTP_400_BAD_REQUEST)


class SetDefaultDataroomPic(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk, format=None):
        user = request.user
        # print(user.id)
        # print(pk)
        # dataroom = Dataroom.objects.get(user_id=user.id,id=pk)
        dataroom = Dataroom.objects.get(id=pk)
        # print ("dataroom logo url ", dataroom.dataroom_logo.url)
        # if dataroom.dataroom_logo.url != "default_images/dataroom-icon.png":
        #   print ("dont delete the url")
        #   dataroom.dataroom_logo.delete(save=True)

        # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==')
        # container_name ='docullycontainer'
        # filename_Azurepath='https://docullystorage.blob.core.windows.net/docullycontainer/'
        # print(filename_Azurepath,"filename")
        # blob_name=filename_Azurepath
        # print(blob_name,"blob_name")
        # block_blob_service.create_blob_from_path(container_name,blob_name,outputfile,content_settings=ContentSettings(content_type='application/pdf'))
        # sas_url = block_blob_service.generate_blob_shared_access_signature(container_name,blob_name,BlobPermissions.READ,datetime.datetime.utcnow() + datetime.timedelta(days=2))
        #print sas_url
        # print(sas_url)
        # print ("dataroom logo url ", dataroom.dataroom_logo.url)
        dataroom.dataroom_logo = 'images/dataroom-icon.png'
        dataroom.save()
        # dataroom.dataroom_logo.url = str(dataroom.dataroom_logo)+sas_url
        serializer = DataroomSerializer(dataroom, many=False)
        # print(serializer.data)
        data1=serializer.data
        data1['dataroom_logo']= str(data1['dataroom_logo'])
        # print(data1['dataroom_logo'],'hrhrh')
        data = {
            "data": data1, 
            "msg" : "Data Room Logo updated successfully!"
        }
        # print(data)
        return Response(data)

    # def put(self, request, pk, format=None):
    #   user = request.user
    #   print(user.id)
    #   print(pk)
    #   # dataroom = Dataroom.objects.get(user_id=user.id,id=pk)
    #   dataroom = Dataroom.objects.get(id=pk)
    #   # print ("dataroom logo url ", dataroom.dataroom_logo.url)
    #   # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==')


    #   # container_name ='docullycontainer'
    #   # filename_Azurepath=OutFile.split("/").pop()
    #   # print(filename_Azurepath,"filename")
    #   # blob_name=filename_Azurepath
    #   # print(blob_name,"blob_name")
    #   # # block_blob_service.create_blob_from_path(container_name,blob_name,outputfile,content_settings=ContentSettings(content_type='application/pdf'))
    #   # sas_url = block_blob_service.generate_blob_shared_access_signature(container_name,blob_name,BlobPermissions.READ,datetime.datetime.utcnow() + datetime.timedelta(days=2))
    #   # #print sas_url
    #   # print(sas_url)

    #   if dataroom.dataroom_logo.url != "images/dataroom-icon.png":
    #       print ("dont delete the url")
    #       dataroom.dataroom_logo.delete(save=True)
        
    #   dataroom.dataroom_logo.url = "images/dataroom-icon.png"
    #   dataroom.save()
    #   serializer = DataroomSerializer(dataroom, many=False)
    #   # serializer.data['dataroom_logo']='https://services.docullyvdr.com/assets/images/dataroom-icon.png'
    #   print(serializer.data)
    #   data = {
    #       "data": serializer.data, 
    #       "msg" : "Data Room Logo updated successfully!"
    #   }
    #   return Response(data)

class UploadDataroomOverviewVideo(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        overview_video = request.FILES.getlist('overview_video')
        data = request.data
        dataroom_id = data.get("dataroom_id")
        overview_video_file = data.get("file")
        import magic
        file12=overview_video_file
        
        mime = magic.from_buffer(file12.read(), mime=True)
        if overview_video_file.content_type==mime:
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
        # print ("remove dataroom overview api method called")
        user = request.user
        dataroom_overview = DataroomOverview.objects.get(user_id=user.id, dataroom_id=pk)
        dataroom_overview.change_video_ppt.delete()
        dataroom_overview.save()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        return Response({"data":dataroom_overview_serializer.data, "msg":"Overview video successfully removed !"})


import PyPDF2
from io import BytesIO
class AddNewDataroomDisclaimer(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, pk, format=None):
        # print ("get method called", pk)
        user = request.user
        data = request.data
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk)
        dataroom_disclaimer_serilizer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=True)
        # print ("dataroom_disclaimer_serilizer data", dataroom_disclaimer_serilizer.data)
        return Response(dataroom_disclaimer_serilizer.data)

    def post(self, request, pk, format=None):
        #data = request.data
        
        user = request.user
        # print ("request files", request.FILES)
        disclaimer = request.FILES.get('fileKey')
        if disclaimer == None:
            disclaimer = request.FILES.getlist('file')[0]
        # print ("request files", disclaimer)
        # print ("file name is", disclaimer.name)
        import magic
        file12=disclaimer
        
        mime = magic.from_buffer(file12.read(), mime=True)
        if disclaimer.content_type==mime:
            dataaa=request.data.get('file_size')
            print(dataaa,'44444444444444444444444444ttttttttttttttttttttttdiscla,er')
            # file_content = disclaimer.read()

            # with open(file_content) as fileee:
            pdfReader = PyPDF2.PdfReader(disclaimer,strict=False)
            pn = len(pdfReader.pages)
            print('------------pages',pn)
            new_data = {
                'user':user.id, 
                'dataroom': int(pk), 
                'is_dataroom_disclaimer_default': False, 
                'dataroom_disclaimer_preview_status': 1,
                'dataroom_disclaimer_name': disclaimer.name if '.pdf' in str(disclaimer.name) else None ,
                'file_size':dataaa 
            }

            dataroom_disclaimer_serializer = DataroomDisclaimerSerializerupload(data=new_data)
            # print ("dataroom disclaimer errors",dataroom_disclaimer_serializer.is_valid(), dataroom_disclaimer_serializer.errors)
            if dataroom_disclaimer_serializer.is_valid():
                dataroom_disclaimer_serializer.save()
                dataroom_disclaimer = DataroomDisclaimer.objects.get(id=dataroom_disclaimer_serializer.data.get("id"))
                dataroom_disclaimer.dataroom_disclaimer.delete(save=True)
                dataroom_disclaimer.dataroom_disclaimer = disclaimer

                dataroom_disclaimer.pages=pn
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

        return Response(status=status.HTTP_400_BAD_REQUEST)


class DataroomDisclaimerApiView(APIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk , format=None):
        user = request.user

        # dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk, user_id=user.id) No data for sneha id but working for harvinder for this query
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk)
        filenameee = dataroom_disclaimer.dataroom_disclaimer.file.name.split('/')[-1]
        # filename_name = dataroom_disclaimer.dataroom_disclaimer.name
        # print(os.path.lexists(str(dataroom_disclaimer.dataroom_disclaimer.url)+sas_url))
        filename=str(dataroom_disclaimer.dataroom_disclaimer)
        import os, uuid, sys
        os.chdir('/home/cdms_backend/cdms2/')
        from azure.storage.blob import BlockBlobService, PublicAccess
        if dataroom_disclaimer.dataroom.is_usa_blob==True:
            block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
        else:   
            # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
            block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
        container_name ='docullycontainer'
        file_name = filename.split("/")
        block_blob_service.get_blob_to_path(container_name, filename, file_name[-1])

        if (os.path.exists(file_name[-1])):

            # file_path = os.path.join(str(dataroom_disclaimer.dataroom_disclaimer.url)+sas_url)
            with open(file_name[-1], 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'attachment; filename='+filenameee
                os.remove(file_name[-1])

                return response
            
        
    def put(self, request, pk, format=None):
        user = request.user
        dataroom_disclaimer = DataroomDisclaimer.objects.get(id=pk)
        
        if dataroom_disclaimer:
            # print ("dataroom disclaimer default", dataroom_disclaimer.is_dataroom_disclaimer_default)
            if not dataroom_disclaimer.is_dataroom_disclaimer_default:
                DataroomDisclaimer.objects.filter(dataroom_id = dataroom_disclaimer.dataroom_id).exclude(id=dataroom_disclaimer.id).update(is_dataroom_disclaimer_default=False)
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
        dataroom_disclaimer.dataroom_disclaimer.delete(save=True)
        dataroom_disclaimer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      


class CreateContactGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        # print("get method called")
        user = request.user
        contact_groups = ContactGroup.objects.filter(user_id=user.id)
        contact_serializer = ContactGroupSerializer(contact_groups, many=True)
        # print ("contact serializer data", contact_serializer.data)
        return Response(contact_serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        # print ("create contact group")
        user = request.user
        data = request.data
        data["user"] = user.id
        # print ("data is", data)
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
                    # print ("Dont insert the contact in group , beause this contact already exist")
                except:
                    new_data = {
                        'user' : user.id, 
                        'contact_group' : selected_group_id, 
                        'contact' : res["id"]
                    }
                    # print ("new data is", new_data)
                    contact_group_members_serializer = ContactGroupMembersSerializer(data= new_data)
                    # print ("contact group serializer ", contact_group_members_serializer.is_valid())
                    # print ("contact group errors", contact_group_members_serializer.errors)
                    if contact_group_members_serializer.is_valid():
                        contact_group_members_serializer.save()
            return Response({'msg':"Contact added !"}, status=status.HTTP_201_CREATED)
        elif len(selected_members) == 1:
            # print ("if selected_members length is equal to 1 ")
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
                # print ("new data is ", new_data)
                contact_group_members_serializer = ContactGroupMembersSerializer(data= new_data)
                # print ("contact group serializer ", contact_group_members_serializer.is_valid())
                # print ("contact group errors", contact_group_members_serializer.errors)
                if contact_group_members_serializer.is_valid():
                    contact_group_members_serializer.save()        
                    return Response({'msg':"Contact added !"}, status=status.HTTP_201_CREATED)
        else:
            # print("There is no member is selceted")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetAllContactsAssocitaedWithTheGroup(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        contact_group_members = [contact.contact.id for contact in ContactGroupMembers.objects.filter(contact_group_id=pk)]
        # print ("contact_group_members", contact_group_members)
        all_contact_members = Contacts.objects.filter(id__in=contact_group_members)
        all_contact_members_serializer = ContactSerializer(all_contact_members, many=True)
        # print ("All contacts member serializer", all_contact_members_serializer.data)
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
        # print ("post method called")
        user = request.user
        data = request.data
        my_team_id = data.get("my_team_id")
        is_uae=data.get("is_uae")
        print('----------------data======',data['dataroom'])
        dataroom_admin_data = data.get('dataroom').get('dataroom_admin')
        print("Dataroom Admin Data", dataroom_admin_data)
        dataroom_count = Dataroom.objects.filter(my_team=my_team_id).count()
        user_data=User.objects.filter(email=dataroom_admin_data['email']).last()
        if data.get('dataroom').get("edit")==True:
            dataroom_count=dataroom_count-1 
            dataroom_storage = Dataroom.objects.filter(my_team=my_team_id).exclude(id=data.get('dataroom').get("id")).aggregate(Sum('dataroom_storage_allocated')).get('dataroom_storage_allocated__sum') 
            dataroom_storage = dataroom_storage if dataroom_storage != None else Decimal(0.00)  + Decimal(data.get('dataroom').get('dataroom_storage_allocated'))
        else:
            dataroom_storage = Dataroom.objects.filter(my_team=my_team_id).aggregate(Sum('dataroom_storage_allocated')).get('dataroom_storage_allocated__sum')

            dataroom_storage = Decimal(dataroom_storage if dataroom_storage != None else Decimal(0.00))  + Decimal(data.get('dataroom').get('dataroom_storage_allocated'))

        # dataroom_storage = Dataroom.objects.filter(my_team=my_team_id).aggregate(Sum('dataroom_storage_allocated')).get('dataroom_storage_allocated__sum')
        my_team_allowed_datarooms = MyTeams.objects.get(id=my_team_id)
        # print ("dataroom count ", dataroom_count)

        # print ("my_team_allowed_datarooms", my_team_allowed_datarooms.dataroom_allowed)

        if Decimal(dataroom_storage) <= my_team_allowed_datarooms.dataroom_storage_allowed:
                if data.get('dataroom').get('dataroom_users_permitted')=='' or data.get('dataroom').get('dataroom_users_permitted')==None:
                    data['dataroom']['dataroom_users_permitted']=10000
                if data.get('dataroom').get("edit")==True:
                    dataroom_memberlimit=int(DataroomMembers.objects.filter(is_deleted=False,dataroom=data.get('dataroom').get("id")).count())
                    if int(data.get('dataroom').get('dataroom_users_permitted'))>=dataroom_memberlimit:
                        datroomdata=Dataroom.objects.get(id=data.get('dataroom').get("id"))
                        serializer = DataroomSerializertwo(datroomdata,data=data.get('dataroom'))
                        if serializer.is_valid():
                            serializer.save()   
                            if Dataroom.objects.filter(id=datroomdata.id,dataroom_version="Lite").exists():
                                cat= Categories.objects.create(categories_name="General",dataroom=datroomdata)
                                # for usr in each['user']:
                                # ManageDataroomCategories.objects.create(user=user_data, dataroom_id=datroomdata.id, category_id=cat.id)

                                ip = utils.get_client_ip(request)
                                # Watermarking.objects.create(dataroom_id=datroomdata.id,user=user_data,name='Center Center',type='center :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)
                                # Watermarking.objects.create(dataroom_id=datroomdata.id,user=user_data,name='Top Center',type='top :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)
                                # Watermarking.objects.create(dataroom_id=datroomdata.id,user=user_data,name='Center Center',type='bottom :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)
                                Watermarking.objects.filter(dataroom_id=datroomdata.id,user=user_data).update(name='Center Center',type='center :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True,font_size=20)
                                Watermarking.objects.filter(dataroom_id=datroomdata.id,user=user_data).update(name='Top Center',type='top :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True,font_size=20)
                                Watermarking.objects.filter(dataroom_id=datroomdata.id,user=user_data).update(name='Center Center',type='bottom :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True,font_size=20)
                                watermarking = Watermarking.objects.filter(dataroom_id=datroomdata.id).order_by('-id')
                                     

             


                            if dataroomProLiteFeatures.objects.filter(dataroom_id=serializer.data.get('id')).exists():
                                dataroomProLiteFeatures.objects.filter(dataroom_id=serializer.data.get('id')).update(dataroom_id=serializer.data.get('id'),
                                custom_watermarking=data['dataroom']['dataroom_features']['custom_watermarking'],
                                two_factor_auth=data['dataroom']['dataroom_features']['two_factor_auth'],
                                proj_overview=data['dataroom']['dataroom_features']['proj_overview'],
                                proj_video_intro=data['dataroom']['dataroom_features']['proj_video_intro'],
                                custom_logo=data['dataroom']['dataroom_features']['custom_logo'],
                                custom_external_link=data['dataroom']['dataroom_features']['custom_external_link'],
                                email_to_dataroom_upload=data['dataroom']['dataroom_features']['email_to_dataroom_upload'],
                                google_drive_upload=data['dataroom']['dataroom_features']['google_drive_upload'],
                                one_drive_upload=data['dataroom']['dataroom_features']['one_drive_upload'],
                                sharepoint_upload=data['dataroom']['dataroom_features']['sharepoint_upload'],
                                dropbox_upload=data['dataroom']['dataroom_features']['dropbox_upload'],
                                favourites=data['dataroom']['dataroom_features']['favourites'],
                                redaction=data['dataroom']['dataroom_features']['redaction'],
                                la_admin_access=data['dataroom']['dataroom_features']['la_admin_access'],
                                bulk_users_upload=data['dataroom']['dataroom_features']['bulk_users_upload'],
                                doculink_perm=data['dataroom']['dataroom_features']['doculink_perm'],
                                auto_expire=data['dataroom']['dataroom_features']['auto_expire'],
                                module_perm=data['dataroom']['dataroom_features']['module_perm'],
                                qa_with_cat=data['dataroom']['dataroom_features']['qa_with_cat'],
                                qa_submit=data['dataroom']['dataroom_features']['qa_submit'],
                                desktop_unlimit_upload=data['dataroom']['dataroom_features']['desktop_unlimit_upload'],
                                proj_management=data['dataroom']['dataroom_features']['proj_management'],
                                voting_perm=data['dataroom']['dataroom_features']['voting_perm'],
                                proj_updates=data['dataroom']['dataroom_features']['proj_updates'],
                                country_perm=data['dataroom']['dataroom_features']['country_perm'],
                                auto_logout=data['dataroom']['dataroom_features']['auto_logout'],
                                co_current_logins=data['dataroom']['dataroom_features']['co_current_logins'],
                                voting_report_perm=data['dataroom']['dataroom_features']['voting_report_perm'],
                                index_report_others=data['dataroom']['dataroom_features']['index_report_others'],
                                self_upload_status=data['dataroom']['dataroom_features']['self_upload_status'],
                                all_user_upload_status=data['dataroom']['dataroom_features']['all_user_upload_status'],
                                activity_tracker_perm=data['dataroom']['dataroom_features']['activity_tracker_perm'],
                                file_view_limit=data['dataroom']['dataroom_features']['file_view_limit'],
                                viewer_support=data['dataroom']['dataroom_features']['viewer_support'],
                                fence_viewer=data['dataroom']['dataroom_features']['fence_viewer'],
                                print_screen_perm=data['dataroom']['dataroom_features']['print_screen_perm'],
                                is_irm_protected=data['dataroom']['dataroom_features']['is_irm_protected'],
                                is_upload_restrict=data['dataroom']['dataroom_features']['is_upload_restrict'])

                            if data['dataroom']['dataroom_features']['is_upload_restrict']==False or data['dataroom']['dataroom_features']['is_upload_restrict']=="false":
                                DataroomGroupPermission.objects.filter(dataroom_id=serializer.data.get('id')).update(upload_ristrict_with_timer=False)
                            else:
                                dataroomProLiteFeatures.objects.create(dataroom_id=serializer.data.get('id'),
                                custom_watermarking=data['dataroom']['dataroom_features']['custom_watermarking'],
                                two_factor_auth=data['dataroom']['dataroom_features']['two_factor_auth'],
                                proj_overview=data['dataroom']['dataroom_features']['proj_overview'],
                                proj_video_intro=data['dataroom']['dataroom_features']['proj_video_intro'],
                                custom_logo=data['dataroom']['dataroom_features']['custom_logo'],
                                custom_external_link=data['dataroom']['dataroom_features']['custom_external_link'],
                                email_to_dataroom_upload=data['dataroom']['dataroom_features']['email_to_dataroom_upload'],
                                google_drive_upload=data['dataroom']['dataroom_features']['google_drive_upload'],
                                one_drive_upload=data['dataroom']['dataroom_features']['one_drive_upload'],
                                sharepoint_upload=data['dataroom']['dataroom_features']['sharepoint_upload'],
                                dropbox_upload=data['dataroom']['dataroom_features']['dropbox_upload'],
                                favourites=data['dataroom']['dataroom_features']['favourites'],
                                redaction=data['dataroom']['dataroom_features']['redaction'],
                                la_admin_access=data['dataroom']['dataroom_features']['la_admin_access'],
                                bulk_users_upload=data['dataroom']['dataroom_features']['bulk_users_upload'],
                                doculink_perm=data['dataroom']['dataroom_features']['doculink_perm'],
                                auto_expire=data['dataroom']['dataroom_features']['auto_expire'],
                                module_perm=data['dataroom']['dataroom_features']['module_perm'],
                                qa_with_cat=data['dataroom']['dataroom_features']['qa_with_cat'],
                                qa_submit=data['dataroom']['dataroom_features']['qa_submit'],
                                desktop_unlimit_upload=data['dataroom']['dataroom_features']['desktop_unlimit_upload'],
                                proj_management=data['dataroom']['dataroom_features']['proj_management'],
                                voting_perm=data['dataroom']['dataroom_features']['voting_perm'],
                                proj_updates=data['dataroom']['dataroom_features']['proj_updates'],
                                country_perm=data['dataroom']['dataroom_features']['country_perm'],   
                                auto_logout=data['dataroom']['dataroom_features']['auto_logout'],
                                co_current_logins=data['dataroom']['dataroom_features']['co_current_logins'],
                                voting_report_perm=data['dataroom']['dataroom_features']['voting_report_perm'],
                                index_report_others=data['dataroom']['dataroom_features']['index_report_others'],
                                self_upload_status=data['dataroom']['dataroom_features']['self_upload_status'],
                                all_user_upload_status=data['dataroom']['dataroom_features']['all_user_upload_status'],
                                activity_tracker_perm=data['dataroom']['dataroom_features']['activity_tracker_perm'],
                                file_view_limit=data['dataroom']['dataroom_features']['file_view_limit'],
                                viewer_support=data['dataroom']['dataroom_features']['viewer_support'],
                                fence_viewer=data['dataroom']['dataroom_features']['fence_viewer'],
                                print_screen_perm=data['dataroom']['dataroom_features']['print_screen_perm'],
                                is_irm_protected=data['dataroom']['dataroom_features']['is_irm_protected'],
                                is_upload_restrict=data['dataroom']['dataroom_features']['is_upload_restrict'])

                            if data['dataroom']['dataroom_features']['is_upload_restrict']==False or data['dataroom']['dataroom_features']['is_upload_restrict']=="false":
                                DataroomGroupPermission.objects.filter(dataroom_id=serializer.data.get('id')).update(upload_ristrict_with_timer=False)
                                
                            data = {
                                'message': "Dataroom is updated  !", 
                                'success': True
                            }
                            return Response(data, status=status.HTTP_201_CREATED)   
                        else:
                            print('edit ',serializer.errors)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                            data = {
                                'message': "The current number of members on the data room are higher than the new limit. Please remove the members from the  data room first to effect the new limit.", 
                                'success': False
                            }
                            return Response(data, status=status.HTTP_201_CREATED)   

                else:
                    if dataroom_count < my_team_allowed_datarooms.dataroom_allowed:

                        if int(data.get('dataroom').get('dataroom_users_permitted'))!=0:
                            dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
                            dataroom_data = data.get('dataroom')
                            dataroom_data["user"] = user.id
                            dataroom_data["my_team"] = int(my_team_id)
                            dataroom_data["is_paid"] = True
                            dataroom_data["offlinedataroom"] = True
                            # dataroom_data["dataroom_modules"] =  DataroomModulesSerializer(dataroom_modules,many=False).data
                            dataroom_data["dataroom_modules"] =  dataroom_modules.id

                            serializer = DataroomSerializertwo(data=dataroom_data)
                            print ("serailizer valid", serializer.is_valid())
                            print ("serailizer errors", serializer.errors)
                            
                            if serializer.is_valid():
                                serializer.save()
                                id_1=serializer.data.get('id')
                                Dataroom.objects.filter(id=id_1).update(is_usa_blob=is_uae)
                                if Dataroom.objects.filter(id=id_1,dataroom_version="Lite").exists():

                                    cat= Categories.objects.create(categories_name="General",dataroom_id=id_1)
                                    # cat= Categories.objects.create(categories_name="General",dataroom=datroomdata)
                                # for usr in each['user']:
                                    ManageDataroomCategories.objects.create(user=user_data, dataroom_id=id_1, category_id=cat.id)

                                    Watermarking.objects.create(dataroom_id=id_1,user=user_data,name='Center Center',type='center :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)
                                    Watermarking.objects.create(dataroom_id=id_1,user=user_data,name='Top Center',type='top :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)
                                    Watermarking.objects.create(dataroom_id=id_1,user=user_data,name='Center Center',type='bottom :: center',user_ipaddress=True,user_name=True,user_email=True,current_time=True,dataroom_name=True)

                                if dataroomProLiteFeatures.objects.filter(dataroom_id=serializer.data.get('id')).exists():

                                    dataroomProLiteFeatures.objects.filter(dataroom_id=serializer.data.get('id')).update(dataroom_id=data['id'],
                                    custom_watermarking=data['dataroom']['dataroom_features']['custom_watermarking'],
                                    two_factor_auth=data['dataroom']['dataroom_features']['two_factor_auth'],
                                    proj_overview=data['dataroom']['dataroom_features']['proj_overview'],
                                    proj_video_intro=data['dataroom']['dataroom_features']['proj_video_intro'],
                                    custom_logo=data['dataroom']['dataroom_features']['custom_logo'],
                                    custom_external_link=data['dataroom']['dataroom_features']['custom_external_link'],
                                    email_to_dataroom_upload=data['dataroom']['dataroom_features']['email_to_dataroom_upload'],
                                    google_drive_upload=data['dataroom']['dataroom_features']['google_drive_upload'],
                                    one_drive_upload=data['dataroom']['dataroom_features']['one_drive_upload'],
                                    sharepoint_upload=data['dataroom']['dataroom_features']['sharepoint_upload'],
                                    dropbox_upload=data['dataroom']['dataroom_features']['dropbox_upload'],
                                    favourites=data['dataroom']['dataroom_features']['favourites'],
                                    redaction=data['dataroom']['dataroom_features']['redaction'],
                                    la_admin_access=data['dataroom']['dataroom_features']['la_admin_access'],
                                    bulk_users_upload=data['dataroom']['dataroom_features']['bulk_users_upload'],
                                    doculink_perm=data['dataroom']['dataroom_features']['doculink_perm'],
                                    auto_expire=data['dataroom']['dataroom_features']['auto_expire'],
                                    module_perm=data['dataroom']['dataroom_features']['module_perm'],
                                    qa_with_cat=data['dataroom']['dataroom_features']['qa_with_cat'],
                                    qa_submit=data['dataroom']['dataroom_features']['qa_submit'],
                                    desktop_unlimit_upload=data['dataroom']['dataroom_features']['desktop_unlimit_upload'],
                                    proj_management=data['dataroom']['dataroom_features']['proj_management'],
                                    voting_perm=data['dataroom']['dataroom_features']['voting_perm'],
                                    proj_updates=data['dataroom']['dataroom_features']['proj_updates'],
                                    country_perm=data['dataroom']['dataroom_features']['country_perm'],                                
                                    auto_logout=data['dataroom']['dataroom_features']['auto_logout'],
                                    co_current_logins=data['dataroom']['dataroom_features']['co_current_logins'],
                                    voting_report_perm=data['dataroom']['dataroom_features']['voting_report_perm'],
                                    index_report_others=data['dataroom']['dataroom_features']['index_report_others'],
                                    self_upload_status=data['dataroom']['dataroom_features']['self_upload_status'],
                                    all_user_upload_status=data['dataroom']['dataroom_features']['all_user_upload_status'],
                                    activity_tracker_perm=data['dataroom']['dataroom_features']['activity_tracker_perm'],
                                    file_view_limit=data['dataroom']['dataroom_features']['file_view_limit'],
                                    viewer_support=data['dataroom']['dataroom_features']['viewer_support'],
                                    fence_viewer=data['dataroom']['dataroom_features']['fence_viewer'],
                                    print_screen_perm=data['dataroom']['dataroom_features']['print_screen_perm'],
                                    is_irm_protected=data['dataroom']['dataroom_features']['is_irm_protected'],
                                    is_upload_restrict=data['dataroom']['dataroom_features']['is_upload_restrict'])
                                else:
                                    dataroomProLiteFeatures.objects.create(dataroom_id=serializer.data.get('id'),
                                    custom_watermarking=data['dataroom']['dataroom_features']['custom_watermarking'],
                                    two_factor_auth=data['dataroom']['dataroom_features']['two_factor_auth'],
                                    proj_overview=data['dataroom']['dataroom_features']['proj_overview'],
                                    proj_video_intro=data['dataroom']['dataroom_features']['proj_video_intro'],
                                    custom_logo=data['dataroom']['dataroom_features']['custom_logo'],
                                    custom_external_link=data['dataroom']['dataroom_features']['custom_external_link'],
                                    email_to_dataroom_upload=data['dataroom']['dataroom_features']['email_to_dataroom_upload'],
                                    google_drive_upload=data['dataroom']['dataroom_features']['google_drive_upload'],
                                    one_drive_upload=data['dataroom']['dataroom_features']['one_drive_upload'],
                                    sharepoint_upload=data['dataroom']['dataroom_features']['sharepoint_upload'],
                                    dropbox_upload=data['dataroom']['dataroom_features']['dropbox_upload'],
                                    favourites=data['dataroom']['dataroom_features']['favourites'],
                                    redaction=data['dataroom']['dataroom_features']['redaction'],
                                    la_admin_access=data['dataroom']['dataroom_features']['la_admin_access'],
                                    bulk_users_upload=data['dataroom']['dataroom_features']['bulk_users_upload'],
                                    doculink_perm=data['dataroom']['dataroom_features']['doculink_perm'],
                                    auto_expire=data['dataroom']['dataroom_features']['auto_expire'],
                                    module_perm=data['dataroom']['dataroom_features']['module_perm'],
                                    qa_with_cat=data['dataroom']['dataroom_features']['qa_with_cat'],
                                    qa_submit=data['dataroom']['dataroom_features']['qa_submit'],
                                    desktop_unlimit_upload=data['dataroom']['dataroom_features']['desktop_unlimit_upload'],
                                    proj_management=data['dataroom']['dataroom_features']['proj_management'],
                                    voting_perm=data['dataroom']['dataroom_features']['voting_perm'],
                                    proj_updates=data['dataroom']['dataroom_features']['proj_updates'],
                                    country_perm=data['dataroom']['dataroom_features']['country_perm'],                                
                                    auto_logout=data['dataroom']['dataroom_features']['auto_logout'],
                                    co_current_logins=data['dataroom']['dataroom_features']['co_current_logins'],
                                    voting_report_perm=data['dataroom']['dataroom_features']['voting_report_perm'],
                                    index_report_others=data['dataroom']['dataroom_features']['index_report_others'],
                                    self_upload_status=data['dataroom']['dataroom_features']['self_upload_status'],
                                    all_user_upload_status=data['dataroom']['dataroom_features']['all_user_upload_status'],
                                    activity_tracker_perm=data['dataroom']['dataroom_features']['activity_tracker_perm'],
                                    file_view_limit=data['dataroom']['dataroom_features']['file_view_limit'],
                                    viewer_support=data['dataroom']['dataroom_features']['viewer_support'],
                                    fence_viewer=data['dataroom']['dataroom_features']['fence_viewer'],
                                    print_screen_perm=data['dataroom']['dataroom_features']['print_screen_perm'],
                                    is_irm_protected=data['dataroom']['dataroom_features']['is_irm_protected'],
                                    is_upload_restrict=data['dataroom']['dataroom_features']['is_upload_restrict'])

                                c_d_object = CreateOverviewHeading()
                                create_nested_data = c_d_object.create_dataroom_overiview_headings_links(request, serializer.data)
                                if create_nested_data:
                                    data = {
                                        'message' : " Dataroom successfully created",
                                        'data' : serializer.data, 
                                        'success': True  
                                    }
                                _new_dataroom_admin = DataroomAdmin()
                                # print("Dataroom Admin Data", dataroom_admin_data)
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
                                dataroom_admin.is_end_user = False
                                dataroom_admin.save()
                                dataroom_member_serializer = DataroomMembersSerializer(data=dataroom_member_data)
                                # print ("dataroom_member is valid", dataroom_member_serializer.is_valid())
                                # print ("dataroom_member errors", dataroom_member_serializer.errors)
                                
                                if dataroom_member_serializer.is_valid():
                                    dataroom_member_serializer.save()
                                    admin_user = User.objects.filter(email=dataroom_admin_data.get('email')).first()
                                    if admin_user:
                                        obj, created = DataroomMembers.objects.get_or_create(dataroom_id=serializer.data['id'], member_id=admin_user.id, member_added_by_id=user.id)
                                        obj.is_dataroom_admin = True
                                        obj.memberactivestatus= True
                                        obj.date_joined=datetime.datetime.now()
                                        obj.save()
                                    # send email to the dataroom member
                                    if is_exist_user:
                                        # print ("is_exist_user", is_exist_user)
                                        # print ("send email to already exist should called")
                                        dataroom_utils.send_email_to_already_exist_admin_or_end_user(dataroom_admin, serializer.data,  subject = "Welcome to DocullyVDR")
                                        # print ("Email sucessfully send")
                                    else:
                                        # print ("is_exist_user", is_exist_user)
                                        # print ("create new user send password method should called")
                                        dataroom_utils.send_password_to_dataroom_admin_or_end_user(dataroom_admin , serializer.data, __dataroom_admin_password , subject = "Welcome to DocullyVDR" )                     
                                    return Response(data, status=status.HTTP_201_CREATED)
                                return Response({"errors":'Error in creating nested data'}, status=status.HTTP_400_BAD_REQUEST)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        else:
                                data = {
                                    'message': "Member count should be greater than Zero", 
                                    'success': False
                                }
                                return Response(data, status=status.HTTP_201_CREATED)
                    else :
                        # print ("dataroom limit is exceed")
                        data = {
                            'message': "Dataroom limit is exceed !", 
                            'success': False
                        }   
                        return Response(data, status=status.HTTP_201_CREATED)


        else:
                # print ("dataroom Storage limit is exceed")
                data = {
                    'message': "Dataroom Storage limit is exceed !", 
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
        # print ("dataroom dataroom_overview_serializer", dataroom_overview_serializer.is_valid())
        # print ("dataroom dataroom_overview_serializer erros", dataroom_overview_serializer.errors)
    
        if dataroom_overview_serializer.is_valid():
            dataroom_overview_serializer.save()
        return True

class DataroomAdmin:
    def __init__(self):
        print ("Create dataroom admin")

    def create_dataroom_admins(self, request, data):
        # print ("create dataroom admins")
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
            
            # print ("add new user")
            "generate random pasword for user"

            password = User.objects.make_random_password() # 7Gjk2kd4T9
            password = User.objects.make_random_password(length=14) # FTELhrNFdRbSgy
            passwrod = User.objects.make_random_password(length=14, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889") # zvk0hawf8m6394
            #user.set_password(password)
                        
            #password = "Password1#"#User.objects.make_random_password(length=14, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
            data["password"] = password
            data["is_active"] = True
            data["is_staff"] = True
            data["is_end_user"] = False
            create_new_user_serializer = UserSerializer(data=data)
            if create_new_user_serializer.is_valid():
                create_new_user_serializer.save()
            #step 2:
            #send email to user
                user = User.objects.get(email__iexact = data.get("email"))
                user.set_password(password)
                user.save()
                return user, False, password






class DataroomUsageDetailsForGraph(APIView):
   authentication_classes = (TokenAuthentication, )
   permission_classes = (IsAuthenticated, )

   def get(self, request, pk,  format=None):
           # print ("post method called")
           import datetime
           from datetime import timedelta
           # print ("primary key is", pk)
           # flagg = request.GET.get('location')
           dataroom_storage = Dataroom.objects.get(pk=pk)

           from_date = dataroom_storage.created_date
           first_date=from_date
           todaysdatee = str(datetime.date.today())
           todaysdatee = str(todaysdatee+'T23:59:50')

           todaysdatee=datetime.datetime.strptime( todaysdatee, '%Y-%m-%dT%H:%M:%S')
           to_date = str(request.GET.get('to_date'))
           to_date=str(to_date+'T23:58:50')
           # print("-------", from_date, to_date,todaysdatee)
           if not (from_date == '' and to_date == '') or not (from_date == 'undefined' and to_date == 'undefined'):
               # todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:00')
               todays_date = datetime.datetime.strptime(to_date,'%Y-%m-%dT%H:%M:%S')
               
               # print('))))))))))))))))',todays_date)
               # todays_date = datetime.datetime.strptime(todays_date,'%Y-%m-%d %H:%M:%S')
           # print(type(from_date),type(todays_date),type(todaysdatee))
           # print(from_date,todays_date,todaysdatee)
           pages=0
           docx_storage=0
           docx_storage_count1=0
           trash_media_storage=0
           trash_media_storage_count1=0
           trash_docx_page_count=0
           vote_media_storage=0
           vote_media_storage_count1=0
           vote_docx_page_count=0
           disc_media_storage=0
           disc_media_storage_count1=0           
           docx_list=['.pdf','.docx','.xlsx','.xls','.csv','.ppt','.pptx','doc']
           if from_date<=todays_date and todaysdatee>=todays_date: 
                   # print('coming herer ')
                   if (from_date == '' and to_date == '') or (from_date == 'undefined' and to_date == 'undefined'):
                       # dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk).aggregate(total_consumed_space = Sum('file_size_mb'))
                       dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False,is_deleted_permanent=False, is_folder=False,is_root_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       trash_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False,is_deleted_permanent=False,is_root_folder=False ).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       vote_consumed = round((Vote.objects.filter(dataroom_id=pk,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=pk,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=pk).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=pk).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       for li in docx_list:
                           docx_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False,name__iendswith=li)
                           docx_storage_count1=docx_storage_count1+docx_count.count()
                           docx_storage=docx_storage+round(docx_count.aggregate(Sum('file_size_mb')).get('file_size_mb__sum'))

                       

                   else:
                       # dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date).aggregate(total_consumed_space = Sum('file_size'))
                       # dataroom_consumed = ((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False,is_deleted_permanent=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       # trash_c=DataroomFolder.objects.filter(dataroom_id=pk,is_root_folder=False, is_deleted=True, is_folder=False, is_deleted_permanent=False)
                       # trash_consumed = round(trash_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False, is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       # vote_c=Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,vote_created__lte=todays_date,is_deleted=False)                       
                       # vote_consumed = round(vote_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,is_deleted=False).filter(vote_created__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       # disclaimer_c=DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date,disclaimer_added_date__lte=todays_date)                       
                       # disclaimer_consumed =round(disclaimer_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date).filter(disclaimer_added_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)

                       dataroom_consumed = ((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False,is_deleted_permanent=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)
                       trash_c=DataroomFolder.objects.filter(dataroom_id=pk,is_root_folder=False, is_deleted=True, is_folder=False, is_deleted_permanent=False)
                       trash_consumed = round(trash_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False, is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)
                       vote_c=Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,vote_created__lte=todays_date,is_deleted=False)                       
                       vote_consumed = round(vote_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,is_deleted=False).filter(vote_created__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)
                       disclaimer_c=DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date,disclaimer_added_date__lte=todays_date)                       
                       disclaimer_consumed =round(disclaimer_c.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date).filter(disclaimer_added_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)
                       

                       # docx_count222 = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False).exclude(name__iendswith='.pdf').exclude(name__iendswith='.docx').exclude(name__iendswith='.xlsx').exclude(name__iendswith='.xls').exclude(name__iendswith='.csv').exclude(name__iendswith='.ppt').exclude(name__iendswith='.pptx').exclude(name__iendswith='.doc')
                       # # try:
                       # for i in docx_count222:
                       #  # print('----------------------otherssssss file nameee0',i.name)
                       #  # DataroomFolder.objects.filter(dataroom_id=771,id=i.id).update(parent_folder_id=277977)
                       #  try:
                       #      print('----------------------otherssssss file nameee0',i.parent_folder.name)
                       #  except:
                       #      pass
                       # except:

                           # pass
                       for li in docx_list:
                           docx_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False,name__iendswith=li,is_compatable=True)
                           try:
                                pages=pages+int(docx_count.aggregate(Sum('pages')).get('pages__sum'))
                           except:

                                pages=pages

                           # print('----------------++++++@@@@@^^^^%%%%%%%%%%@@@@@@docxxxx',docx_count.count())                           

                           
                           docx_storage_count1=docx_storage_count1+docx_count.count()
                           if docx_count.count()!=0:
                                docx_storage=docx_storage+docx_count.aggregate(Sum('file_size_mb')).get('file_size_mb__sum')
                           print('=======+++++++))))))))))))))))000',docx_storage)
                           trash_media_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=True, is_root_folder=False, is_deleted_permanent=False,name__iendswith=li,is_compatable=True)
                           trash_media_storage_count1=trash_media_storage_count1+trash_media_count.count()
                           # print('----------------++++++@@@@@^^^^%%%%%%%%%%@@@@@@',trash_media_count.count()) 


                           if trash_media_count.count()!=0:
                                try:
                                    trash_media_storage=trash_media_storage+trash_media_count.aggregate(Sum('file_size_mb')).get('file_size_mb__sum')
                                except:
                                    trash_media_storage=trash_media_storage

                                try:
                                    trash_docx_page_count=trash_docx_page_count+int(trash_media_count.aggregate(Sum('pages')).get('pages__sum'))
                                except:

                                    trash_docx_page_count=trash_docx_page_count


                                # trash_docx_page_count



                           vote_media_count = Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,vote_created__lte=todays_date,is_deleted=False,document_file_name__iendswith=li) 
                           
                           vote_media_storage_count1=vote_media_storage_count1+vote_media_count.count()
                           # print('----------------++++++@@@@@^^^^%%%%%%%%%%@@@@@@voteeee',vote_media_count.count())                           
                           if vote_media_count.count()!=0:
                                try:
                                    vote_media_storage=vote_media_storage+vote_media_count.aggregate(Sum('file_size_mb')).get('file_size_mb__sum')
                                except:
                                    vote_media_storage=vote_media_storage

                                try:
                                    vote_docx_page_count=vote_docx_page_count+int(vote_media_count.aggregate(Sum('pages')).get('pages__sum'))
                                except:

                                    vote_docx_page_count=vote_docx_page_count

                           disc_media_count = DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date,disclaimer_added_date__lte=todays_date,dataroom_disclaimer_name__iendswith=li)
                           
                           disc_media_storage_count1=disc_media_storage_count1+disc_media_count.count()
                           # print('----------------++++++@@@@@^^^^%%%%%%%%%%@@@@@@dsiccc',disc_media_count.count())                           
                           if disc_media_count.count()!=0:
                                try:
                                    disc_media_storage=disc_media_storage+disc_media_count.aggregate(Sum('file_size_mb')).get('file_size_mb__sum')
                                except:
                                    disc_media_storage=disc_media_storage
 



                   Redacted_Pdf_docx=Redacted_Pdf.objects.filter(dataroom_id=pk,is_deleted=False,is_deleted_permanent=False)
                   Redacted_Pdf_trash=Redacted_Pdf.objects.filter(dataroom_id=pk,is_deleted=True,is_deleted_permanent=False)
                   # docx_storage_count1=docx_storage_count1=Redacted_Pdf_docx.count()
                   # trash_media_storage_count1=trash_media_storage_count1+Redacted_Pdf_trash.count()



                   print('------------------12121',dataroom_consumed)
                   print('------------------121212',trash_consumed)
                   print('------------------22223333',vote_consumed)
                   print('------------------33334444',disclaimer_consumed)

                   if int(dataroom_consumed)<dataroom_consumed:
                       dataroom_consumed=int(dataroom_consumed)+1   
                   if int(trash_consumed)<trash_consumed:
                       trash_consumed=int(trash_consumed)+1 
                   if int(vote_consumed)<vote_consumed:
                       vote_consumed=int(vote_consumed)+1   
                   print('--------------disclamer',disclaimer_consumed,'-----int disc',int(disclaimer_consumed))
                   if int(disclaimer_consumed)<disclaimer_consumed:
                       disclaimer_consumed=int(disclaimer_consumed)+1   


                   # docx_storage=round(docx_storage)
                   # vote_media_storage=round(vote_media_storage)
                   # disc_media_storage=round(disc_media_storage)

                   print('-----------------------------------------------doccccczxxxx storage',int(docx_storage))


                   if int(docx_storage)<docx_storage:
                       docx_storage=int(docx_storage)+1   


                   if int(vote_media_storage)<vote_media_storage:
                       vote_media_storage=int(vote_media_storage)+1   

                   if int(disc_media_storage)<disc_media_storage:
                       disc_media_storage=int(disc_media_storage)+1   



                   # dataroom_consumed = dataroom_consumed.get('total_consumed_space')/100000
                   totaldataroomcosumed=dataroom_consumed+trash_consumed+vote_consumed+disclaimer_consumed
                   if int(totaldataroomcosumed)<totaldataroomcosumed:
                       totaldataroomcosumed=int(totaldataroomcosumed)+1                    
                   if int(totaldataroomcosumed)==0 and totaldataroomcosumed>0:
                       totaldataroomcosumed=1

                   # print('dataroom_consumed 1---',dataroom_consumed)
                   # document_count222 = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False)
                   # for i in document_count222:
                   #     print('----------------------count nameeeeee',i.name)
                   #     print('----------------------count nameeeeee',i.index)
                   #     print('----------------------count nameeeeee',i.parent_folder.name)
                   document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False).count()
                   trash_document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=True, is_root_folder=False, is_deleted_permanent=False).count()
                   # vote_document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=True, is_root_folder=False, is_deleted_permanent=False).count()
                   # disc_document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=True, is_root_folder=False, is_deleted_permanent=False).count()
                   # print ("document count is ", document_count)
                   # print ("dataroom dataroom_consumed", dataroom_consumed)
                   

                   if document_count is None:
                       document_count = 0
                   if dataroom_consumed is None:
                       dataroom_consumed = 0
                   
                   
                   
                   # if docx_count is None:
                   #     docx_count = 


                   others_d=DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False,is_compatable=False)
                   others_d1=DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False,is_compatable=True).exclude(name__iendswith='.pdf').exclude(name__iendswith='.docx').exclude(name__iendswith='.xlsx').exclude(name__iendswith='.xls').exclude(name__iendswith='.csv').exclude(name__iendswith='.ppt').exclude(name__iendswith='.pptx').exclude(name__iendswith='.doc')
                    



                   print('dataroom_consumed',dataroom_consumed)
                   print('docx_storage',round(docx_storage))
                   print('document_count',document_count)
                   print('docx_storage_count1',docx_storage_count1)
                   # print('dataroom_consumed',dataroom_consumed)
                   others_storage=round(others_d.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if others_d.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else  0)
                   others_storage1=round(others_d1.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') if others_d1.aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else  0)

                   others_storage=others_storage+others_storage1
                   
                   others_storage_count=others_d.count()+others_d1.count()
                   # others_storage_count1=

                   trash_others_storage=int(trash_consumed)-int(trash_media_storage)
                   trash_others_storage_count=int(trash_document_count)-int(trash_media_storage_count1)

                   vote_others_storage=int(vote_consumed)-int(vote_media_storage)
                   vote_others_storage_count=int(vote_c.count())-int(vote_media_storage_count1)


                   disc_others_storage=int(disclaimer_consumed)-int(disc_media_storage)
                   disc_others_storage_count=int(disclaimer_c.count())-int(disc_media_storage_count1)

                   if others_storage:
                       others_page_count=(int(others_storage)*1024)/65
                   else:
                       others_page_count=0
                   docx_page_count=pages

                   print('docx_page_count',docx_page_count)
                   print('others_storage',others_storage)

                   trash_docx_page_count=trash_docx_page_count
                   trash_others_page_count=(int(trash_others_storage)*1024)/65


                   vote_docx_page_count=vote_docx_page_count
                   vote_others_page_count=(int(vote_others_storage)*1024)/65

                   disc_docx_page_count=disclaimer_c.aggregate(Sum('pages')).get('pages__sum')
                   # disc_others_page_count=(int(disc_others_storage)*1024)/65


                   # total dataroom storage
                   # print("dataroom_storage===>",Dataroom.objects.filter(pk=pk).values())
                   total_dataroom_storage  = dataroom_storage.dataroom_storage_allocated*1024 # all data in MBS
                   # total_dataroom_storage  = dataroom_storage.dataroom_storage_allocated # all data in MBS
                   # print('total_dataroom_storage',total_dataroom_storage)
                   # dataroom_consumed = (dataroom_consumed/1024)/1024  # all data in mbs
                   # print('dataroom_consumedv 2',dataroom_consumed)
                   # print("dataroom ==>",round(dataroom_consumed/100000,3))
                   # print(int(total_dataroom_storage),"total_dataroom_storage====>",type(total_dataroom_storage))
                   # print(int(totaldataroomcosumed),"consumed==============>",type(totaldataroomcosumed))
                   # print("total_free ====>",float(total_dataroom_storage*1000) - float(dataroom_consumed))
                   # dataroom_free = total_dataroom_storage - Decimal(dataroom_consumed)
                   dataroom_free = int(total_dataroom_storage) - int(totaldataroomcosumed)
                   # print('dataroom_free',dataroom_free)
                   document_count1=int(trash_c.count())+int(vote_c.count())+int(disclaimer_c.count())+int(document_count)
                   print('-------------------lasttttt++=$$$$$$$$$$$$$$$',document_count)
                   print('-------------------lasttttttrash_c',trash_c.count())
                   print('-------------------lasttttt++=$$$$$$$$$$$$$$$',disclaimer_c.count())
                   data = {
                       'total_dataroom_storage' : int(total_dataroom_storage), 
                       'dataroom_consumed' : int(totaldataroomcosumed),
                       'trash_consumed' :int(trash_consumed),
                       'vote_consumed':int(vote_consumed),
                       'disclaimer_consumed':int(disclaimer_consumed),
                       'dataroom_free'  : int(dataroom_free), 
                       'document': document_count1,
                       'live_total_docs': document_count,
                       'docx_storage':round(docx_storage),
                       'docx_count': docx_storage_count1,
                       'docx_page_count':round(docx_page_count),
                       'others_page_count':round(others_page_count),
                       'others_count':others_storage_count,
                       'others_storage':others_storage,
                        'trash_others_storage':trash_others_storage,
                        'trash_media_storage':round(trash_media_storage),
                        'trash_others_storage_count':trash_others_storage_count,
                        'trash_media_storage_count1':trash_media_storage_count1,
                        'trash_docx_page_count':round(trash_docx_page_count),
                        "trash_others_page_count":round(trash_others_page_count),
                        'vote_docx_count':vote_media_storage_count1,
                        'vote_others_count':vote_others_storage_count,
                        'vote_docx_storage':vote_media_storage,
                        'vote_others_storage':vote_others_storage,
                        'vote_docx_page_count':vote_docx_page_count,
                        'vote_others_page_count':vote_others_page_count,
                        'disc_docx_page_count':disc_docx_page_count,
                        # "disc_others_page_count":disc_others_page_count,

                        'vote_others_storage':vote_others_storage,
                        'vote_media_storage':vote_media_storage,
                        'vote_others_storage_count':vote_others_storage_count,
                        'vote_media_storage_count1':vote_media_storage_count1,

                        'disc_others_storage':disc_others_storage,
                        'disc_media_storage':disc_media_storage,
                        'disc_others_storage_count':disc_others_storage_count,
                        'disc_media_storage_count1':disc_media_storage_count1,

                       'trash_count':trash_c.count(),
                       'vote_count':vote_c.count(),
                       'disclaimer_count':disclaimer_c.count()



                   }

                   # print ("data is", data)
                   storage = data['dataroom_consumed']  
                   # print("Storage", str(storage)[3])
                   # if int(str(storage)[3]) < 5:
                   #     data['dataroom_consumed'] = int(str(storage)[0:1])
                   # else:
                   #     storage = storage + 0.1
                   data['dataroom_consumed'] = round(data['dataroom_consumed'],0)#int(str(storage)[0:1])
                   data['dataroom_free'] = round(data['dataroom_free'],0)
                   # print(data,'************')
                   return Response(data=data, status=status.HTTP_201_CREATED)
           else:
               return Response(data=None, status=status.HTTP_201_CREATED)










class DataroomUsageDetailsForGraphold(APIView):
   authentication_classes = (TokenAuthentication, )
   permission_classes = (IsAuthenticated, )

   def get(self, request, pk,  format=None):
           # print ("post method called")
           import datetime

           # print ("primary key is", pk)
           # flagg = request.GET.get('location')
           dataroom_storage = Dataroom.objects.get(pk=pk)

           from_date = dataroom_storage.created_date
           first_date=from_date
           todaysdatee = str(datetime.date.today())
           todaysdatee = str(todaysdatee+'T23:59:50')

           todaysdatee=datetime.datetime.strptime( todaysdatee, '%Y-%m-%dT%H:%M:%S')
           to_date = str(request.GET.get('to_date'))
           to_date=str(to_date+'T23:58:50')
           # print("-------", from_date, to_date,todaysdatee)
           if not (from_date == '' and to_date == '') or not (from_date == 'undefined' and to_date == 'undefined'):
               # todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:00')
               todays_date = datetime.datetime.strptime(to_date,'%Y-%m-%dT%H:%M:%S')
               
               # print('))))))))))))))))',todays_date)
               # todays_date = datetime.datetime.strptime(todays_date,'%Y-%m-%d %H:%M:%S')
           # print(type(from_date),type(todays_date),type(todaysdatee))
           # print(from_date,todays_date,todaysdatee)

           if from_date<=todays_date and todaysdatee>=todays_date: 
                   # print('coming herer ')
                   if (from_date == '' and to_date == '') or (from_date == 'undefined' and to_date == 'undefined'):
                       # dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk).aggregate(total_consumed_space = Sum('file_size_mb'))
                       dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False,is_deleted_permanent=False, is_folder=False,is_root_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       trash_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False,is_deleted_permanent=False,is_root_folder=False ).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False,is_deleted_permanent=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       vote_consumed = round((Vote.objects.filter(dataroom_id=pk,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=pk,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=pk).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=pk).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                   else:
                       # dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date).aggregate(total_consumed_space = Sum('file_size'))
                       dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False,is_deleted_permanent=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=False, is_folder=False, created_date__gte=first_date).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       trash_consumed = round((DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False, created_date__gte=first_date,is_deleted_permanent=False).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=pk, is_deleted=True, is_folder=False, created_date__gte=first_date,is_deleted_permanent=False).filter(created_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       vote_consumed = round((Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date).filter(vote_created__lte=todays_date,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=pk, vote_created__gte=first_date,is_deleted=False).filter(vote_created__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
                       disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date).filter(disclaimer_added_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=pk, disclaimer_added_date__gte=first_date).filter(disclaimer_added_date__lte=todays_date).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,3)
    



                   if int(dataroom_consumed)<dataroom_consumed:
                       dataroom_consumed=int(dataroom_consumed)+1   
                   if int(trash_consumed)<trash_consumed:
                       trash_consumed=int(trash_consumed)+1 
                   if int(vote_consumed)<vote_consumed:
                       vote_consumed=int(vote_consumed)+1   
                   if int(disclaimer_consumed)<disclaimer_consumed:
                       disclaimer_consumed=int(disclaimer_consumed)+1   



                   # dataroom_consumed = dataroom_consumed.get('total_consumed_space')/100000
                   totaldataroomcosumed=dataroom_consumed+trash_consumed+vote_consumed+disclaimer_consumed
                   if int(totaldataroomcosumed)<totaldataroomcosumed:
                       totaldataroomcosumed=int(totaldataroomcosumed)+1                    
                   if int(totaldataroomcosumed)==0 and totaldataroomcosumed>0:
                       totaldataroomcosumed=1

                   # print('dataroom_consumed 1---',dataroom_consumed)
                   document_count = DataroomFolder.objects.filter(dataroom_id=pk, is_folder=False, is_deleted=False, is_root_folder=False, is_deleted_permanent=False).count()
                   # print ("document count is ", document_count)
                   # print ("dataroom dataroom_consumed", dataroom_consumed)
                   if document_count is None:
                       document_count = 0
                   if dataroom_consumed is None:
                       dataroom_consumed = 0
                   # total dataroom storage
                   # print("dataroom_storage===>",Dataroom.objects.filter(pk=pk).values())
                   total_dataroom_storage  = dataroom_storage.dataroom_storage_allocated*1024 # all data in MBS
                   # total_dataroom_storage  = dataroom_storage.dataroom_storage_allocated # all data in MBS
                   # print('total_dataroom_storage',total_dataroom_storage)
                   # dataroom_consumed = (dataroom_consumed/1024)/1024  # all data in mbs
                   # print('dataroom_consumedv 2',dataroom_consumed)
                   # print("dataroom ==>",round(dataroom_consumed/100000,3))
                   # print(int(total_dataroom_storage),"total_dataroom_storage====>",type(total_dataroom_storage))
                   # print(int(totaldataroomcosumed),"consumed==============>",type(totaldataroomcosumed))
                   # print("total_free ====>",float(total_dataroom_storage*1000) - float(dataroom_consumed))
                   # dataroom_free = total_dataroom_storage - Decimal(dataroom_consumed)
                   dataroom_free = int(total_dataroom_storage) - int(totaldataroomcosumed)
                   # print('dataroom_free',dataroom_free)
                   data = {
                       'total_dataroom_storage' : int(total_dataroom_storage), 
                       'dataroom_consumed' : int(totaldataroomcosumed),
                       'trash_consumed' :int(trash_consumed),
                       'vote_consumed':int(vote_consumed),
                       'disclaimer_consumed':int(disclaimer_consumed),
                       'dataroom_free'  : int(dataroom_free), 
                       'document': document_count
                   }

                   # print ("data is", data)
                   storage = data['dataroom_consumed']
                   # print("Storage", str(storage)[3])
                   # if int(str(storage)[3]) < 5:
                   #     data['dataroom_consumed'] = int(str(storage)[0:1])
                   # else:
                   #     storage = storage + 0.1
                   data['dataroom_consumed'] = round(data['dataroom_consumed'],0)#int(str(storage)[0:1])
                   data['dataroom_free'] = round(data['dataroom_free'],0)
                   # print(data,'************')
                   return Response(data=data, status=status.HTTP_201_CREATED)
           else:
               return Response(data=None, status=status.HTTP_201_CREATED)


def pathgeneratortoprint(data):
    if data['is_root_folder']==False:
        dataa=DataroomFolder.objects.get(id=data['parent_folder'])
        dataa = DataroomFolderSerializer(dataa)
        tempp=str(pathgeneratortoprint(dataa.data))+'/'+str(data['name'])
    else:
        tempp=str(data['name'])

    return tempp

def build_tree_recursive_index_report(tree, parent, nodes):
    from data_documents import utils
    children  = [n for n in nodes if n['parent_folder'] == parent]
    for child in children:
        data = {}
        data['name'] = child['name']
        data['id'] = child['id']
        if child['is_folder'] == True:
            data['type'] = 'Folder'
        else:
            data['type']  = 'File'
        # if child['is_root_folder']==False:
        #   data['path'] = pathgeneratortoprint(child['parent_folder'])
        # else:
        data['path'] = child['path']
        data['date'] = child['created_date']
        data['size'] = child['file_size_mb'] if child['file_size_mb'] != None else 0
        data['index'] = utils.getIndexes(child)
        data['children'] = []
        tree.append(data)
        build_tree_recursive_index_report(data['children'], child['id'], nodes)

class DownloadDataroomIndexReport(APIView):
    authentication_classes = ( TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        
        if dataroompermission==False:
            dataroom = Dataroom.objects.get(id=pk)
            member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=pk,is_deleted=False).first()
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_Date')

            todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
            first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
            document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
            data = []
            from data_documents import utils
            for doc in document:
                flagg=0            

                if member.is_la_user == True or member.is_dataroom_admin == True:
                    flagg=1
                else:
                    # try:
                    perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=doc.id,dataroom_id=pk, dataroom_groups_id=member.end_user_group.first().id)
                    if perm_obj.is_view_only==True:
                            flagg=1
                    # except:
                        # flagg=0
                if flagg==1:
                        docu = DataroomFolder.objects.get(id = doc.id)
                        docu_serializer = DataroomFolderSerializer(docu)
                        datas = docu_serializer.data
                        datas['index'] = utils.getIndexes(datas)
                        data.append(datas)
                        docu1 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
                        if len(docu1) > 0:
                            datas = []
                            data.extend(utils.get_under_file_datewise(docu1,datas, from_date, to_date,member))
            for i in data:
                i['path']=str(dataroom.dataroom_nameFront)+'/'+str(pathgeneratortoprint(i))
                # print(i['path'],'&&&&&&&&&&&&&&&&&&&&')
            tree = []
            build_tree_recursive_index_report(tree, None, data)
            import csv
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="index.csv"'
            writer = csv.writer(response)
            if DataroomOverview.objects.filter(dataroom_id=pk).exists():
                DataroomOverviewdata=DataroomOverview.objects.filter(dataroom_id=pk).last()
                indexpermission=DataroomOverviewdata.hide_file_indexing
            else:
                indexpermission=True
            header_data, datas = utils.getExcelIndexReportUserWise(tree,[],indexpermission)
            
            writer.writerow(header_data)
            new_list = []
            # for value in datas:
            #   # #print(type(value),"<===== new_data_for_csv====>",value)
            #   new_list.append(list(value))
            # # #print("new_list==========>",new_list)
            # i=0
            # for new_value in new_list:
            #   # #print("new_value=====>",new_value)
            #   if new_list[i][-1] is not None:
            #       new_list[i][-1] = dataroom.dataroom_nameFront +'/'+ new_list[i][1] + '/' + new_list[i][-1]
            #       # new_path = new_list[1][-1].split('/')
            #   i=i+1
            # print(new_list,'list________')
            # # #print("set===>",str(new_list[1][-1]).split('/'))
            # print("new_path=====>",new_path[-1],new_path[-2],new_path[-3])
            # new_list[1][-1] = new_path[-3] +'/'+ new_path[-2]+'/'+new_path[-1]
            # print("updated_list===>",new_list)        
            writer.writerows(datas)         # print("writer", header_data, datas)
            return response
        else:
            return Response(None)


# class DownloadDataroomIndexReportnew(APIView):
#   authentication_classes = ( TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )

#   def get(self, request, pk, format=None):
#       user = request.user
#       dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
#       if dataroompermission==False:
#           dataroom = Dataroom.objects.get(id=pk)
#           member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=pk,is_deleted=False).first()
#           from_date = request.GET.get('from_date')
#           to_date = request.GET.get('to_Date')
#           if DataroomOverview.objects.filter(dataroom_id=pk).exists():
#               DataroomOverviewdata=DataroomOverview.objects.filter(dataroom_id=pk).last()
#               indexpermission=DataroomOverviewdata.hide_file_indexing
#           else:
#               indexpermission=True
#           todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
#           first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
#           document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
#           data = []
#           from data_documents import utils
#           import csv
#           response = HttpResponse(content_type='text/csv')
#           response['Content-Disposition'] = 'attachment; filename="index.csv"'
#           writer = csv.writer(response)
#           header_data, datas = utils.getExcelIndexReportUserWisenew(document,[],indexpermission,first_date,todays_date,member)
#           writer.writerow(header_data)
#           writer.writerows(datas)
#           return response



class DownloadDataroomIndexReportnew(APIView):
    authentication_classes = ( TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        user = request.user
        dataroompermission=dataroom_utils.checkdataroomaccess(user.id,int(pk))
        if dataroompermission==False:
            dataroom = Dataroom.objects.get(id=pk)
            member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=pk,is_deleted=False).first()
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_Date')
            if DataroomOverview.objects.filter(dataroom_id=pk).exists():
                DataroomOverviewdata=DataroomOverview.objects.filter(dataroom_id=pk).last()
                indexpermission=DataroomOverviewdata.hide_file_indexing
            else:
                indexpermission=True
            todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
            first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')
            document = DataroomFolder.objects.filter(dataroom_id = pk, is_root_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
            data = []
            from data_documents import utils
            import csv
            data = json.loads(request.data)
            # print('-----------dataaaaa',data)
            objid=int(data['statusid'])

            # datetimee=datetime.now()
            from data_documents.models import BulkDownloadstatus
            count1 = DataroomFolder.objects.filter(dataroom_id=dataroom.id, is_deleted=False).count()
            print('-----------count',count1)
            BulkDownloadstatus.objects.filter(id=objid,is_index_report=True).update(failfilecount=int(count1))
            file_name=str(BulkDownloadstatus.objects.filter(id=objid,is_index_report=True).last().filename)
            # filename = str(dataroom.dataroom_name)+"Index_Report"+str(int(datetimee.timestamp()))+'.csv'
            # response = HttpResponse(content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="index.csv"'
            with open(f'/home/cdms_backend/cdms2/media/{file_name}', 'w',encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header_data, datas = utils.getExcelIndexReportUserWisenew(request,document,objid,[],indexpermission,first_date,todays_date,member)
                # datas = datas.encode('utf-8', errors='ignore')
                writer.writerow(header_data)
                writer.writerows(datas)
            BulkDownloadstatus.objects.filter(id=objid,is_index_report=True).update(readytodownload=True)
            return Response('result', status=status.HTTP_201_CREATED)


class UploadNewContactCSV(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        # print ("user_id is", user.id)
        file = request.FILES['csv_file'] 
        import magic
        file12=file
        
        mime = magic.from_buffer(file12.read(), mime=True)
        if file.content_type==mime:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            #print ("reader data is", reader.__dict__)
            all_contacts = []
            for row in reader:
                row["user"] = user.id
                contact_serializer = ContactSerializer(data=row)
                # print ("contact serializer", contact_serializer.is_valid())
                # print ("contact errors", contact_serializer.errors)
                if contact_serializer.is_valid():
                    contact_serializer.save()
                else:
                    return Response([], status=status.HTTP_201_CREATED)

            all_contacts = Contacts.objects.filter(user_id=user.id)
            all_contacts_serializer = ContactSerializer(all_contacts, many=True)
            return Response(all_contacts_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg':'Cannot upload this type of file'},status=status.HTTP_400_BAD_REQUEST)



class DownloadSampleContactCsv(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        # print ("donwload contact csv")
        # print("if it is hit in the url ================>")
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
        
        # print ("dataroom id is", pk)
        contacts = Contacts.objects.filter(user_id=user.id, dataroom_id = pk)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CreateDataroomContactApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def post(self, request, format=None):
        # print ("post method called")
        user = request.user
        new_data = request.data
        # print ("request data is ", new_data)
        data = new_data.get('contact')
        user = request.user
        data["user"] = user.id
        data["dataroom"] = new_data.get('dataroom')#
        serializer = ContactSerializer(data=data)
        # print ("serializer", serializer.is_valid())
        # print ("serializer", serializer.errors)
        
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
        # if user.is_superadmin:
        #     datarooms = Dataroom.objects.filter(user_id = user.id)
        # elif user.is_admin:
        #     my_team_ids = [team.myteam.id for team in TeamMembers.objects.filter(member_id=user.id)]
        #     print ("my team ids ", my_team_ids)
        #     datarooms = Dataroom.objects.filter(my_team_id__in = my_team_ids)
        # elif user.is_end_user:
        #     dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(member_id=user.id)]
        #     print ("dataroom ids", dataroom_ids)
        #     datarooms = Dataroom.objects.filter(id__in=dataroom_ids)
        # print ("datarooms are", serializer.data)
        admin_access = False
        # end_user_dataroom_id = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(Q(is_end_user=True), is_deleted=False, member_id=user.id)]
        dataroom_ids = [dataroom_member.dataroom.id for dataroom_member in DataroomMembers.objects.filter(Q(is_dataroom_admin=True) | Q(is_la_user=True), is_deleted=False, member_id=user.id)]

        # end_user_datarooms = Dataroom.objects.filter(id__in=end_user_dataroom_id).count()
        # print("end_user_datarooms",end_user_datarooms)

        datarooms = Dataroom.objects.filter(id__in=dataroom_ids)
        print("admin access check",datarooms.count())
        if datarooms.count() > 0:
            admin_access = True
        storage = [{
            'name': 'Storage',
            'data': []
        }]
        document = [
            {'name': 'Proprietary or Undetectable','y': 0.2,'dataLabels': {'enabled': False}}
        ]
        for dataroom in datarooms:
            if dataroom:
                for stor in storage:
                    stor['data'].append({'name': dataroom.dataroom_nameFront, 'y': dataroom.dataroom_storage_allocated})
                    dataroom_consumed = DataroomFolder.objects.filter(dataroom_id=dataroom.id).aggregate(total_consumed_space = Sum('file_size')).get('total_consumed_space')

                    if dataroom_consumed is None:
                        dataroom_consumed = 0
                    dataroom_consumed = round(((dataroom_consumed/1024)/1024),0)  # all data in mbs
                    document.append([dataroom.dataroom_nameFront, dataroom_consumed])

        return Response({'storage': storage, 'document': document,'access':admin_access}, status=status.HTTP_201_CREATED)

class GetDataroomViewed(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):

        import datetime
        user = request.user
        dataroom_obj = DataroomView()
        dataroom_obj.dataroom_id = pk
        dataroom_obj.user_id = user.id
        qs = DataroomMembers.objects.filter(dataroom_id=pk,member_id=user.id, is_deleted=False).exists()
        invite_qs = InviteUser.objects.filter(invitiation_receiver_id=user.id,is_invitation_accepted=True,dataroom_invitation=pk,is_shifted=False).exists()
        if invite_qs:
            update_invite_event = InviteUser.objects.filter(invitiation_receiver_id=user.id,is_invitation_accepted=True,dataroom_invitation=pk,is_shifted=False).last()
            #### 17-11-2020 for invitation acceptance status 
            #### not needed 18-11-2020
            # update_event = DataroomMembers.objects.get(dataroom_id=pk,member_id=user.id, is_deleted=False,memberactivestatus=False)
            # update_event.memberactivestatus = True
            # update_event.save()
            # update_invite_event.invitiation_receiver_id__is_active = True
            #######
            update_invite_event.is_shifted = True
            update_invite_event.save()
        if qs:
            update_event = DataroomMembers.objects.get(dataroom_id=pk,member_id=user.id, is_deleted=False)
            ##### - 17-11-2020
            # update_event.member_id__is_active = True
            #######
            update_event.event_timestamp = datetime.datetime.now()
            update_event.save()
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
        print(from_date)
        print(to_date)

        date_from = list(from_date.split(" ")) 
        date_to = list(to_date.split(" ")) 
        # print(date_from,date_to)
        dict_data = {
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'Jun' : 6,
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9, 
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12}
        import datetime
        # todays_date = datetime.datetime.strptime( to_date, '%Y-%m-%d')
        # first_date = datetime.datetime.strptime( from_date, '%Y-%m-%d')
        todays_date = str(date_to[3]) + '-' + str(dict_data[date_to[1]]) + '-' + str(date_to[2])
        first_date = str(date_from[3]) + '-' + str(dict_data[date_from[1]]) + '-' + str(date_from[2])
        # print(first_date)
        # print(todays_date)
        # print("FROMDATE", first_date, type(first_date), "TODATE", todays_date, type(todays_date))
        from . import utils
        dataroom = DataroomView.objects.filter(dataroom_id=pk)
        data = utils.getStartEndDateofWeek(dataroom, first_date, todays_date)
        # print(data,'kklklkl')
        return Response(data,status=status.HTTP_201_CREATED)


class GetDetaroomAllUsers(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        users_id = []
        data = []
        is_discalimer = False
        disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk)
        disclaimerSeralizer = DataroomDisclaimerSerializer(disclaimer, many=True)
        if disclaimerSeralizer.data:
            is_discalimer = True
        # dataroom_obj = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False,disclaimer_status=True)
        dataroom_obj = DataroomMembers.objects.filter(dataroom_id=pk, is_deleted=False)

        for dataroom in dataroom_obj:
            # users_id.append(dataroom.member_id)
            # for user in users_id:
                # users = User.objects.filter(id__in=users_id)
            # DataroomGroups.objects.filter()
            disclaimer1data={}
            if dataroom.disclaimer_signed_id:
                disclaimer1 = DataroomDisclaimer.objects.filter(id=dataroom.disclaimer_signed_id).last()
                # print(disclaimer1.user,'yyyyyyyyyyyyyyyyyy')
                disclaimer1data=DataroomDisclaimerSerializer(disclaimer1, many=False).data
            users = User.objects.filter(id=dataroom.member_id).first()
            serializer = UserSerializer(users,)
            usr_data = serializer.data
            usr_data['is_dataroom_admin'] = dataroom.is_dataroom_admin
            usr_data['is_la_user'] = dataroom.is_la_user
            usr_data['is_end_user'] = dataroom.is_end_user
            usr_data['disclaimer_status'] = dataroom.disclaimer_status
            usr_data['is_discalimer'] = is_discalimer
            print('dataroom.disclaimer_signed_date',dataroom.disclaimer_signed_date)
            usr_data['disclaimer_signed_date'] = dataroom.disclaimer_signed_date

            usr_data['disclaimer_signed_id'] = dataroom.disclaimer_signed_id
            usr_data['disclaimerdata'] = disclaimer1data

            try:
                usr_data['group_name'] = []
                for each in dataroom.end_user_group.all():
                    # import pdb;pdb.set_trace();
                    usr_data['group_name'].append(each.group_name)
            except:
                usr_data['group_name'] = ["Admin"]
            if len(usr_data['group_name']) <= 0:
                usr_data['group_name'] = ["Admin"]
            data.append(usr_data)
            # print('0000000000000000000000000000000',data,'5555555555555555111111111111111111111')

        return Response(data, status=status.HTTP_201_CREATED)

from .pdf_watermarking import GeneratePDF
class WatermarkingSettings(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        import logging
        logger = logging.getLogger(__name__)
        user=request.user
        userid=user.id
        watermarking = Watermarking.objects.filter(dataroom_id=pk).order_by('-id')
        for i in watermarking:
            i.user_id=userid
        serializer = WatermarkingSerializer(watermarking,many=True)
        data = serializer.data

        sample_pdf_url = 'https://newdocullystorage.blob.core.windows.net/docullycontainer/A_Sample_PDF.pdf'+sas_url

        from os import path
        from userauth import utils

        if data==[]:
            Watermarking.objects.create(attachments='https://newdocullystorage.blob.core.windows.net/docullycontainer/A_Sample_PDF.pdf'+sas_url,font_size=40,opacity=0.5,rotation=0,name='Center Center',user_id=user.id,dataroom_id=pk)
            Watermarking.objects.create(attachments='https://newdocullystorage.blob.core.windows.net/docullycontainer/A_Sample_PDF.pdf'+sas_url,font_size=40,opacity=0.5,rotation=0,name='Center Center',user_id=user.id,dataroom_id=pk)
            Watermarking.objects.create(attachments='https://newdocullystorage.blob.core.windows.net/docullycontainer/A_Sample_PDF.pdf'+sas_url,font_size=40,opacity=0.5,rotation=0,name='Center Center',user_id=user.id,dataroom_id=pk)
            watermarking = Watermarking.objects.filter(dataroom_id=pk).order_by('-id')
            serializer = WatermarkingSerializer(watermarking,many=True)
            data = serializer.data
            for i in data:
                i['attachments'] = sample_pdf_url
            return Response(data,status=status.HTTP_201_CREATED)

        # Try to generate watermark PDF
        watermark_file = "/home/cdms_backend/cdms2/Admin_Watermark/"+str(pk)+".pdf"
        try:
            ip = utils.get_client_ip(request)
            GeneratePDF(data,ip,user,pk)
            # After successful generation, set the Azure blob URL
            blob_url = 'https://newdocullystorage.blob.core.windows.net/docullycontainer/'+str(pk)+'.pdf'+str(sas_url)
            for da in data:
                da['attachments'] = blob_url
        except Exception as e:
            logger.error("GeneratePDF failed for dataroom %s: %s", pk, e, exc_info=True)
            # Fallback to sample PDF if generation fails
            for da in data:
                da['attachments'] = sample_pdf_url

        return Response(data,status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        user = request.user
        # print(user,"user")
        data = request.data
        for da in data:
            da['user'] = user.id
            da['dataroom'] = pk
            # print(da,"daa")
            dataroom=Dataroom.objects.get(id=pk)
            if dataroom.dataroom_version=="Lite":
                if not dataroomProLiteFeatures.objects.filter(dataroom_id=pk,custom_watermarking=True).exists():
                    da['custom_text']=''
            
            serializer = WatermarkingSerializer(data=da)
            # print ("serializer", serializer.is_valid())
            # print ("serializer", serializer.errors)
            if serializer.is_valid():
                serializer.update()
                # print(serializer.data,"seruu")
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
        from userauth import utils
        ip = utils.get_client_ip(request)
        watermarking = Watermarking.objects.filter(dataroom_id=pk)
        try:
            GeneratePDF(data,ip,user,pk)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("GeneratePDF failed in POST for dataroom %s: %s", pk, e, exc_info=True)
            return Response({'msg':'Watermarking settings saved but PDF preview generation failed: '+str(e)},status=status.HTTP_201_CREATED)

        return Response({'msg':'Watermarking Setting Update successfully'},status=status.HTTP_201_CREATED)

    
from .pdf_watermarking import GeneratePDF
class UpdateWatermarkingSettings(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, format=None):
        user = request.user
        data = request.data
        # print(data,"data")
        pkk=data[0]['dataroom']
        # print(data,"dataaaaa")
        for da in data:
            dataroom = da.get('dataroom')
            watermarking = Watermarking.objects.get(id=int(da.get('id')))
            # print(watermarking,"watermarking")
            serializer = WatermarkingSerializer(watermarking, data=da)
            if serializer.is_valid():
                serializer.save()
        from userauth import utils
        ip = utils.get_client_ip(request)
        watermarking = Watermarking.objects.filter(dataroom_id=dataroom)

        try:
            GeneratePDF(data,ip,user,pkk)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("GeneratePDF failed in PUT for dataroom %s: %s", pkk, e, exc_info=True)
            return Response({'msg':'Watermarking settings saved but PDF generation failed: '+str(e)},status=status.HTTP_201_CREATED)
        new_image = "https://newdocullystorage.blob.core.windows.net/docullycontainer/"+str(dataroom)+".pdf"+sas_url
        # print(new_image,"new_image")
        # pdf=new_image[0]['attachments'].split("/")
        # print(pdf,"pdf")
        dataroom_no=str(pkk)
        # print(dataroom_no,"dataroom_no")
        usrename=str(user)
        # print(usrename,"usrename")
        usrename2=usrename.replace('.com',"")
        filename=str(dataroom_no)+'.pdf'
        # print(filename,"filename")
        # content_settings=ContentSettings(content_type='application/CSV')
        return Response({'msg':'Watermarking Setting Update successfully','attachments':new_image,'file':filename},status=status.HTTP_201_CREATED)
        # else:
    # return Response({'msg':'Watermarking Setting Not Update successfully'},status=status.HTTP_400_BAD_REQUEST)

class WatermarkPreviewServe(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        preview_path = '/home/cdms_backend/cdms2/Admin_Preview_Watermarkfile/' + str(pk) + '.pdf'
        if os.path.exists(preview_path):
            with open(preview_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="' + str(pk) + '.pdf"'
                return response
        else:
            return Response({'msg': 'Watermark preview not found'}, status=status.HTTP_404_NOT_FOUND)

# class UpdateWatermarkingSettings(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )

#   def put(self, request, format=None):
#       user = request.user
#       data = request.data
#       print(data,"data")
#       pkk=data[0]['dataroom']
#       print(data,"dataaaaa")
#       for da in data:
#           dataroom = da.get('dataroom')
#           watermarking = Watermarking.objects.get(id=int(da.get('id')))
#           print(watermarking,"watermarking")
#           serializer = WatermarkingSerializer(watermarking, data=da)
#           if serializer.is_valid():
#               serializer.save()
#       from userauth import utils
#       ip = utils.get_client_ip(request)
#       watermarking = Watermarking.objects.filter(dataroom_id=dataroom)
#       print(watermarking,"watermarking")
#       #print("value of updated watermarking ===>",Watermarking.objects.filter(dataroom_id=dataroom).values('attachments'))
#       print(dataroom,"dataroom")
        
#       # if dataroom_utils.WatermarkingImage(watermarking, ip):
#       getdata=GeneratePDF(data,ip,user,pkk)
#       # new_image = Watermarking.objects.filter(dataroom_id=dataroom).values('attachments').distinct()
#       new_image = Watermarking.objects.filter(dataroom_id=dataroom).values('attachments').distinct()
#       new_image='https://docullystorage.blob.core.windows.net/docullycontainer'+getdata
#       print(new_image,"new_image")
#       # pdf=new_image[0]['attachments'].split("/")
#       # print(pdf,"pdf")
#       dataroom_no=str(pkk)
#       print(dataroom_no,"dataroom_no")
#       usrename=str(user)
#       print(usrename,"usrename")
#       usrename2=usrename.replace('.com',"")
#       filename=str(dataroom_no)+'.pdf'
#       print(filename,"filename")
#       # content_settings=ContentSettings(content_type='application/CSV')
#       return Response({'msg':'Watermarking Setting Update successfully','attachments':new_image,'file':filename},status=status.HTTP_201_CREATED)
#       # else:
#   # return Response({'msg':'Watermarking Setting Not Update successfully'},status=status.HTTP_400_BAD_REQUEST)


class DataroomDisclaimerApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, pk, format=None):
        # print ("get method called", pk)
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
        del data['change_video_ppt']
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
        # print("check the pk",pk)
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk, is_dataroom_disclaimer_default=True).first()
        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        data['disclaimer'] = dataroom_disclaimer_serializer.data

        dataroom_member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).first()
        # print("DataroomOverviewApi--------", dataroom_member)
        if dataroom_member == None:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data
            data['member']['disclaimer_status'] = None
        else:
            dataroom_member_serializer = DataroomMembersSerializer(dataroom_member, many=False)
            data['member'] = dataroom_member_serializer.data

        dataroom_overview = DataroomOverview.objects.filter(dataroom_id=pk).first()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        # print(dataroom_overview_serializer.data['dataroom_disclaimer'],'check thissss')       
        # sdata=dataroom_overview_serializer.data
        # print(sdata,'sdata')
        data['overview'] = dataroom_overview_serializer.data
        # print(data['de'],'data[overview]')

        # print("Dataaaaaaaaaaaa", data)
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        import datetime
        user = request.user
        # print("user", user.id, pk)
        data = {}
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk, is_dataroom_disclaimer_default=True).first()
        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        data['disclaimer'] = dataroom_disclaimer_serializer.data

        member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).update(disclaimer_status=True, disclaimer_signed_date=datetime.datetime.now(), disclaimer_signed_id=data['disclaimer']['id'])
        # print("Members", member)
        dataroom_overview = DataroomOverview.objects.filter(dataroom_id=pk).first()
        dataroom_overview_serializer = DataroomOverviewSerializer(dataroom_overview, many=False)
        return Response(dataroom_overview_serializer.data, status=status.HTTP_201_CREATED)





class Check_2fa_permission(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request,pk,format=None):
        otp_auth=Dataroom.objects.get(id=pk).otp_auth
        return Response(otp_auth)



class Set_2fa_permission(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self,request,pk,format=None):
        perm_obj = request.data['perm_obj']
        dataroom=Dataroom.objects.filter(id=pk)
        if dataroom.last().dataroom_version=='Lite':
            if not dataroomProLiteFeatures.objects.filter(dataroom_id=pk,two_factor_auth=True).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
        dataroom.update(otp_auth=perm_obj)
        otp_auth=Dataroom.objects.get(id=pk).otp_auth
        return Response(otp_auth)








class ArchiveDataroom(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        data = {}
        dataroom_disclaimer = DataroomDisclaimer.objects.filter(dataroom_id=pk, is_dataroom_disclaimer_default=True).first()
        dataroom_disclaimer_serializer = DataroomDisclaimerSerializer(dataroom_disclaimer, many=False)
        data['disclaimer'] = dataroom_disclaimer_serializer.data

        dataroom_member = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).first()
        # print("DataroomOverviewApi--------", dataroom_member)
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
        dataroom = self.get_object(pk, request)

        # emailer_utils.send_archive_dataroom_email(dataroom, request.user)

        return Response(data, status=status.HTTP_201_CREATED)


class ContactSupportTrial(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        user = request.user
        data = request.data
        # print("dataaa", data)
        emails = []
        members = DataroomMembers.objects.filter(dataroom_id=data.get('id'), is_deleted=False)
        for mem in members:
            emails.append(mem.member.email)
        from . import utils
        utils.send_email_trial_dataroom(data, user, emails)
        return Response(data, status=status.HTTP_201_CREATED)


class CheckFirstpage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=pk,is_deleted=False).first()
        data={}
        if member.is_dataroom_admin:
            data['overviewaccess']=True
            # data['documentaccess']=True
            data['usersandpermissionaccess']=True
            data['qnaaccess']=True
            data['updatesaccess']=True
            data['votingaccess']=True
            data['reportsaccess']=True
        elif member.is_la_user:
            group_perm = DataroomGroupPermission.objects.filter(dataroom_groups_id=member.end_user_group.first().id,dataroom=pk).last()
            # print('coming here RRRRRRRRRRRRRRR')
            data['overviewaccess']=group_perm.is_overview
            # data['documentaccess']=False
            data['usersandpermissionaccess']=group_perm.is_users_and_permission
            data['qnaaccess']=group_perm.is_q_and_a
            data['updatesaccess']=group_perm.is_updates
            data['votingaccess']=group_perm.is_voting
            data['reportsaccess']=group_perm.is_reports
        else:
            group_perm = DataroomGroupPermission.objects.filter(dataroom_groups_id=member.end_user_group.first().id,dataroom=pk).last()
            data['overviewaccess']=group_perm.is_overview
            # data['documentaccess']=False
            data['usersandpermissionaccess']=group_perm.is_users_and_permission
            data['qnaaccess']=group_perm.is_q_and_a
            data['updatesaccess']=group_perm.is_updates
            data['votingaccess']=group_perm.is_voting
            data['reportsaccess']=group_perm.is_reports
        # print('coming here RRRRRRRRRRRRRRR',data)

        return Response(data, status=status.HTTP_201_CREATED)

# class dataroomdeleteapirvgg(APIView):
#   permission_classes = (AllowAny,)

#   def get(self, request, pk, format=None):
#       # from azure.storage.blob.sharedaccesssignature import BlobSharedAccessSignature
#       # from datetime import datetime, timedelta


#       # # AZURE_ACC_NAME = 'docullystorage'
#       # # AZURE_PRIMARY_KEY = 'ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw=='
#       # # AZURE_CONTAINER = 'docullycontainer'
#       # # AZURE_BLOB='173.pdf'
#       # # expiry= datetime.utcnow() + timedelta(hours=1)
#       # # ip = utils.get_client_ip(request)

#       # # blobSharedAccessSignature = BlobSharedAccessSignature(AZURE_ACC_NAME, AZURE_PRIMARY_KEY)
#       # # sasToken = blobSharedAccessSignature.generate_blob(AZURE_CONTAINER, AZURE_BLOB, expiry=expiry, permission="r",ip=ip)
#       # # # data= Dataroom.objects.filter()
#       # # # for i in data:
#       # # # print(data[2].id)
#       # # # User.objects.filter(id=194).update(is_trial=False)
#       # if addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False).exists(): 
#       #   print('coming here 2222222222')
    
#       #   tempaddon_data=addon_plan_tempforsameday.objects.filter(user_undo_upload=False,invoice_generated=False)
#       #   for i in tempaddon_data:
#       #       print('coming here 333333333')

#       #       vote_consumed = round((Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=i.dataroom.id,is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
#       #       disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=i.dataroom.id).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
#       #       dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=i.dataroom.id,is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=i.dataroom.id, is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
#       #       total_consumed=vote_consumed + disclaimer_consumed + dataroom_consumed
#       #       dataroomsize=Dataroom.objects.filter(id=i.dataroom.id).first().dataroom_storage_allocated * 1024
#       #       if total_consumed > dataroomsize: 
#       #           print('coming here 444444444444')
#       #           extrasize=int(total_consumed)-int(dataroomsize)
#       #           addon_storage=int(i.addon_plan.storage)*1024
#       #           if int(extrasize/addon_storage)<(extrasize/addon_storage):
#       #               addonsneed=int(extrasize/addon_storage)+1
#       #           else:
#       #               addonsneed=int(extrasize/addon_storage)
#       #           print(extrasize,addonsneed,addon_storage)
#       #           for j in range(0,addonsneed):
#       #               print('coming here 555555555555')
#       #               obj=addon_plan_invoiceuserwise()
#       #               obj.user_id=i.user.id
#       #               obj.addon_plan_id=i.addon_plan.id
#       #               obj.dataroom_id=i.dataroom.id
#       #               obj.start_date=i.start_date
#       #               obj.is_deleted=False
#       #               obj.is_plan_active=True
#       #               obj.save()
#       #               plandata1=planinvoiceuserwise.objects.filter(dataroom_id=i.dataroom.id,is_latest_invoice=True).first()  
#       #               plandata1.addon_plans.add(obj)
#       #               plandata1.save()
#       #               data=planinvoiceuserwise.objects.filter(id=plandata1.id).first()
#       #               Dataroom.objects.filter(id=i.dataroom.id).update(dataroom_storage_allocated = F('dataroom_storage_allocated')+int(i.addon_plan.storage))
#       #               addon_plan_tempforsameday.objects.filter(id=i.id).update(invoice_generated=True)
#       #               send_mail_to_superadmin(subject= '1GB Data Storage #'+str(i.dataroom.id), userid=i.user.id, first_name = i.user.first_name, user_email=i.user.email ,data =data,addondata=obj,projectname=data.project_name,payment_reference='',upgradef=0,quantityflag=0)                    
#       return Response('done', status=status.HTTP_201_CREATED)

