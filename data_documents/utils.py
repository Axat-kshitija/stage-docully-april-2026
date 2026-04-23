from .models import DataroomFolder,BulkActivityTracker,Folderupload, Folderuploadinbulk
from .serializers import *
from users_and_permission.models import DataroomMembers,DataroomGroupFolderSpecificPermissions,DataroomGroups,DataroomGroupPermission,Irm_group_protection_details
from userauth.models import User
from userauth.serializers import UserSerializer
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
import logging
from django.conf import settings
from emailer.serializers import EmailerSerializer
import os
from datetime import datetime, timedelta
import requests
import urllib.request
from itertools import chain

# import win32com.client
# import xlrd
from django.db.models import Max, F, Min, Q, Sum

# import client
# import win32com.client
from dms.settings import *

import random
import string
from constants import constants
from django.shortcuts import render
from django.http import HttpResponse
from userauth.models import User_time_zone

from rest_framework.views import exception_handler

import PyPDF2
from dataroom.serializers import WatermarkingSerializer
from dataroom.pdf_watermarking import GeneratePDF
import os, uuid, sys
# import urllib.request
from dataroom.models import Watermarking,dataroomProLiteFeatures
from dataroom.serializers import WatermarkingSerializer

from azure.storage.blob import BlockBlobService,PublicAccess
from .models import *
import sys
import subprocess
import re





def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    logger = logging.getLogger(__name__)
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        return response
    else:
        # Log the actual exception so it shows up in the log file
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return HttpResponse("Internal Server Error", status=500)





def randomString2(stringLength=8):
    """Generate a random string of fixed length """
    letters= string.ascii_lowercase
    return ''.join(random.sample(letters,stringLength))

def get_all_file_paths(directory): 

    # initializing empty file paths list 
    file_paths = [] 
    # print()
    # crawling through directory and subdirectories 
    for root, directories, files in os.walk(directory):
        # print('rooot-------',root,'directories-------',directories,'files----------',files)
        for filename in files: 
            # print('-------filenamee---',filename)
            # join the two strings in order to form the full filepath. 
            filepath = os.path.join(root, filename) 
            # print('======filepath',filepath)
            file_paths.append(filepath) 

    # returning all file paths 
    return file_paths

def copy(source, destination):
    os.system("cp -r "+str(source)+" "+str(destination))

def split_link(link):
    link = str(link).split('/')[1:]
    # print(link)
    return '/'.join(link)

def get_subfolder_list(id, directory):
    data  = []
    subfolder = []
    uploaded_by = ''

    dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = id, is_root_folder=False, is_deleted=False).order_by('index')
    dataroom_folder_serializer = DataroomFolderSerializer(dataroom_folders, many=True)

    subfolder = dataroom_folder_serializer.data
    for file in subfolder:
        if file['is_folder']:
            try:
                from azure.storage.blob import BlockBlobService
                import zipfile
                from .models import Dataroom
                data_room = Dataroom.objects.get(id=file['dataroom'])
                os.mkdir(str(directory)+'/'+str(file['name']).replace(' ','\ '))
                if data_room.is_usa_blob==True:
                    block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                else:
                    block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                # block_blob_service = BlockBlobService(account_name ='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
                CONTAINER_NAME='docullycontainer'
                # print(block_blob_service, "BB")
                rootfolder_file_name =DataroomFolder.objects.filter(parent_folder=file['id'],is_root_folder=False,is_folder=False).values_list('path',flat=True)
                # print(rootfolder_file_name,"rootfolder_file_name_utils")
                for f in (rootfolder_file_name):
                    # print(f,"f")
                    file_name=f.split("/")
                    # print(file_name)
                    bb = block_blob_service.get_blob_to_path(CONTAINER_NAME, f, file_name[-1])
                    # print("yes", bb.__dict__, file_name[-1])
                    # with open("./BlockDestination.txt", "wb") as my_blob:
                    #   blob_data = bb.download_blob()
                    #   blob_data.readinto(bb)
                    with open(file_name[-1], 'rb') as ifh:
                        read_data=ifh.read()
                        with open("/home/cdms_backend/cdms2/"+directory+'/'+str(file['name'])+"/"+file_name[-1], 'wb') as fileee:
                            fileee.write(read_data)
                            get_subfolder_list(file['id'], str(directory)+'/'+str(file['name']).replace(' ','\ '))
            except FileExistsError:
                pass
            
        # else:
        #   print("in else2")
            # copy(str(split_link(file['path'])).replace('%20','\ '), str(directory).replace(' ','\ '))


def send_addon_email(subject, to, first_name):
    subject = subject
    toemail=to
    to = [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    ctx = {
        'user': first_name,
        'email': toemail,
        'subject': subject,
    }

    # message = get_template('userauth/account_verify.html').render(ctx)
    message='addon email'
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    # msg.content_subtype = 'html'
    msg.send()



def get_under_file(docu1, data):
    for doc in docu1:
        docu2 = DataroomFolder.objects.get(id=doc.id)
        docu2_serializer = DataroomFolderSerializer(docu2)
        datas = getIndexofFolder(docu2_serializer.data)
        data.append(datas)
        docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
        if len(docu3) > 0:
            get_under_file(docu3, data)
    return data

def get_under_fileee(docu1, data, member):
    for doc in docu1:
        flagg=0            
        if member.is_la_user == True or member.is_dataroom_admin == True:
            flagg=1
        else:
            # try:
            if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=doc.id,dataroom_id=doc.dataroom, dataroom_groups_id=member.end_user_group.first().id).exists():
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=doc.id,dataroom_id=doc.dataroom, dataroom_groups_id=member.end_user_group.first().id).last()
                if perm_obj.is_view_only==True:
                        flagg=1
            # except:
            #   flagg=0
        if flagg==1:    
                # docu2 = DataroomFolder.objects.get(id=doc.id)
                # docu2_serializer = DataroomFolderSerializer(docu2)
                docu = DataroomFolder.objects.filter(id = doc.id).values('name','id','is_root_folder','is_folder','path','created_date','file_size_mb','parent_folder','index').last()
                datas = getIndexofFolder1(docu)
                
                data.append(datas)
                docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
                if len(docu3) > 0:
                    get_under_fileee(docu3, data,member)
    return data

def get_under_file_with_permission(docu1, data, perm):
    for doc in docu1:
        docu2 = DataroomFolder.objects.get(id=doc.id)
        docu2_serializer = DataroomFolderSerializer(docu2)
        datas = getIndexofFolder(docu2_serializer.data)
        data.append(datas)
        docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False, id__in=perm).order_by('index')
        if len(docu3) > 0:
            get_under_file(docu3, data)
    return data

def get_under_file_datewise(docu1, data, from_date, to_date,member):
    for doc in docu1:
        flagg=0            
        if member.is_la_user == True or member.is_dataroom_admin == True:
            flagg=1
        else:
            if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=doc.id,dataroom_id=doc.dataroom, dataroom_groups_id=member.end_user_group.first().id).exists():
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=doc.id,dataroom_id=doc.dataroom, dataroom_groups_id=member.end_user_group.first().id).last()
                if perm_obj.is_view_only==True:
                        flagg=1
            # except:
            #   flagg=0
        if flagg==1:                
                docu2 = DataroomFolder.objects.get(id=doc.id)
                docu2_serializer = DataroomFolderSerializer(docu2)
                datas = getIndexofFolder(docu2_serializer.data)
                data.append(datas)
                docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False).order_by('index')
                if len(docu3) > 0:
                    get_under_fileee(docu3, data,member)
    return data

def get_under_file_withoutindex(docu1, data):
    for doc in docu1:
        docu2 = DataroomFolder.objects.get(id=doc.id)
        docu2_serializer = DataroomFolderSerializer(docu2)
        # datas = getIndexofFolder(docu2_serializer.data)
        data.append(docu2_serializer.data)
        docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_deleted=False)
        if len(docu3) > 0:
            get_under_file_withoutindex(docu3, data)
    return data

def get_under_folder(docu1, data, user, perm_obj, pk):
    for doc in docu1:
        docu2 = DataroomFolder.objects.get(id=doc.id)
        docu2_serializer = DataroomFolderSerializer(docu2)
        datas = getIndexofFolder(docu2_serializer.data)
        data.append(datas)
        if user.is_superadmin == True:
            docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_folder=True, is_deleted=False).order_by('index')
        else:
            member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=pk, is_deleted=False).first()
            if member.is_la_user == True or member.is_dataroom_admin == True:
                docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_folder=True, is_deleted=False).order_by('index')
            else:
                docu3 = DataroomFolder.objects.filter(parent_folder = doc.id, is_folder = True, is_deleted=False, id__in=perm_obj).order_by('index')
        if len(docu3) > 0:
            get_under_folder(docu3, data, user, perm_obj, pk)
    return data

def check_subfolder(docu1, data, user, perm_obj, pk):
    # print(docu1)
    for doc in docu1:
        docu2 = DataroomFolder.objects.get(id=doc.id)
        docu2_serializer = DataroomFolderSerializer(docu2)
        datas = getIndexofFolder(docu2_serializer.data)
        if datas:
            return True
    return False

def getIndexes(data):
    indexes = True
    try:
        print('---------------data00',data['name'])
    except:
        print('---------------data00',datas.name)
    if data['is_folder'] == True:
        index = str(data['index'])
    else:
        index = "0."+str(data['index'])
    parent_folder = data['parent_folder']
    while indexes == True:
        if parent_folder == None:
            indexes = False
        else:
            folder = DataroomFolder.objects.get(id=parent_folder)
            index = str(folder.index)+'.'+str(index)
            parent_folder = folder.parent_folder_id
    # print("Index------", index)
    return index

def getIndexes_with_queryset(data):
    indexes = True
    if data.is_folder == True:
        index = str(data.index)
    else:
        index = "0."+str(data.index)
    parent_folder = data.parent_folder
    while indexes == True:
        if parent_folder == None:
            indexes = False
        else:
            # folder = DataroomFolder.objects.get(id=parent_folder.id)
            folder = parent_folder
            index = str(folder.index)+'.'+str(index)
            parent_folder = folder.parent_folder
    # print("Index------", index)
    return index

def getIndexofFolder(data):
    # print("dataaaaaa", data)
    if data['is_root_folder'] == True:
        data['names'] = str(data['index'])+' '+data['name']
    else:
        data['names'] = getIndexes(data)
        data['names'] = str(data['names'])+' '+data['name']
    # print("dataaaa", data)
    return data

def getIndexofFolder1(data):
    # print("dataaaaaa", data)
    if data['is_root_folder'] == True:
        data['name'] = str(data['index'])+' '+data['name']
    else:
        data['name'] = getIndexes(data)
        data['name'] = str(data['name'])+' '+data['name']
    # print("dataaaa", data)
    # data['path']=str(data.dataroom_nameFront)+'/'+str(pathgeneratortoprintvalues(data))
    return data


def assign_view_permission(folderdata,dataroomId):
    # member = DataroomMembers.objects.filter(dataroom_id = dataroomId, is_deleted=False)

    membergroup = DataroomGroups.objects.filter(dataroom_id = dataroomId, is_deleted=False,end_user=True)
    
    print('cming rehe ((((555555555555555555')

    for i in membergroup:
        # if i.is_la_user == False or i.is_dataroom_admin == False:
        # if i.end_user_group.first():
        tempflag=folderdata['is_root_folder']
        if tempflag==False:
            if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['parent_folder'],dataroom_id=dataroomId, dataroom_groups_id=i.id).exists():
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['parent_folder'],dataroom_id=dataroomId, dataroom_groups_id=i.id).last()                  
                if perm_obj.is_no_access==False: 
                    if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['id'],dataroom_id=dataroomId,dataroom_groups_id=i.id).exists():
                        pass
                    else:
                        tempvar2=folderdata['is_folder']
                        if tempvar2==True:
                            DataroomGroupFolderSpecificPermissions.objects.create(is_upload=perm_obj.is_upload,is_no_access=False,is_access=True,is_view_only=perm_obj.is_view_only,folder_id=folderdata['id'],
                                dataroom_id=dataroomId,dataroom_groups_id=i.id,permission_given_by_id=perm_obj.permission_given_by.id,is_view_and_print=perm_obj.is_view_and_print,
                                is_view_and_print_and_download=perm_obj.is_view_and_print_and_download,is_watermarking=perm_obj.is_watermarking,is_drm=perm_obj.is_drm,is_editor=perm_obj.is_editor,
                                is_shortcut=perm_obj.is_shortcut,folder_timer_upload_ristrict=perm_obj.folder_timer_upload_ristrict,folder_timer_upload_ristrict_date=perm_obj.folder_timer_upload_ristrict_date)
                        else:
                            DataroomGroupFolderSpecificPermissions.objects.create(is_no_access=False,is_access=True,is_view_only=perm_obj.is_view_only,folder_id=folderdata['id'],dataroom_id=dataroomId,dataroom_groups_id=i.id,permission_given_by_id=perm_obj.permission_given_by.id,is_view_and_print=perm_obj.is_view_and_print,is_view_and_print_and_download=perm_obj.is_view_and_print_and_download,is_watermarking=perm_obj.is_watermarking,is_drm=perm_obj.is_drm,is_editor=perm_obj.is_editor,is_shortcut=perm_obj.is_shortcut)



def parent_folder_se(id):
    import datetime
    data=DataroomFolder.objects.filter(id=id)
    data.update(updated_date=datetime.datetime.now())
    if data.last().parent_folder:
        parent_folder_se(data.last().parent_folder.id)



def assign_view_permission1(folderdata,dataroomId):
    # member = DataroomMembers.objects.filter(dataroom_id = dataroomId, is_deleted=False)

    membergroup = DataroomGroups.objects.filter(dataroom_id = dataroomId, is_deleted=False,end_user=True)
    
    print('cming rehe ((((555555555555555555')

    for i in membergroup:
        # if i.is_la_user == False or i.is_dataroom_admin == False:
        # if i.end_user_group.first():
        tempflag=folderdata['is_root_folder']
        if tempflag==False:
            if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['parent_folder'],dataroom_id=dataroomId, dataroom_groups_id=i.id).exists():
                perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['parent_folder'],dataroom_id=dataroomId, dataroom_groups_id=i.id).last()                  
                if perm_obj.is_no_access==False: 
                    if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdata['id'],dataroom_id=dataroomId,dataroom_groups_id=i.id).exists():
                        pass
                    else:
                        tempvar2=folderdata['is_folder']
                        if tempvar2==True:
                            DataroomGroupFolderSpecificPermissions.objects.create(is_upload=perm_obj.is_upload,is_no_access=False,is_access=True,is_view_only=perm_obj.is_view_only,folder_id=folderdata['id'],dataroom_id=dataroomId,dataroom_groups_id=i.id,permission_given_by_id=perm_obj.permission_given_by.id,is_view_and_print=perm_obj.is_view_and_print,is_view_and_print_and_download=perm_obj.is_view_and_print_and_download,is_watermarking=perm_obj.is_watermarking,is_drm=perm_obj.is_drm,is_editor=perm_obj.is_editor,is_shortcut=perm_obj.is_shortcut)
                        else:
                            DataroomGroupFolderSpecificPermissions.objects.create(is_no_access=False,is_access=True,is_view_only=perm_obj.is_view_only,folder_id=folderdata['id'],dataroom_id=dataroomId,dataroom_groups_id=i.id,permission_given_by_id=perm_obj.permission_given_by.id,is_view_and_print=perm_obj.is_view_and_print,is_view_and_print_and_download=perm_obj.is_view_and_print_and_download,is_watermarking=perm_obj.is_watermarking,is_drm=perm_obj.is_drm,is_editor=perm_obj.is_editor,is_shortcut=perm_obj.is_shortcut)









def folder_perms_folder(file,parent_folder_id,group,user):
    for grp in group:
        if parent_folder_id==None:

            if file.is_root_folder==True:
                parent_folder_permission= DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()            
            else:

                parent_folder_permission= DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.parent_folder.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        else:
            parent_folder_permission= DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=parent_folder_id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        if parent_folder_permission:
            print('------------==================================================assign fodler 111')
            if not folder_permission :
                print('------------==================================================assign fodler 111 insidee')
                # print('----------folder',folder_permission.folder.name,folder_permission.is_view_only)
            #     # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
            #     # if serializer.is_valid():
            #     #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id,
                is_no_access=parent_folder_permission.is_no_access,
                is_view_only=parent_folder_permission.is_view_only,
                is_view_and_print=parent_folder_permission.is_view_and_print,
                is_view_and_print_and_download=parent_folder_permission.is_view_and_print_and_download,
                is_upload=parent_folder_permission.is_upload,
                is_watermarking=parent_folder_permission.is_watermarking,
                is_drm=parent_folder_permission.is_drm,
                is_editor=parent_folder_permission.is_editor,
                permission_given_by_id=user.id,
                is_shortcut=parent_folder_permission.is_shortcut,
                # access_revoke=da['perm']['access_revoke']
                )
                # self.assign_folder_permission(copy_file.id,copy_file.dataroom.id,parent_folder_permission,grp,user)
            else:
                print('------------==================================================assign fodler 1 elsee')
            #     # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
            #     # if serializer.is_valid():
            #     #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).update(is_no_access=parent_folder_permission.is_no_access,
                is_view_only=parent_folder_permission.is_view_only,
                is_view_and_print=parent_folder_permission.is_view_and_print,
                is_view_and_print_and_download=parent_folder_permission.is_view_and_print_and_download,
                is_upload=parent_folder_permission.is_upload,
                is_watermarking=parent_folder_permission.is_watermarking,
                is_drm=parent_folder_permission.is_drm,
                is_editor=parent_folder_permission.is_editor,
                permission_given_by_id=user.id,
                is_shortcut=parent_folder_permission.is_shortcut,
                )
                    
    return True




def folder_perms_file(file,parent_folder_id,group,user):
    
    
    for grp in group:
        if parent_folder_id==None:
        # if file.is_folder==True:
            parent_folder_permission= DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.parent_folder.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        else:
            parent_folder_permission= DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=parent_folder_id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        folder_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).first()
        if parent_folder_permission:
            print('------------==================================================assign fodler 22')
            if not folder_permission :
                # print('----------folder',folder_permission.folder.name,folder_permission.is_view_only)
            #     # serializer = DataroomGroupFolderSpecificPermissionsSerializer(data=da['perm'], context={'folder': da['id'], 'permission_given_by': user, 'dataroom': pk, 'dataroom_groups': group_id})
            #     # if serializer.is_valid():
            #     #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.create(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id,
                is_no_access=parent_folder_permission.is_no_access,
                is_view_only=parent_folder_permission.is_view_only,
                is_view_and_print=parent_folder_permission.is_view_and_print,
                is_view_and_print_and_download=parent_folder_permission.is_view_and_print_and_download,
                is_upload=False,
                is_watermarking=parent_folder_permission.is_watermarking,
                is_drm=parent_folder_permission.is_drm,
                is_editor=parent_folder_permission.is_editor,
                permission_given_by_id=user.id,
                is_shortcut=parent_folder_permission.is_shortcut,
                # access_revoke=da['perm']['access_revoke']
                )
                
            else:
                print('------------==================================================assign fodler 22 else')
            #     # serializer = DataroomGroupFolderSpecificPermissionsSerializer(folder_permission,data = da['perm'])
            #     # if serializer.is_valid():
            #     #     serializer.save()
                DataGrpSpecPerm = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=file.id,dataroom_id=file.dataroom.id,dataroom_groups_id=grp.id).update(is_no_access=parent_folder_permission.is_no_access,
                is_view_only=parent_folder_permission.is_view_only,
                is_view_and_print=parent_folder_permission.is_view_and_print,
                is_view_and_print_and_download=parent_folder_permission.is_view_and_print_and_download,
                is_upload=False,
                is_watermarking=parent_folder_permission.is_watermarking,
                is_drm=parent_folder_permission.is_drm,
                is_editor=parent_folder_permission.is_editor,
                permission_given_by_id=user.id,
                is_shortcut=parent_folder_permission.is_shortcut,
                )


    return True




# def assign_view_permission(folderdata,dataroomId):
#   member = DataroomMembers.objects.filter(dataroom_id = dataroomId, is_deleted=False)
#   print('cming rehe ((((555555555555555555')
#   folderdataa=DataroomFolder.objects.get(id=)
#   for i in member:
#       print('cming rehe ((((44444444444444')

#       if i.is_la_user == False or i.is_dataroom_admin == False:
#           print('cming rehe ((((333333333333333333',i.end_user_group.first())

#           if i.end_user_group.first():

#               if folderdataa.is_root_folder==False:
#                   print('cming rehe ((((222222222222222222')

#                   if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=folderdataa.parent_folder,dataroom_id=dataroomId, dataroom_groups_id=i.end_user_group.first().id).exists():
#                       perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=folderdataa.parent_folder,dataroom_id=dataroomId, dataroom_groups_id=i.end_user_group.first().id)                       
#                       print('cming rehe ((((111111111111111')

#                       if perm_obj.is_no_access==False: 
#                           print('cming rehe ((((9999999999999999999')
#                           DataroomGroupFolderSpecificPermissions.objects.create(is_no_access=False,is_access=True,is_view_only=True,folder_id=folderdataa.id,dataroom_id=dataroomId,dataroom_groups_id=i.end_user_group.first().id,permission_given_by_id=perm_obj.permission_given_by.id)






def email_to_data_send_notify_to_all_members_regarding_uploaded_file(data,upload_id,upload_type,user):
    import datetime
    check = Dataroom.objects.filter(id=data.dataroom_id,notify=True)
    print('-inseideeee mail email to dataroom')
    print('-inseideeee mail email to dataroom',check)
    if check:
        print('---------iiiiiiiii')
        dataroom = data.dataroom.dataroom_nameFront
        # print(upload_type,"utils data",upload_id)
        if upload_type:
            print('-------------middle23')
            upload_single_file_data = Folderuploadinbulk.objects.filter(dataroom_id= data.dataroom_id,is_folder=False,bulkupload_id=upload_id).values()[:5]
            # print("bulk upload files",upload_single_file_data)
            upload_single_file_data_count = Folderuploadinbulk.objects.filter(dataroom_id= data.dataroom_id,is_folder=False,bulkupload_id=upload_id).count()
        else:
            print('-------------middle44')
            upload_single_file_data = Folderupload.objects.filter(dataroom_id= data.dataroom_id,id=upload_id).values()
            upload_single_file_data_count = Folderupload.objects.filter(dataroom_id= data.dataroom_id,id=upload_id).count()
        # upload_single_entry = FolderuploadSerializer(upload_single_file_data, many=False).data
        # subject = "Notification of new updated files"

        print('-------------middle44',upload_single_file_data_count)
        print('-------------middle')
        subject = "New document's uploaded on Project"+ dataroom +" on Docully at " + str(datetime.date.today())
        # to = members
        print('-------------11')
        from_email = settings.DEFAULT_FROM_EMAIL
        print('-------------22')
        from constants.constants import backend_ip
        print('-------------33')
        path = DataroomFolder.objects.get(id=data.id).path
        print('-------------44')
        link = backend_ip+str(path.url)
        print('-------------55')
        # for to in members:
        # user = User.objects.get(email=user.email)
        dataaa=[user.email]
        print('-------------66')
        
        ctx = {
            'email': dataaa,
            'subject': subject,
            'dataroom':dataroom,
            'data':data,
            'upload_single_entry':upload_single_file_data,
            'user': user,
            'count':upload_single_file_data_count,
            'link':link
        }
        message = get_template('data_documents/email_to_dataroom_new_file_upload.html').render(ctx)
        # print("members-----222", dataaa)

        msg = EmailMessage(subject, message, to=dataaa, from_email=from_email)
        # msg.attach_file(data.path.path)
        msg.content_subtype = 'html'
        msg.send()
        print("email send")











def send_notify_to_all_members_regarding_uploaded_file(data,upload_id,upload_type):
        # print("data" , data)
    import datetime
    check = Dataroom.objects.filter(id=data.dataroom_id,notify=True)
    if check.exists():

        member = DataroomMembers.objects.filter(dataroom_id = data.dataroom_id, is_deleted=False,memberactivestatus=True,member__notify_recieved=True)
        members = []
        # print(member)
        for mem in member:
            if mem.is_la_user == True or mem.is_dataroom_admin == True:
                members.append(mem.member.email)

            else: 
                if mem.end_user_group.first():
                    if data.is_root_folder==False:
                        if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=data.parent_folder,dataroom_id=data.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id).exists():
                            perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=data.parent_folder,dataroom_id=data.dataroom_id, dataroom_groups_id=mem.end_user_group.first().id).last()
                            if perm_obj.is_no_access==False: 
                                members.append(mem.member.email)
        # print("members-----", member)

        # print("members-----1111", members)
        dataroom = data.dataroom.dataroom_nameFront
        # print(upload_type,"utils data",upload_id)
        if upload_type:
            upload_single_file_data = Folderuploadinbulk.objects.filter(dataroom_id= data.dataroom_id,is_folder=False,bulkupload_id=upload_id).values()[:5]
            # print("bulk upload files",upload_single_file_data)
            upload_single_file_data_count = Folderuploadinbulk.objects.filter(dataroom_id= data.dataroom_id,is_folder=False,bulkupload_id=upload_id).count()
        else:
            upload_single_file_data = Folderupload.objects.filter(dataroom_id= data.dataroom_id,id=upload_id).values()
            upload_single_file_data_count = Folderupload.objects.filter(dataroom_id= data.dataroom_id,id=upload_id).count()
        # upload_single_entry = FolderuploadSerializer(upload_single_file_data, many=False).data
        # subject = "Notification of new updated files"
        subject = "New document's uploaded on Project"+ dataroom +" on Docully at " + str(datetime.date.today())
        # to = members
        from_email = settings.DEFAULT_FROM_EMAIL
        from constants.constants import backend_ip
        path = DataroomFolder.objects.get(id=data.id).path
        link = backend_ip+str(path.url)
        for to in members:
                user = User.objects.get(email=to)
                dataaa=[]
                dataaa.append(to)       
                ctx = {
                    'email': to,
                    'subject': subject,
                    'dataroom':dataroom,
                    'data':data,
                    'upload_single_entry':upload_single_file_data,
                    'user': user,
                    'count':upload_single_file_data_count,
                    'link':link
                }
                message = get_template('data_documents/new_upload_file.html').render(ctx)
                # print("members-----222", dataaa)

                msg = EmailMessage(subject, message, to=dataaa, from_email=from_email)
                # msg.attach_file(data.path.path)
                msg.content_subtype = 'html'
                msg.send()
                print("email send")
    # print ("Eamil send.")
    else:
        pass


def getExcelOverviewData(data):
    datas = []
    for da in data:
        act = ()
        date1=da.get('created_date').strftime("%d-%m-%Y %H:%M:%S")
        # print(date1)
        # print('-------------')
        act = act + (da.get('title'), da.get('user'), da.get('event'), date1)
        datas.append(act)
    header_data = [
        'Title', 'Event By' , 'Event', 'Date'
    ]
    return header_data, datas

def getExcelDataActivityByDate(data):
    datas = []
    count=0
    for da in data: 
        act = ()
        #changes made by harish 
        count = count + 1
        uploaded_Q = User.objects.get(id=da.get('user'))
        uploaded_by = uploaded_Q.first_name + uploaded_Q.last_name
        # print('------------uplode by ',uploaded_Q)
        parent = DataroomFolder.objects.get(id = da.get('parent_folder')).name
        # group_name =group_Q.group_name


        dateobject=datetime.strptime(str(da.get('created_date')).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
        # act = act + (da.get('index'), da.get('name'), da.get('file_content_type'),str(da.get('created_date')).replace('T',' ',1))
        act = act + (str(count), da.get('name'), parent,da.get('file_content_type'),date1 , uploaded_by)

        datas.append(act)
    header_data = [
        'Index','Title','Parent Folder','Type','Created','Uploaded by'
        ]
    # print('data---------------------111111111111111111111111111111111111111111----')
    # print(datas)
    return header_data, datas

def getExcelDataDownloadedFiles(data):
    datas = []
    from datetime import datetime
    for da in data: 
        if da.get('user__first_name') and da.get('folder__name') != '' or None:
            act = ()
            # print(da.get('created_date'))
            dateobject=datetime.strptime(str(da.get('created_date')).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            # date1=dateobject.strftime("%d-%m-%Y %H:%M:%S")
            date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
            act = act + (da.get('user__first_name'),date1, da.get('folder__name'),)
            datas.append(act)
    header_data = [
        'Download By','Date','File Name'
        ]
    return header_data, datas

def getActivityByDateExport(data):
    datas = []
    for da in data: 
        act = ()
        # dates =datetime.datetime.strptime( da.get('date'),'%d/%m/%Y %H:%M:%S')
        act = act + (da.get('date'), str(da.get('dataroom_views')), da.get('documents_view'), da.get('documents_print'), da.get('documents_download'))
        datas.append(act)
    header_data = [
        'Date','Dataroom Views','Documents Viewed', 'Documents Printed', 'Documents Downloaded'
        ]
    return header_data, datas

def saveConversionPath(folder):
    # print(folder.path.url)
    source = folder.path.url
    path_list = source.split('/')
    del path_list[-1]
    # print(path_list)
    folder_path = "/".join(path_list )
    # print(folder_path)
    from . import convert
    # print("folder_path", folder_path, "source", source)
    file = convert.convert_to(folder_path, source)
    # print("file------", file)
    file_list = file.split('/home/cdms_backend/cdms2/media/')
    # print("file_listtttttt", file_list[-1])
    conversion_path = file_list[-1]
    return conversion_path

def saveExcelConversionPath(folder):
    # print(folder.path.url)
    source = folder.path.url
    path_list = source.split('/')
    del path_list[0]
    # print(path_list)
    source = "/".join(path_list)
    del path_list[-1]
    folder_path = "/".join(path_list)
    # print(folder_path)
    from . import convert
    # print("folder_path", folder_path, "source", source)
    file = convert.convert_to(folder_path, source)
    # print("file------", file)
    file_list = file.split('/home/cdms_backend/cdms2/media/'+path_list[1])
    # print("file_listtttttt", file_list[-1])
    conversion_path = file_list[-1]
    return conversion_path


def getExcelIndexReportUserWise(tree, datas,indexpermission,objid):
    # print(type(datas),"utils.py--------", tree)
    header_data=[]

    for da in tree: 
        act = ()
        dateobject=datetime.strptime(str(da.get('date')).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
        date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
        # print(str(da.get('path')),'filepath_______Rushiiiiiiiiiiii')
        if indexpermission==True:
                act = act + (da.get('index'), str(da.get('name')), da.get('type'), da.get('size'), date1, str(da.get('path')))
                datas.append(act)
                if len(da['children']) > 0:
                    getExcelIndexReportUserWise(da['children'], datas,indexpermission,objid)
                header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        else:
                act = act + (str(da.get('name')), da.get('type'), da.get('size'), date1, str(da.get('path')))
                datas.append(act)
                if len(da['children']) > 0:
                    getExcelIndexReportUserWise(da['children'], datas,indexpermission,objid)
                header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    return header_data, datas










def getExcelIndexReportUserWisenew_for_directdownload(request,tree, datas,indexpermission,member,objid):
    # print(type(datas),"utils.py--------", tree)
    from datetime import datetime
    header_data=[]

    user = request.user
    timez=''
    if User_time_zone.objects.filter(user_id=user.id).exists():
        user_zone=User_time_zone.objects.filter(user_id=user.id).last()
        timez=user_zone.time_zone.tz
    for da in tree: 
        if member.is_la_user == True or member.is_dataroom_admin == True:
            flagg=1
        else:
            perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da.id,dataroom_id=da.dataroom.id, dataroom_groups_id=member.end_user_group.first().id).first()
            print('==========================',perm_obj.folder.name)
            if perm_obj:
                if perm_obj.is_view_only==True:
                    flagg=1
                else:
                    flagg=0
            else:
                flagg=0
        if flagg==1:
            act = ()
            dateobject=datetime.strptime(str(da.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
            date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f')
            date1 = convert_to_kolkata(date1,timez)
            date1 = datetime.strftime(date1, '%Y-%m-%d %H:%M:%S')+" "+user_zone.time_zone.abbreviation
            index=getIndexes_with_queryset(da)
            if da.is_folder==True:
                file_orfolder='Folder'
            else:
                file_orfolder='File'
            # path=pathgeneratortoprint(da)
            path=pathgeneratortoprint12(da)
            if indexpermission==True:
                    # print('indexx----------------',index)
                    act = act + (index, str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
                    datas.append(act)
                    if da.is_folder==True:
                        subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False).order_by('index')
                        subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False).order_by('index')
                        # print('-----------------dataaaaa--------------folderrr',subfolder_queryset)
                        # print('----------------------------------------------folderrrrr-',subfile_queryset)
                        subfolderfiles=list(chain(subfolder_queryset,subfile_queryset))
                        # print('--------------------subfolderfiles---------------------------',subfolderfiles)
                        if len(subfolderfiles)>0:
                            getExcelIndexReportUserWisenew_for_directdownload(request,subfolderfiles, datas,indexpermission,member,objid)
                    header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
            else:
                    act = act + (str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
                    datas.append(act)
                    if da.is_folder==True:
                        subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False).order_by('index')
                        subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False).order_by('index')
                        subfolderfiles=list(chain(subfolder_queryset,subfile_queryset))
                        # print('-----------------dataaaaa--------------folderrr',subfolder_queryset)
                        # print('----------------------------------------------folderrrrr-',subfile_queryset)
                        # print('--------------------subfolderfiles---------------------------',subfolderfiles)
                        if len(subfolderfiles)>0:
                            getExcelIndexReportUserWisenew_for_directdownload(request,subfolderfiles, datas,indexpermission,member,objid)
                    header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        # else:
        #   if indexpermission==True:
        #       header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        #   else:
        #       header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        # BulkDownloadstatus.objects.filter(id=objid, is_index_report=True).update(successfilescount=F('successfilescount')+1)
        # BulkDownloadFiles.objects.create(user_id=user.id,dataroom_id=da.dataroom.id,batch_id=objid)
        # bulkprint = BulkDownloadstatus.objects.filter(id=objid, is_index_report=True).last()
        # print('----------------fail',bulkprint.failfilecount,'------success',bulkprint.successfilescount)
    # print('---------------------return ',header_data,datas)
    return header_data, datas



#     return tempp

def pathgeneratortoprintvalues(data):
    # print('-----------dataaaa',data)
    if data['is_root_folder']==False:
        dataa=DataroomFolder.objects.filter(id=data['parent_folder']).values('name', 
        'path','file_size_mb','is_folder','index','parent_folder','is_root_folder')
        # dataa = DataroomFolderSerializer(dataa)
        # print('-------------dataa22',dataa)
        # data1.extend(dataa)
        tempp=str(pathgeneratortoprint(dataa[0]))+'/'+str(data['name'])
    else:
        tempp=str(data['name'])

    return tempp




def pathgeneratortoprint(data):
    if data.is_root_folder==False:
        dataa=DataroomFolder.objects.filter(id=data.parent_folder.id,is_deleted=False).last()
        tempp=str(pathgeneratortoprint(dataa))+'/'+str(data.name)
    else:
        tempp=str(data.name)

    return tempp

def pathgeneratortoprint12(data):
    # print('data11',data)
    if data.is_root_folder==False and data.is_deleted==False:
        # dataa=DataroomFolder.objects.filter(id=data.parent_folder.id,is_deleted=False).last()
        dataa = data.parent_folder
        # print('-------dataaa',data)
        tempp=str(pathgeneratortoprint12(dataa))+'/'+str(data.name)
    else:
        tempp=str(data.name)

    return tempp

# def getExcelIndexReportUserWisenew(tree, datas,indexpermission,first_date,todays_date,member):
#   # print(type(datas),"utils.py--------", tree)
#   header_data=[]

#   for da in tree: 
#       if member.is_la_user == True or member.is_dataroom_admin == True:
#           flagg=1
#       else:
#           perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=da.id,dataroom_id=da.dataroom.id, dataroom_groups_id=member.end_user_group.first().id)
#           if perm_obj.is_view_only==True:
#               flagg=1
#       if flagg==1:
#           act = ()
#           dateobject=datetime.strptime(str(da.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
#           # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
#           date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
#           index=getIndexes_with_queryset(da)
#           if da.is_folder==True:
#               file_orfolder='Folder'
#           else:
#               file_orfolder='File'
#           path=pathgeneratortoprint(da)
#           if indexpermission==True:
#                   act = act + (index, str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
#                   datas.append(act)
#                   if da.is_folder==True:
#                       subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
#                       subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
#                       subfolderfiles=list(chain(subfolder_queryset,subfile_queryset))
#                       if len(subfolderfiles)>0:
#                           getExcelIndexReportUserWisenew(subfolderfiles, datas,indexpermission,first_date,todays_date,member)
#                   header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
#           else:
#                   act = act + (str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
#                   datas.append(act)
#                   if da.is_folder==True:
#                       subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
#                       subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
#                       subfolderfiles=chain(subfolder_queryset,subfile_queryset)
#                       if len(subfolderfiles)>0:
#                           getExcelIndexReportUserWisenew(subfolderfiles, datas,indexpermission,first_date,todays_date,member)
#                   header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
#       else:
#           if indexpermission==True:
#               header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
#           else:
#               header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']

#   return header_data, datas



def getExcelIndexReportUserWisenew(request,tree,objid, datas,indexpermission,first_date,todays_date,member):
    # print(type(datas),"utils.py--------", tree)
    header_data=[]
    from datetime import datetime
    user = request.user
    timez=''
    if User_time_zone.objects.filter(user_id=user.id).exists():
        user_zone=User_time_zone.objects.filter(user_id=user.id).last()
        timez=user_zone.time_zone.tz
    for da in tree: 
        if member.is_la_user == True or member.is_dataroom_admin == True:
            flagg=1
        else:
            perm_obj = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=da.id,dataroom_id=da.dataroom.id, dataroom_groups_id=member.end_user_group.first().id).first()
            if perm_obj:
                if perm_obj.is_view_only==True:
                    flagg=1
                else:
                    flagg=0
            else:
                flagg=0
        if flagg==1:
            act = ()
            dateobject=datetime.strptime(str(da.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
            # date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
            date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f')
            date1 = convert_to_kolkata(date1,timez)
            date1 = datetime.strftime(date1, '%Y-%m-%d %H:%M:%S')+" "+user_zone.time_zone.abbreviation
            index=getIndexes_with_queryset(da)
            if da.is_folder==True:
                file_orfolder='Folder'
            else:
                file_orfolder='File'
            # path=pathgeneratortoprint(da)
            path=pathgeneratortoprint12(da)
            if indexpermission==True:
                    # print('indexx----------------',index)
                    act = act + (index, str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
                    datas.append(act)
                    if da.is_folder==True:
                        subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
                        subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
                        # print('-----------------dataaaaa--------------folderrr',subfolder_queryset)
                        # print('----------------------------------------------folderrrrr-',subfile_queryset)
                        subfolderfiles=list(chain(subfolder_queryset,subfile_queryset))
                        # print('--------------------subfolderfiles---------------------------',subfolderfiles)
                        if len(subfolderfiles)>0:
                            getExcelIndexReportUserWisenew(request,subfolderfiles,objid, datas,indexpermission,first_date,todays_date,member)
                    header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
            else:
                    act = act + (str(da.name), file_orfolder, da.file_size_mb if da.file_size_mb != None else 0, date1, str(path))
                    datas.append(act)
                    if da.is_folder==True:
                        subfolder_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=True, is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
                        subfile_queryset=DataroomFolder.objects.filter(parent_folder = da.id,is_folder=False,is_deleted=False, created_date__gte=first_date, created_date__lte=todays_date).order_by('index')
                        subfolderfiles=list(chain(subfolder_queryset,subfile_queryset))
                        # print('-----------------dataaaaa--------------folderrr',subfolder_queryset)
                        # print('----------------------------------------------folderrrrr-',subfile_queryset)
                        # print('--------------------subfolderfiles---------------------------',subfolderfiles)
                        if len(subfolderfiles)>0:
                            getExcelIndexReportUserWisenew(request,subfolderfiles,objid, datas,indexpermission,first_date,todays_date,member)
                    header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        # else:
        #   if indexpermission==True:
        #       header_data = ['Index','Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        #   else:
        #       header_data = ['Name','Type', 'Size(in MB)', 'Date Uploaded', 'Path']
        BulkDownloadstatus.objects.filter(id=objid, is_index_report=True).update(successfilescount=F('successfilescount')+1)
        BulkDownloadFiles.objects.create(user_id=user.id,dataroom_id=da.dataroom.id,batch_id=objid)
        bulkprint = BulkDownloadstatus.objects.filter(id=objid, is_index_report=True).last()
        print('----------------fail',bulkprint.failfilecount,'------success',bulkprint.successfilescount)
    # print('---------------------return ',header_data,datas)
    return header_data, datas



# def getExcelbulkdownloadReport(data, datas,indexpermission):
#   # print(type(datas),"utils.py--------", tree)
#   header_data=[]

#   for da in data: 
#       act = ()
#       dateobject=datetime.strptime(str(da.get('date')).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
#       # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
#       date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
#       # print(str(da.get('path')),'filepath_______Rushiiiiiiiiiiii')
#       if indexpermission==True:
#               act = act + (da.get('index'), str(da.get('name')),da.get('file_size_mb'), date1, str(da.get('path')),str(da.get('statuss')))
#               datas.append(act)
#               header_data = ['Index','Name', 'Size(in MB)', 'Date Time', 'Path','Download Status']
#       else:
#               act = act + (str(da.get('name')), da.get('file_size_mb'), date1, str(da.get('path')),str(da.get('statuss')))
#               datas.append(act)
#               header_data = ['Name', 'Size(in MB)', 'Date Time', 'Path','Download Status']
#   return header_data, datas




def pathgeneratortoprint1(data):
    # print('-----------dataaaa',data)
    if data['is_root_folder']==False:
        dataa=DataroomFolder.objects.filter(id=data['parent_folder']).values('name', 
        'path','file_size_mb','is_folder','index','parent_folder','is_root_folder')
        # dataa = DataroomFolderSerializer(dataa)
        # print('-------------dataa22',dataa)
        # data1.extend(dataa)
        tempp=str(pathgeneratortoprint1(dataa[0]))+'/'+str(data['name'])
    else:
        tempp=str(data['name'])

    return tempp




def getExcelbulkdownloadReport(data, datas,indexpermission,dataroom):
    # print(type(datas),"utils.py--------", tree)
    print('00000000000000000',dataroom)
    header_data=[]
    from datetime import datetime
    for da in data: 
        act = ()
        try:
            dateobject=datetime.strptime(str(da['date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        except:
            dateobject=datetime.strptime(str(da['date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
        # date1=dateobject.strftime("%Y-%d-%m %H:%M:%S")
        try:
            date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
        except:
            date1 = datetime.strptime(str(dateobject), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
        path = str(dataroom.dataroom_nameFront)+'/'+str(pathgeneratortoprint1(da))
        # print(str(da.get('path')),'filepath_______Rushiiiiiiiiiiii')
        if indexpermission==True:
                act = act + (da['index'], str(da['name']),da['file_size_mb'], date1, path,str(da['statuss']))
                datas.append(act)
                header_data = ['Index','Name', 'Size(in MB)', 'Date Time', 'Path','Download Status']
        else:
                act = act + (str(da['name']), da['file_size_mb'], date1, path,str(da['statuss']))
                datas.append(act)
                header_data = ['Name', 'Size(in MB)', 'Date Time', 'Path','Download Status']
    return header_data, datas




def getIndexofFolder(data):
    # print("dataaaaaa", data)
    if data['is_root_folder'] == True:
        data['names'] = str(data['index'])+' '+data['name']
    else:
        data['names'] = getIndexes(data)
        data['names'] = str(data['names'])+' '+data['name']
    # print("dataaaa", data)
    return data

def send_email_to_members(groups, members, update):
    check = Dataroom.objects.filter(id=update.dataroom_id,notify=True)
    if check.exists():

        if len(groups) > 0:
            userss = DataroomMembers.objects.filter(end_user_group__in=groups,dataroom_id = update.dataroom_id, is_deleted=False,memberactivestatus=True,member__notify_recieved=True)
        elif len(members) > 0:
            userss = DataroomMembers.objects.filter(id__in=members, is_deleted=False,memberactivestatus=True,member__notify_recieved=True)
        else:
            return True

        to = []
        for user in userss:
            to.append(user.member.email)
        # print("to------------",to)
        # subject = "Update in Project "+str(update.dataroom.dataroom_nameFront)+" on Docully"+str(update.subject)

        subject = update.subject
        from_email = settings.DEFAULT_FROM_EMAIL
        from constants.constants import backend_ip
        if update.file:
            path = DataroomFolder.objects.get(id=update.file.id).path
            link = backend_ip+str(path.url)
        else: 
            link = None


        for t in to:
            dataaa=[]
            dataaa.append(t)        

            ctx = {
            'email': t,
            'subject': subject,
            'messages': update.message,
            'link': link,
            'update':update
            }

            message = get_template('data_documents/new_updates.html').render(ctx)
            msg = EmailMessage(subject, message, to=dataaa, from_email=from_email)
            msg.content_subtype = 'html'
            msg.send()
            data = {
                'subject':subject, 
                'user' : update.user_id, 
                'from_email':from_email, 
                'body_html':message, 
                'emailer_type': 8, 
                'to_email': t
            }
            emailer_serializer = EmailerSerializer(data=data)
            if emailer_serializer.is_valid():
                emailer_serializer.save()
        return True
    else:
        pass

# def excel_to_pdf(watermark, group_folder, conversion_path, ip):
#   path_list = conversion_path.split("/")
#   del path_list[0]
#   name = path_list[-1]
#   path = '/'.join(path_list)
#   workdir=path
#   # file_location= os.path.join(workdir, 'input_'+monthyear+'.xlsx')
#   # print ("The names of combined   file_location is",file_location)
#   workbook=xlrd.open_workbook(workdir)

#   #open a sheet to import data 
#   sheet=workbook.sheet_by_index(0)
#   sheet.Visible=1

#   # Now to print the number of worksheets in the excel file 
#   print ("The number of worksheets are ", workbook.nsheets)
#   excel = client.DispatchEx("Excel.Application")

#   print ("The names of worksheets are", workbook.sheet_names())
#   out_folder = "xls.pdf"

#   # in_file = os.path.abspath(path)
#   # print("in_file is", in_file)
#   # out_file = os.path.abspath(out_folder)
#   # print("out_file is", out_file)
#   docu=excel.Workbooks.Open(path)
#   print("Exporting", in_file)
#   docu.SaveAs(out_folder, FileFormat=56)
#   docu.Close()

def notify_document_updates(data):
    # print("data" , data)
    check = Dataroom.objects.filter(id=data.dataroom_id,notify=True)
    if check.exists():
        member = DataroomMembers.objects.filter(dataroom_id = data.dataroom_id, is_deleted=False,memberactivestatus=True,member__notify_recieved=True)
        # print("members-----", member)
        members = []
        for mem in member:
            members.append(mem.member.email)
        # print("members-----", members)
        dataroom = data.dataroom.dataroom_nameFront
        subject = "Notification of File"
        # to = members
        from_email = settings.DEFAULT_FROM_EMAIL
        from constants.constants import backend_ip
        path = DataroomFolder.objects.get(id=data.id).path
        link = backend_ip+str(path.url)
        for to in members:
            dataaa=[]
            dataaa.append(to)   
            ctx = {
                'email': to,
                'subject': subject,
                'dataroom':dataroom,
                'data':data,
                'link':link
            }
            message = get_template('data_documents/new_upload_file.html').render(ctx)
            msg = EmailMessage(subject, message, to=dataaa, from_email=from_email)
            # msg.attach_file(data.path.path)
            msg.content_subtype = 'html'
            msg.send()
        # print ("Email send.")
    else:
        pass


def send_mail_to_coordinator(qna_obj, category_obj):
    subject = "Assigned a Question******"
    if category_obj.user.notify_recieved:
        to = [category_obj.user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        ctx = {
            'email': to,
            'subject': subject,
            'qna_obj':qna_obj,
            'category_obj':category_obj
        }
        message = get_template('emailer/assigned_question_mail.html').render(ctx)
        msg = EmailMessage(subject, message, to=to, from_email=from_email, cc=[qna_obj.user.email])
        # msg.attach_file(data.path.path)
        msg.content_subtype = 'html'
        msg.send()
    else:
        pass
    # print ("Email send.")




def convert_to(folder, source):
    from .utils import randomString2
    randomname = randomString2(5)
    args = [libreoffice_exec(),f'\"-env:UserInstallation=file:///tmp/LibreOffice_Conversion_{randomString2(5)}\"', '--headless', '--convert-to', 'pdf', '--outdir', folder, source]
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())
    tt=1
    if filename:
        return filename.group(1)
    else:
        return tt


def libreoffice_exec():
# TODO: Provide support for more platforms
    if sys.platform == 'darwin':
        return '/usr/bin/soffice'
    return 'libreoffice'

def forblob_notfoundissue(file_data):
                                if str(file_data.get('name')).split('.')[-1]=='xlsx' or str(file_data.get('name')).split('.')[-1]=='csv' or str(file_data.get('name')).split('.')[-1]=='xls' or str(file_data.get('name')).split('.')[-1]=='txt' or str(file_data.get('name')).split('.')[-1]=='pptx' or str(file_data.get('name')).split('.')[-1]=='ppt' or str(file_data.get('name')).split('.')[-1]=='docx' or str(file_data.get('name')).split('.')[-1]=='doc' or str(file_data.get('name')).split('.')[-1]=='odt':
                                    import os
                                    filepath=file_data['path']
                                    # print(filepath,"filepath")
                                    pathsplit=filepath.split('/')
                                    # print(pathsplit,"pathsplit")
                                    from azure.storage.blob import BlockBlobService, PublicAccess,ContentSettings
                                    pathu=pathsplit[-2].replace("%20", " ")+"/"+pathsplit[-1].replace("%20", " ")
                                    # print(pathu,"pathu")
                                    
                                    block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                                    container_name='docullycontainer'
                                    block_blob_service.get_blob_to_path(container_name, pathu, pathsplit[-1])
                                    with open(pathsplit[-1], 'rb') as ifh:
                                        read_data=ifh.read()
                                        with open("/home/cdms_backend/cdms2/DocFile_server/"+pathsplit[-1], 'wb') as fileee:
                                            fileee.write(read_data)
                                            # print("yes done pptx 8888888888888888888888888888888888888888888888899999999999999999999999999999999")

                                    convert_to('/home/cdms_backend/cdms2/server_DocFile/',  "/home/cdms_backend/cdms2/DocFile_server/"+pathsplit[-1])
                                    fileext=pathsplit[-1].split('.')
                                    fileext[-1]='pdf'
                                    fileext='.'.join(fileext)

                                    blob_na=pathsplit[4]+"/"+fileext
                                    # print(blob_na,"blob_na")
                                    block_blob_service.create_blob_from_path(
                                    container_name,
                                    blob_na,
                                    "/home/cdms_backend/cdms2/server_DocFile/"+fileext,content_settings=ContentSettings(content_type='application/pdf'))
                                    os.remove(pathsplit[-1])
                                    os.remove('/home/cdms_backend/cdms2/DocFile_server/'+pathsplit[-1])
                                    os.remove('/home/cdms_backend/cdms2/server_DocFile/'+fileext)


#Raveena Code#####
# from azure.common import AzureException, AzureMissingResourceHttpError
def downloadtwo(request,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid):
    user=request.user
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except Exception as e:
            print('permissionnnnnnn----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            pass
        
    data_room=Dataroom.objects.get(id=dataroomid)
    if flagch==1:       
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
            # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
            indexx=getIndexes(datas)

            # filedata = dataroom_folder_serializer.data
            filename =  str(datas['name'])  # be careful with file names
            # if preindex=='' and pindex=='':
            #   filename = index+"_"+str(filename)
            # elif pindex=='':
            #   filename = preindex+'.0.'+index+"_"+str(filename)
            # elif preindex=='':
            #   filename = pindex+'.0.'+index+"_"+str(filename)
            # else:
            #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)
            # file_name_list=list()
            # file_name1 = datas['path'].split("/")
            # file_name_list.append(file_name1[4])
            # file_name_list.append(file_name1[5])
            # print('------filename111111111111111',file_name_list)
            print('------urllllllllllllllllllllllllllllllllllllll',url)
            file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
            file_name=file_name.replace("%E2%80%93","–")
            print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
            # print('----------pathhhhhhm beforeeeeeeeeee',datas['path'],sas_url)
            # datas['path']=datas['path'].replace("%E2%80%93", "")
            # print('----------pathhhhhhafterrrrrr',datas['path'])
            print('------filename befire %20 afterrrrrrrr',file_name)
            if docaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")

                if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            if exelaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")
                if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            tempname=filename.split('.')
            # print('--------------------------------------',filename)
            print(datas,filename,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
            if dataindex==True:
                filename=str(indexx)+' '+str(filename)
                # print(filename,'===============')
                # print(file_name,'@@@@@@@@@@@@@@@@@')

            file_path = os.path.join(dest_folder, filename)
            # print('-----------file patghhg',file_path)
            # BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            # print('--------------------filennameeeee---------',filename)
            try:
                if (tempname[-1]=='pdf' or tempname[-1]=='PDF') :
                    # file_path = os.path.join(dest_folder, filename)
                    userid=user.id
                    watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
                    if watermarking.exists() and watermakingcheck :      
                        for i in watermarking:
                            i.user_id=userid
                        serializer = WatermarkingSerializer(watermarking,many=True)
                        data = serializer.data
                    else:
                        data=False
                    if data:
                        
                        tempfile='temp'+str(random.randint(0, 10000))
                        temp_path = os.path.join(dest_folder, tempfile)
                        if data_room.is_usa_blob==True:
                            sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                            block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
                        else:
                            sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                            block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                        
                        # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                        container_name ='docullycontainer'
                        print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTTttttttttttttttttt')
                        # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                        # if member.is_la_user or member.is_dataroom_admin:
                        #     block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                        # else:

                        if Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                            red=Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                            url=(red.file).split('/')
                            file_namee=url[-2]+'/'+url[-1]

                            block_blob_service.get_blob_to_path(container_name, file_namee, temp_path)
                        else:
                            block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)

                        from userauth import utils
                        ip = utils.get_client_ip(request)
                        try:
                            GeneratePDF(data,ip,user,dataroomid)
                            watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
                            outputfile=file_path
                            # print(str(outputfile),'++++++++++++++++++++++++++++++')
                            pdf_writer=PyPDF2.PdfWriter()
                        
                            if (os.path.exists(temp_path)):
                                with open(temp_path, 'rb') as fh:
                                    pdf=PyPDF2.PdfReader(fh,strict=False)
                                    with open(watermarkfile,'rb') as watermarkfile:
                                        watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile,strict=False)
                                        for i in range(len(pdf.pages)):
                                            p=pdf.pages[i]
                                            p.merge_page(watermarkfile_pdf.pages[0])
                                            pdf_writer.add_page(p)
                                        # watermarkfile.close()
                                        # fh.close()
                                        with open(outputfile,'wb') as outputfileeee:
                                            pdf_writer.write(outputfileeee)
                                    # outputfileeee.close()                                 
                                    os.remove(temp_path)
                        except:
                            os.remove(temp_path)
                            # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            # if member.is_la_user or member.is_dataroom_admin:
                            #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            # else:

                            if Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                                red=Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                                url=(red.file).split('/')
                                file_namee=url[-2]+'/'+url[-1]

                                block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                            else:
                                block_blob_service.get_blob_to_path(container_name, file_name ,file_path)

                        if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            pass
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                    else:
                        # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                        if data_room.is_usa_blob==True:
                            sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                            block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                        else:
                            sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                            block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                        
                        container_name ='docullycontainer'
                        print('--------------except pdf  download file location',file_path)
                        # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        # if member.is_la_user or member.is_dataroom_admin:
                        #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        # else:

                        if Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                            red=Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                            url=(red.file).split('/')
                            file_namee=url[-2]+'/'+url[-1]

                            block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                        else:
                            block_blob_service.get_blob_to_path(container_name, file_name ,file_path)

                        if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            pass
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                else:
                    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                    if data_room.is_usa_blob==True:
                        block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                    else:
                        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                    
                    container_name ='docullycontainer'
                    try:

                        print('-------------------------------filename============',file_name)
                        print('-------------------------------filepath============',file_path)

                        if Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).exists():
                            red=Redacted_Pdf.objects.filter(folder_id=datas['id'],is_deleted=False,is_deleted_permanent=False,current_version=True).last()
                            url=(red.file).split('/')
                            file_namee=url[-2]+'/'+url[-1]
                            file_path=file_path.split('.')
                            file_path[-1]='pdf'
                            temp_file_name='.'.join(file_path)
                            block_blob_service.get_blob_to_path(container_name, file_namee, temp_file_name)
                        else:
                            block_blob_service.get_blob_to_path(container_name, file_name ,file_path)

                        if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            pass    
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                    except Exception as e:
                        print('11111111111111111111111111111111111111111111111111111111----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                        BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            # except AzureMissingResourceHttpError:
            #   if os.path.exists(temp_path):
            #       os.remove(temp_path)
            #   try:
            #       forblob_notfoundissue(datas)
            #       if (tempname[-1]=='pdf' or tempname[-1]=='PDF') and watermakingcheck:
            #           # file_path = os.path.join(dest_folder, filename)
            #           userid=user.id      
            #           watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
            #           for i in watermarking:
            #               i.user_id=userid
            #           serializer = WatermarkingSerializer(watermarking,many=True)
            #           data = serializer.data
            #           if data:
            #               tempfile='temp'+str(random.randint(0, 10000))
            #               temp_path = os.path.join(dest_folder, tempfile)
            #               block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
            #               container_name ='docullycontainer'
            #               # print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTT')
            #               block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
            #               from userauth import utils
            #               ip = utils.get_client_ip(request)
            #               try:
            #                   GeneratePDF(data,ip,user,dataroomid)
            #                   watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
            #                   outputfile=file_path
            #                   # print(str(outputfile),'++++++++++++++++++++++++++++++')
            #                   pdf_writer=PyPDF2.PdfFileWriter()
                            
            #                   if (os.path.exists(temp_path)):
            #                       with open(temp_path, 'rb') as fh:
            #                           pdf=PyPDF2.PdfFileReader(fh,strict=False)
            #                           with open(watermarkfile,'rb') as watermarkfile:
            #                               watermarkfile_pdf=PyPDF2.PdfFileReader(watermarkfile,strict=False)
            #                               for i in range(pdf.getNumPages()):
            #                                   p=pdf.getPage(i)
            #                                   p.mergePage(watermarkfile_pdf.getPage(0))
            #                                   pdf_writer.addPage(p)
                                            
            #                               with open(outputfile,'wb') as outputfileeee:
            #                                   pdf_writer.write(outputfileeee)
            #                                   outputfileeee.close()
            #                                   watermarkfile.close()
            #                                   fh.close()
            #                                   os.remove(temp_path)
            #               except:
            #                   os.remove(temp_path)
            #                   block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

            #           else:
            #               block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
            #               container_name ='docullycontainer'
            #               block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #       else:
            #           block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
            #           container_name ='docullycontainer'
            #           try:
            #               block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #           except Exception as e:
            #               print('22222222222222222222222222222222222222222222222222----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            #               BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #   except Exception as e:
            #       if os.path.exists(temp_path):
            #           os.remove(temp_path)
            #       print('33333333333333333333333333333333333333333333333333333333333----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            #       BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            except Exception as e:

                    print('4444444444444444444444444444444444444444444444444444444444----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                    BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            
            # user = request.user
            # bulk_activity_tracker = BulkActivityTracker()
            # bulk_activity_tracker.user_id = user.id
            # bulk_activity_tracker.save()

            # urllib.request.urlretrieve(url,file_path)


            # r = requests.get(url, stream=True)
            # if r.ok:
            #     print("saving to", os.path.abspath(file_path))
            #     with open(file_path, 'wb') as f:
            #         for chunk in r.iter_content(chunk_size=1024 * 8):
            #             if chunk:
            #                 f.write(chunk)
            #                 f.flush()
            #                 os.fsync(f.fileno())
            # else:  # HTTP status code 4XX/5XX
            #     print("Download failed: status code {}\n{}".format(r.status_code, r.text))


import json
def donwload_irm_files(outputfile,access_token,file_name1,temp_name,datas_id,user_id,dataroomid,bulkid,objid,data,alldata,file_name,group_s):
    # data=DataroomFolder.objects.get(id=pk)
    # url=data.path.url
    # file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
    # file_name=file_name.replace("%E2%80%93","–")
    # print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
    # file_name1=url.split("/")[-1]

    # # if data_room.is_usa_blob==True:
    # #     sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

    # #     block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
    # # else:
    # sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    # container_name ='docullycontainer'


    # temp_path = '/home/cdms_backend/cdms2/media/'+str(file_name1)
    temp_path = outputfile
    # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)


    # url = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

    # # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAMhWAA.BQABAwEAAAADAOz_BQD0_yvJVyFPy09dlLYE8P7FyKqXcD76OrOYiAnp5R7OCRD5huWdkmnEo4S7ItdyCh8ill-dPcMcMD614aTr0irmNzYbPE8bElvaTGhfs73FgVxnXtKOyrTUBsopx_eas3yfB-HkA3neQI6t_2lLwb-lF-TozGv6nVi0htsMrMF-oZiCqA2_kKV66L16tBeL2KC_9BFKmRcx8_2Oe_CgpnuR6XJctwIkqlDxlmhjSsnNUJ11cM7KV5LfE8abGVy5AkGyWQedq3E2H4a5PLfw2pHFWCdUIY17fBiqcGLyEg04zcZiwReZ5K5LIQwl6NVgkl6lvH2YCIX142fUXxGz7qCGj-JaBbTAvf8tW2o_33Isj8eaYollOFjs4wpeFV-bOrwlaXjvNOrM-nWkVzx2WiBtfhkglzONbCjR8KK4JEkksJyBBYr83IfldoUotHeUtRPj6zkRnVzVAwxiz_EYnwN_CXbrwFwLklL1qdZ4qgvMdUua9glZ8T6lZsy5Vt07detJNic9dy9Y4bBku5WoqCxw_qX5JdvvDJim3b_1lS-8xk3_kyByfTXjhvX8fTQKs7oujwSJ-b0HRtnkhJWd5A0AbIIQUB-p-I7GTw1SB39Czn3ncPH9Hrs5doNtS2A0I7ZZJ9Udzbg4dCMbJ7R9bnupmU0NNq08O83shzhFwBuGEFdd_zgef6FrNBgTDjS2CbpyA0Yl-QGccVjnwAB2Qr28A3AEoK69gE5O4balu73Nq18kjwUAA2XMEVd_WSvPQXCweKVWXR309APPxwDQzXAdhvUjj6R8FI579DsDK2ErbcDM2pAy3j3d7vm6CtANkk2DS9vbA3Sq_MwCblok3x2blscH5EsThvmJJgJyk7lnheWiopWFyqikJy-HZ9etOx3oU97JYlmMRHtsXxkhcDt5tuyKpAjRAfgP49GdBqMYGVGkdcJ19yhOZOT0JecxPRke-iLtRRESKRx6RhwQN8y0B7dMEWuQERwDBTOgT3QRK_URsenTZ2mQWcIoiIDX39U5d8-esswSKucd_oE6llD0fOG8VAqbQcX0OlMn1VZXKBrkLQ2qYKDOKeBktGvfBQLPCVuk4LgmAzdzntL6e8GceKlf_xS3mzX5hcu6dYJisuqTpfV3N-b26xDM0E_WvuWAS0it6coCxjdirowMgl3d-FL5Mao0SBVTbYrFBKkvqN9jidocGSPX0eUGh220aJwXQ-Pf3fJ1LYhVwIcNEU5d9siQunpFKEV-2aS0ONRGD5J7aGaF-LmBotokMiR17wrH0nVWN43UnrcsBNwIc4TgIOq9Ai-CK4Xr1vyy6lgrdPG7tDc0zm03OIvrO01KMtM6wLR6YLKufAjzjx1EhiUxjoKh5FDObFzw0sNyyTknAJ85Ig-NbBH96LD5fBfkJ8Dgg5dP9gvs-j7j'
    # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_1yL9mBiz2zU44ISLb7kTNdiyEqjPiUu4votWAYP8slKmFYuhW0oUN5SjXx5RM580OdJvMOSREoSXBX7ckpMhiOwvtYowTpk88v3O-LXk7Wwa7pJVnF0noyRMyebcmwp29VmL1mbAmNnG-4C6YvqxLnZdIpIAy_-i2Zd55ALtYfK9BTMycotiDMlPgPzsI584n5YkM3NiLhTKICn5nVf9bAm6-TMmSVWQVJkSK4nf_L9h-V5aJk1C_9HA7CQrrh1e91qVKDKOH-I2AZh7zSlTNnV4VjzULDUtmJ8H46U-hpTVjszeNmhMzsVx-_yktGZcghLObXBA6Psfvgzorg6shEQAr0fBjcdJbVnW5n5m9f7rEbDs_gvVxIJfxXaYuYFAV1N1Ijmu-NHXU65tmuvAsEWIx6M048B05RnxHy06WdHOrxWWky4pNFnIVqHDS0fG7Gerb4puAg3mcZ2Os5RDJw9zV3MrdyhdtnSlknPv6daB9UCinTDXr9blFmSLHqv5tq3bAmMT8i-Ef0y_hTabX87ui5-TbY3E2b_1LjpFDZmyr-uq0O-AmLj7MKbPU_W3oZ5_WG-vi4-Iba6txIGIG-IjJhB5TijN8dhAXdLj8OeEK1EkSFC7U5dSvPgQUahqtK5iDwYbzuM10IzyueqxddYxzsStq1oQIJNkZ4o8NR7XeeJip48D0q6c7dCrtqIjBCISBLci3l7SfO8yjVam6bNePz1SWuPNWe8PUE3AQXvORkzg8XBf2dQ6eEmuJxR8kGtsb8Eo4CTE3ZEx6Y9eUEprGmITZ6-qUF3pryDTdgM4LIi8h4LrTNJ-k9ItwEfJDawLVtkO7_7s6iu3j-Y1Azy9ZTNMi0nJesZLXEzj_mTB7EANnCdJGVGydGIHGmByeLfAgaLebAyzIv3kSfDG0hh1D7d8NAKKFWYktPSlab8sZbeYAFEDfyiw6ffBxqxYWpgIwX5ayScPlC6cDVlkQQ4-8m1uxqPJUXTgb0ufP8gBdkhZ6xyupqPqCjsW7fefI_9kiwLcQw8eNp-fmfk-6uTJ7LK_WEVyXLj-2qDZEr9Ah2S5G35iCYC0IrtmxHuWk8U4W5hNWFL1_PDlTBuymnIVVVCmGPn7O072zoygo94QoAz3xnDzQec2jPgkfVqeWThwsqgj_gU7_jS_cxGqf5ta70IhwA874-lkeS3NH_1NgEm5YB3890RzMuyNhhO1TgZTbim1vV1NZaO8yW3K_rBKSmdCAxOZUclMRpD0Yi63QrvQbjSvfa5BiwYg-AGHlBC6DaLek9zwevzF0QH_xjWsFBG6v4R0sI_lY_h7x3zjUPr_sfeMd6MISP0c1WT0mPzKcxP4kqFApab5EJyF2jz5NtQdggA6hQvcd7V2rwHST_k-4eLBFhaQ3Tm0zKM04I5mT23Ww8v'
    # headers = {
    #   'Content-Type': 'application/x-www-form-urlencoded',
    #     'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
    #     }

    # response = requests.request("GET", url, headers=headers, data=payload)
    # resp=response.json()
    # access_token=resp['access_token']
    # access_token=resp['access_token']
    print('--------------temp fileeee',temp_path)

    print('-----------------------access tokennn',access_token)
    import magic
    # target_file = open(temp_path, "rb")



    # application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    mime_type = magic.from_file(temp_path, mime=True)


    print('file nameee==============',file_name1)
    print('file nameee==============temp_name',temp_name)

    url1 = f"https://graph.microsoft.com/v1.0/me/drive/root:/{temp_name}:/content"

    # payload = "<file contents here>"
    headers1 = {
      'Authorization': f'Bearer {access_token}',
      # 'Content-Type': mime_type
    }
    # print('-----------------headers',headers1)

    with open(temp_path, 'rb') as file_data12:
        response1 = requests.request("PUT", url1, headers=headers1, data = file_data12,verify=False)
    # response = requests.request("PUT", url, headers=headers, data=payload)

        file_resp=response1.json()
        # print('responsee-------',file_resp)
        file_id=file_resp['id']
        print('------------file____id',file_id)

        download_url=file_resp['@microsoft.graph.downloadUrl']
    #     url3 = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink"

    #     payload1 = json.dumps({
    #       "type": "edit",
    #       "scope": "anonymous"
    #     })
    #     headers3 = {
    #       'Authorization': f'Bearer {access_token}',
    #       'Content-Type': 'application/json'
    #     }
    #     response3 = requests.request("POST", url3, headers=headers3, data=payload1)
    #     print('-----------333333',response3.json())

    #     resp3=response3.json()
    #     web_url=resp3['link']['webUrl']

    # return Response({"url": web_url,'id':file_id}, status=200)
        irm_prot=Irm_group_protection_details.objects.filter(dataroom_groups_id=group_s.dataroom_groups.id).last()
        print('----------------------irm downloadd()()()()()(())()()',irm_prot.last_name)
        url4 = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/assignSensitivityLabel"

        payload4 = json.dumps({
          "sensitivityLabelId": "1dca0132-b36d-4108-99cc-4f0825fe67bf",
          "assignmentMethod": "standard",
          "justificationText": "test_justifircation"
        })
        headers4 = {
          'Authorization': f'Bearer {access_token}',
          'Content-Type': 'application/json'
        }


        response4 = requests.request("POST", url4, headers=headers4, data=payload4)

        print("------------------senstivity response",response4.text)
        
        headers5 = {
          'Authorization': f'Bearer {access_token}',
          }
        from .tasks import irm_file_bulk_download
        irm_file_bulk_download.apply_async( kwargs={
            "file_name12": temp_path,
            "download_url": download_url,
            "headers5": headers5,
            "datas_id":datas_id,
            "user_id":user_id,
            "dataroomid":dataroomid,
            "bulkid":bulkid,
            "objid":objid,
            "data":data,
            "alldata":alldata,
            "file_name":file_name
        },countdown=20*60)
        



        









def donwload_irm_files_single(outputfile,access_token,file_name1,temp_name,datas_id,user_id,dataroomid,bulkid,objid,data,alldata,file_name,group_s):
    # data=DataroomFolder.objects.get(id=pk)
    # BulkDownloadstatus.objects.filter(id=objid).update(filename=file_name1)
    # url=data.path.url
    # file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
    # file_name=file_name.replace("%E2%80%93","–")
    # print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
    # file_name1=url.split("/")[-1]

    # # if data_room.is_usa_blob==True:
    # #     sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

    # #     block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
    # # else:
    # sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    # container_name ='docullycontainer'


    # temp_path = '/home/cdms_backend/cdms2/media/'+str(file_name1)
    temp_path = outputfile
    # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)


    # url = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

    # # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAMhWAA.BQABAwEAAAADAOz_BQD0_yvJVyFPy09dlLYE8P7FyKqXcD76OrOYiAnp5R7OCRD5huWdkmnEo4S7ItdyCh8ill-dPcMcMD614aTr0irmNzYbPE8bElvaTGhfs73FgVxnXtKOyrTUBsopx_eas3yfB-HkA3neQI6t_2lLwb-lF-TozGv6nVi0htsMrMF-oZiCqA2_kKV66L16tBeL2KC_9BFKmRcx8_2Oe_CgpnuR6XJctwIkqlDxlmhjSsnNUJ11cM7KV5LfE8abGVy5AkGyWQedq3E2H4a5PLfw2pHFWCdUIY17fBiqcGLyEg04zcZiwReZ5K5LIQwl6NVgkl6lvH2YCIX142fUXxGz7qCGj-JaBbTAvf8tW2o_33Isj8eaYollOFjs4wpeFV-bOrwlaXjvNOrM-nWkVzx2WiBtfhkglzONbCjR8KK4JEkksJyBBYr83IfldoUotHeUtRPj6zkRnVzVAwxiz_EYnwN_CXbrwFwLklL1qdZ4qgvMdUua9glZ8T6lZsy5Vt07detJNic9dy9Y4bBku5WoqCxw_qX5JdvvDJim3b_1lS-8xk3_kyByfTXjhvX8fTQKs7oujwSJ-b0HRtnkhJWd5A0AbIIQUB-p-I7GTw1SB39Czn3ncPH9Hrs5doNtS2A0I7ZZJ9Udzbg4dCMbJ7R9bnupmU0NNq08O83shzhFwBuGEFdd_zgef6FrNBgTDjS2CbpyA0Yl-QGccVjnwAB2Qr28A3AEoK69gE5O4balu73Nq18kjwUAA2XMEVd_WSvPQXCweKVWXR309APPxwDQzXAdhvUjj6R8FI579DsDK2ErbcDM2pAy3j3d7vm6CtANkk2DS9vbA3Sq_MwCblok3x2blscH5EsThvmJJgJyk7lnheWiopWFyqikJy-HZ9etOx3oU97JYlmMRHtsXxkhcDt5tuyKpAjRAfgP49GdBqMYGVGkdcJ19yhOZOT0JecxPRke-iLtRRESKRx6RhwQN8y0B7dMEWuQERwDBTOgT3QRK_URsenTZ2mQWcIoiIDX39U5d8-esswSKucd_oE6llD0fOG8VAqbQcX0OlMn1VZXKBrkLQ2qYKDOKeBktGvfBQLPCVuk4LgmAzdzntL6e8GceKlf_xS3mzX5hcu6dYJisuqTpfV3N-b26xDM0E_WvuWAS0it6coCxjdirowMgl3d-FL5Mao0SBVTbYrFBKkvqN9jidocGSPX0eUGh220aJwXQ-Pf3fJ1LYhVwIcNEU5d9siQunpFKEV-2aS0ONRGD5J7aGaF-LmBotokMiR17wrH0nVWN43UnrcsBNwIc4TgIOq9Ai-CK4Xr1vyy6lgrdPG7tDc0zm03OIvrO01KMtM6wLR6YLKufAjzjx1EhiUxjoKh5FDObFzw0sNyyTknAJ85Ig-NbBH96LD5fBfkJ8Dgg5dP9gvs-j7j'
    # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_1yL9mBiz2zU44ISLb7kTNdiyEqjPiUu4votWAYP8slKmFYuhW0oUN5SjXx5RM580OdJvMOSREoSXBX7ckpMhiOwvtYowTpk88v3O-LXk7Wwa7pJVnF0noyRMyebcmwp29VmL1mbAmNnG-4C6YvqxLnZdIpIAy_-i2Zd55ALtYfK9BTMycotiDMlPgPzsI584n5YkM3NiLhTKICn5nVf9bAm6-TMmSVWQVJkSK4nf_L9h-V5aJk1C_9HA7CQrrh1e91qVKDKOH-I2AZh7zSlTNnV4VjzULDUtmJ8H46U-hpTVjszeNmhMzsVx-_yktGZcghLObXBA6Psfvgzorg6shEQAr0fBjcdJbVnW5n5m9f7rEbDs_gvVxIJfxXaYuYFAV1N1Ijmu-NHXU65tmuvAsEWIx6M048B05RnxHy06WdHOrxWWky4pNFnIVqHDS0fG7Gerb4puAg3mcZ2Os5RDJw9zV3MrdyhdtnSlknPv6daB9UCinTDXr9blFmSLHqv5tq3bAmMT8i-Ef0y_hTabX87ui5-TbY3E2b_1LjpFDZmyr-uq0O-AmLj7MKbPU_W3oZ5_WG-vi4-Iba6txIGIG-IjJhB5TijN8dhAXdLj8OeEK1EkSFC7U5dSvPgQUahqtK5iDwYbzuM10IzyueqxddYxzsStq1oQIJNkZ4o8NR7XeeJip48D0q6c7dCrtqIjBCISBLci3l7SfO8yjVam6bNePz1SWuPNWe8PUE3AQXvORkzg8XBf2dQ6eEmuJxR8kGtsb8Eo4CTE3ZEx6Y9eUEprGmITZ6-qUF3pryDTdgM4LIi8h4LrTNJ-k9ItwEfJDawLVtkO7_7s6iu3j-Y1Azy9ZTNMi0nJesZLXEzj_mTB7EANnCdJGVGydGIHGmByeLfAgaLebAyzIv3kSfDG0hh1D7d8NAKKFWYktPSlab8sZbeYAFEDfyiw6ffBxqxYWpgIwX5ayScPlC6cDVlkQQ4-8m1uxqPJUXTgb0ufP8gBdkhZ6xyupqPqCjsW7fefI_9kiwLcQw8eNp-fmfk-6uTJ7LK_WEVyXLj-2qDZEr9Ah2S5G35iCYC0IrtmxHuWk8U4W5hNWFL1_PDlTBuymnIVVVCmGPn7O072zoygo94QoAz3xnDzQec2jPgkfVqeWThwsqgj_gU7_jS_cxGqf5ta70IhwA874-lkeS3NH_1NgEm5YB3890RzMuyNhhO1TgZTbim1vV1NZaO8yW3K_rBKSmdCAxOZUclMRpD0Yi63QrvQbjSvfa5BiwYg-AGHlBC6DaLek9zwevzF0QH_xjWsFBG6v4R0sI_lY_h7x3zjUPr_sfeMd6MISP0c1WT0mPzKcxP4kqFApab5EJyF2jz5NtQdggA6hQvcd7V2rwHST_k-4eLBFhaQ3Tm0zKM04I5mT23Ww8v'
    # headers = {
    #   'Content-Type': 'application/x-www-form-urlencoded',
    #     'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
    #     }

    # response = requests.request("GET", url, headers=headers, data=payload)
    # resp=response.json()
    # access_token=resp['access_token']
    # access_token=resp['access_token']
    print('--------------temp fileeee',temp_path)

    print('-----------------------access tokennn',access_token)
    import magic
    # target_file = open(temp_path, "rb")



    # application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    mime_type = magic.from_file(temp_path, mime=True)


    print('file nameee==============',file_name1)
    print('file nameee==============temp_name',temp_name)

    url1 = f"https://graph.microsoft.com/v1.0/me/drive/root:/{temp_name}:/content"

    # payload = "<file contents here>"
    headers1 = {
      'Authorization': f'Bearer {access_token}',
      # 'Content-Type': mime_type
    }
    # print('-----------------headers',headers1)

    with open(temp_path, 'rb') as file_data12:
        response1 = requests.request("PUT", url1, headers=headers1, data = file_data12,verify=False)
    # response = requests.request("PUT", url, headers=headers, data=payload)

        file_resp=response1.json()
        # print('responsee-------',file_resp)
        file_id=file_resp['id']
        print('------------file____id',file_id)

        download_url=file_resp['@microsoft.graph.downloadUrl']
    #     url3 = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink"

    #     payload1 = json.dumps({
    #       "type": "edit",
    #       "scope": "anonymous"
    #     })
    #     headers3 = {
    #       'Authorization': f'Bearer {access_token}',
    #       'Content-Type': 'application/json'
    #     }
    #     response3 = requests.request("POST", url3, headers=headers3, data=payload1)
    #     print('-----------333333',response3.json())

    #     resp3=response3.json()
    #     web_url=resp3['link']['webUrl']

    # return Response({"url": web_url,'id':file_id}, status=200)
        irm_prot=Irm_group_protection_details.objects.filter(dataroom_groups_id=group_s.dataroom_groups.id).last()
        print('--------------()()()()()))()()()()()',irm_prot.label_id)
        url4 = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/assignSensitivityLabel"

        payload4 = json.dumps({
          "sensitivityLabelId": "1dca0132-b36d-4108-99cc-4f0825fe67bf",
          "assignmentMethod": "standard",
          "justificationText": "test_justifircation"
        })

        print('--------------payload+++++++++++',payload4)
        headers4 = {
          'Authorization': f'Bearer {access_token}',
          'Content-Type': 'application/json'
        }


        response4 = requests.request("POST", url4, headers=headers4, data=payload4)

        print("------------------senstivity response",response4.text)
        
        headers5 = {
          'Authorization': f'Bearer {access_token}',
          }
        from .tasks import irm_file_bulk_download_single
        irm_file_bulk_download_single.apply_async( kwargs={
            "file_name12": temp_path,
            "download_url": download_url,
            "headers5": headers5,
            "datas_id":datas_id,
            "user_id":user_id,
            "dataroomid":dataroomid,
            "bulkid":bulkid,
            "objid":objid,
            "data":data,
            "alldata":alldata,
            "file_name":file_name
        },countdown=20*60)
        




















# from data_documents.views import donwload_irm_files
# def downloadtwo2(user_id,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add):
    # user=User.objects.get(id=user_id)
    # flagch=0    
    # member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    # if member.is_la_user or member.is_dataroom_admin:
    #     flagch=1
    # else:
    #     try:
    #         file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas.id,dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
    #         if file_permission:
    #             if file_permission.is_view_and_print_and_download==True:
    #                 flagch=1
    #     except Exception as e:
    #         print('permissionnnnnnn----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
    #         pass
    # print('--------------download 2 first')
    # data_room=Dataroom.objects.get(id=dataroomid)
    # if flagch==1:       
    #         if not os.path.exists(dest_folder):
    #             os.makedirs(dest_folder)
    #         # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
    #         # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
    #         # indexx=getIndexes(datas)
    #         indexx=getIndexes_with_queryset(datas)


    #         # filedata = dataroom_folder_serializer.data
    #         filename =  str(datas.name)  # be careful with file names
    #         # if preindex=='' and pindex=='':
    #         #   filename = index+"_"+str(filename)
    #         # elif pindex=='':
    #         #   filename = preindex+'.0.'+index+"_"+str(filename)
    #         # elif preindex=='':
    #         #   filename = pindex+'.0.'+index+"_"+str(filename)
    #         # else:
    #         #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)
    #         # file_name_list=list()
    #         # file_name1 = datas['path'].split("/")
    #         # file_name_list.append(file_name1[4])
    #         # file_name_list.append(file_name1[5])
    #         # print('------filename111111111111111',file_name_list)
    #         print('------urllllllllllllllllllllllllllllllllllllll',url)
    #         file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
    #         file_name=file_name.replace("%E2%80%93","–")
    #         print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
    #         temp_file_name=url.split("/")[-1]
            

    #         # print('----------pathhhhhhm beforeeeeeeeeee',datas['path'],sas_url)
    #         # datas['path']=datas['path'].replace("%E2%80%93", "")
    #         # print('----------pathhhhhhafterrrrrr',datas['path'])
    #         print('------filename befire %20 afterrrrrrrr',file_name)
    #         if docaspdf==True:
    #             pathsort2=file_name.split(".")
    #             filename=filename.split(".")

    #             if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
    #                 pathsort2[-1]='pdf'
    #                 filename[-1]='pdf'
    #             file_name='.'.join(pathsort2)
    #             filename='.'.join(filename)

    #         if exelaspdf==True:
    #             pathsort2=file_name.split(".")
    #             filename=filename.split(".")
    #             if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
    #                 pathsort2[-1]='pdf'
    #                 filename[-1]='pdf'
    #             file_name='.'.join(pathsort2)
    #             filename='.'.join(filename)

    #         tempname=filename.split('.')
    #         temp_pdf_file_name=file_name.split('/')
    #         temp_pdf_file_name=temp_pdf_file_name[-1]
    #         print('file_name------------------------????????????-',temp_pdf_file_name)
    #         print(datas,filename,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
    #         if dataindex==True:
    #             filename=str(indexx)+' '+str(filename)
    #             # print(filename,'===============')
    #             # print(file_name,'@@@@@@@@@@@@@@@@@')

    #         file_path = os.path.join(dest_folder, filename)
    #         # print('-----------file patghhg',file_path)
    #         # BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #         # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    #         # print('--------------------filennameeeee---------',filename)
    #         url = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

    #         # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAMhWAA.BQABAwEAAAADAOz_BQD0_yvJVyFPy09dlLYE8P7FyKqXcD76OrOYiAnp5R7OCRD5huWdkmnEo4S7ItdyCh8ill-dPcMcMD614aTr0irmNzYbPE8bElvaTGhfs73FgVxnXtKOyrTUBsopx_eas3yfB-HkA3neQI6t_2lLwb-lF-TozGv6nVi0htsMrMF-oZiCqA2_kKV66L16tBeL2KC_9BFKmRcx8_2Oe_CgpnuR6XJctwIkqlDxlmhjSsnNUJ11cM7KV5LfE8abGVy5AkGyWQedq3E2H4a5PLfw2pHFWCdUIY17fBiqcGLyEg04zcZiwReZ5K5LIQwl6NVgkl6lvH2YCIX142fUXxGz7qCGj-JaBbTAvf8tW2o_33Isj8eaYollOFjs4wpeFV-bOrwlaXjvNOrM-nWkVzx2WiBtfhkglzONbCjR8KK4JEkksJyBBYr83IfldoUotHeUtRPj6zkRnVzVAwxiz_EYnwN_CXbrwFwLklL1qdZ4qgvMdUua9glZ8T6lZsy5Vt07detJNic9dy9Y4bBku5WoqCxw_qX5JdvvDJim3b_1lS-8xk3_kyByfTXjhvX8fTQKs7oujwSJ-b0HRtnkhJWd5A0AbIIQUB-p-I7GTw1SB39Czn3ncPH9Hrs5doNtS2A0I7ZZJ9Udzbg4dCMbJ7R9bnupmU0NNq08O83shzhFwBuGEFdd_zgef6FrNBgTDjS2CbpyA0Yl-QGccVjnwAB2Qr28A3AEoK69gE5O4balu73Nq18kjwUAA2XMEVd_WSvPQXCweKVWXR309APPxwDQzXAdhvUjj6R8FI579DsDK2ErbcDM2pAy3j3d7vm6CtANkk2DS9vbA3Sq_MwCblok3x2blscH5EsThvmJJgJyk7lnheWiopWFyqikJy-HZ9etOx3oU97JYlmMRHtsXxkhcDt5tuyKpAjRAfgP49GdBqMYGVGkdcJ19yhOZOT0JecxPRke-iLtRRESKRx6RhwQN8y0B7dMEWuQERwDBTOgT3QRK_URsenTZ2mQWcIoiIDX39U5d8-esswSKucd_oE6llD0fOG8VAqbQcX0OlMn1VZXKBrkLQ2qYKDOKeBktGvfBQLPCVuk4LgmAzdzntL6e8GceKlf_xS3mzX5hcu6dYJisuqTpfV3N-b26xDM0E_WvuWAS0it6coCxjdirowMgl3d-FL5Mao0SBVTbYrFBKkvqN9jidocGSPX0eUGh220aJwXQ-Pf3fJ1LYhVwIcNEU5d9siQunpFKEV-2aS0ONRGD5J7aGaF-LmBotokMiR17wrH0nVWN43UnrcsBNwIc4TgIOq9Ai-CK4Xr1vyy6lgrdPG7tDc0zm03OIvrO01KMtM6wLR6YLKufAjzjx1EhiUxjoKh5FDObFzw0sNyyTknAJ85Ig-NbBH96LD5fBfkJ8Dgg5dP9gvs-j7j'
    #         payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_1yL9mBiz2zU44ISLb7kTNdiyEqjPiUu4votWAYP8slKmFYuhW0oUN5SjXx5RM580OdJvMOSREoSXBX7ckpMhiOwvtYowTpk88v3O-LXk7Wwa7pJVnF0noyRMyebcmwp29VmL1mbAmNnG-4C6YvqxLnZdIpIAy_-i2Zd55ALtYfK9BTMycotiDMlPgPzsI584n5YkM3NiLhTKICn5nVf9bAm6-TMmSVWQVJkSK4nf_L9h-V5aJk1C_9HA7CQrrh1e91qVKDKOH-I2AZh7zSlTNnV4VjzULDUtmJ8H46U-hpTVjszeNmhMzsVx-_yktGZcghLObXBA6Psfvgzorg6shEQAr0fBjcdJbVnW5n5m9f7rEbDs_gvVxIJfxXaYuYFAV1N1Ijmu-NHXU65tmuvAsEWIx6M048B05RnxHy06WdHOrxWWky4pNFnIVqHDS0fG7Gerb4puAg3mcZ2Os5RDJw9zV3MrdyhdtnSlknPv6daB9UCinTDXr9blFmSLHqv5tq3bAmMT8i-Ef0y_hTabX87ui5-TbY3E2b_1LjpFDZmyr-uq0O-AmLj7MKbPU_W3oZ5_WG-vi4-Iba6txIGIG-IjJhB5TijN8dhAXdLj8OeEK1EkSFC7U5dSvPgQUahqtK5iDwYbzuM10IzyueqxddYxzsStq1oQIJNkZ4o8NR7XeeJip48D0q6c7dCrtqIjBCISBLci3l7SfO8yjVam6bNePz1SWuPNWe8PUE3AQXvORkzg8XBf2dQ6eEmuJxR8kGtsb8Eo4CTE3ZEx6Y9eUEprGmITZ6-qUF3pryDTdgM4LIi8h4LrTNJ-k9ItwEfJDawLVtkO7_7s6iu3j-Y1Azy9ZTNMi0nJesZLXEzj_mTB7EANnCdJGVGydGIHGmByeLfAgaLebAyzIv3kSfDG0hh1D7d8NAKKFWYktPSlab8sZbeYAFEDfyiw6ffBxqxYWpgIwX5ayScPlC6cDVlkQQ4-8m1uxqPJUXTgb0ufP8gBdkhZ6xyupqPqCjsW7fefI_9kiwLcQw8eNp-fmfk-6uTJ7LK_WEVyXLj-2qDZEr9Ah2S5G35iCYC0IrtmxHuWk8U4W5hNWFL1_PDlTBuymnIVVVCmGPn7O072zoygo94QoAz3xnDzQec2jPgkfVqeWThwsqgj_gU7_jS_cxGqf5ta70IhwA874-lkeS3NH_1NgEm5YB3890RzMuyNhhO1TgZTbim1vV1NZaO8yW3K_rBKSmdCAxOZUclMRpD0Yi63QrvQbjSvfa5BiwYg-AGHlBC6DaLek9zwevzF0QH_xjWsFBG6v4R0sI_lY_h7x3zjUPr_sfeMd6MISP0c1WT0mPzKcxP4kqFApab5EJyF2jz5NtQdggA6hQvcd7V2rwHST_k-4eLBFhaQ3Tm0zKM04I5mT23Ww8v'
    #         headers = {
    #           'Content-Type': 'application/x-www-form-urlencoded',
    #             'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
    #             }

    #         response = requests.request("GET", url, headers=headers, data=payload)
    #         resp=response.json()
    #         access_token=resp['access_token']
    #         try:
    #             if (tempname[-1]=='pdf' or tempname[-1]=='PDF') :
    #                 # file_path = os.path.join(dest_folder, filename)
    #                 userid=user.id
    #                 watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
    #                 if watermarking.exists() and watermakingcheck :      
    #                     for i in watermarking:
    #                         i.user_id=userid
    #                     serializer = WatermarkingSerializer(watermarking,many=True)
    #                     data = serializer.data
    #                 else:
    #                     data=False
    #                 if data:
                        
    #                     tempfile='temp'+str(random.randint(0, 10000))
    #                     temp_path = os.path.join(dest_folder, tempfile)
    #                     if data_room.is_usa_blob==True:
    #                         sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

    #                         block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
    #                     else:
    #                         sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    #                         block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                        
    #                     # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    #                     container_name ='docullycontainer'
    #                     print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTTttttttttttttttttt')
    #                     # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
    #                     # if member.is_la_user or member.is_dataroom_admin:
    #                     #     block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
    #                     # else:


    #                     try:
    #                         print('--------------download 2 first tryyyy')
    #                         # file_path = os.path.join(dest_folder, filename)
    #                         if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
    #                             red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
    #                             url=(red.file).split('/')
    #                             file_namee=url[-2]+'/'+url[-1]

    #                             block_blob_service.get_blob_to_path(container_name, file_namee, temp_path)
    #                         else:
    #                             block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)

    #                         from userauth import utils
    #                         ip = ip_add
                        
    #                         GeneratePDF(data,ip,user,dataroomid)
    #                         watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
    #                         outputfile=file_path
    #                         # print(str(outputfile),'++++++++++++++++++++++++++++++')
    #                         pdf_writer=PyPDF2.PdfWriter()
                        
    #                         if (os.path.exists(temp_path)):

    #                             with open(temp_path, 'rb') as fh:
    #                                 pdf=PyPDF2.PdfReader(fh,strict=False)
    #                                 with open(watermarkfile,'rb') as watermarkfile:
    #                                     watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile,strict=False)
    #                                     for i in range(len(pdf.pages)):
    #                                         p=pdf.pages[i]
    #                                         p.merge_page(watermarkfile_pdf.pages[0])
    #                                         pdf_writer.add_page(p)
    #                                     # watermarkfile.close()
    #                                     # fh.close()
    #                                     with open(outputfile,'wb') as outputfileeee:
    #                                         pdf_writer.write(outputfileeee)
    #                                 # outputfileeee.close()                    



                                    
    #                                 donwload_irm_files(outputfile,access_token,filename,temp_pdf_file_name)

    #                                 print('removeeee dirrr insideeee',temp_path)
    #                                 os.remove(temp_path)
    #                                 os.remove(outputfile)
    #                                 # os.chdir(temp_path)
    #                                 # os.remove(tempfile)

    #                         if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
    #                             print('---------------------insideee ifffff')
    #                             pass
    #                         else:
    #                             print('---------------------ooooutside  ifffff')
    #                             BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    #                             BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                     except Exception as e:
    #                         print('-----------------------excc----------------',e)
    #                         # os.chdir(temp_path)
    #                         print('removeeee dirrr outside',file_path)

    #                         os.remove(temp_path)
    #                         if (os.path.exists(file_path)):
    #                             os.remove(file_path)

    #                         # os.chdir(dest_folder)
    #                         # print('------------------------------filessss',os.listdir())
    #                         # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                         # if member.is_la_user or member.is_dataroom_admin:
    #                         #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                         # else:
    #                         try:
    #                             if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
    #                                 red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
    #                                 url=(red.file).split('/')
    #                                 file_namee=url[-2]+'/'+url[-1]

    #                                 block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
    #                                 donwload_irm_files(file_path,access_token,file_namee,url[-1])
    #                             else:
    #                                 block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                                 donwload_irm_files(file_path,access_token,filename,temp_pdf_file_name)

    #                             if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
    #                                 pass
    #                             else:
    #                                 BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    #                                 BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                             os.remove(file_path)                            
    #                         except:
    #                             BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                             if (os.path.exists(file_path)):
    #                                 os.remove(file_path)
    #                         # os.chdir(dest_folder)
    #                         # print('------------------------------filessss',os.listdir())

    #                 else:
    #                     # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    #                     if data_room.is_usa_blob==True:
    #                         sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

    #                         block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
    #                     else:
    #                         sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
    #                         block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
                        
    #                     container_name ='docullycontainer'
    #                     print('--------------except pdf  download file location',file_path)
    #                     print('--------------download 2 elsee')
    #                     # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                     # if member.is_la_user or member.is_dataroom_admin:
    #                     #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                     # else:
    #                     # try:
    #                     print('--------------download 2 second try')
    #                     if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
    #                         red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
    #                         url=(red.file).split('/')
    #                         file_namee=url[-2]+'/'+url[-1]


    #                         print("-------------inside redect")

    #                         block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
    #                         donwload_irm_files(file_path,access_token,filename,url[-1])
    #                     else:
    #                         print("-------------outside redect")
    #                         block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
    #                         donwload_irm_files(file_path,access_token,filename,temp_pdf_file_name)

    #                     os.remove(file_path)

    #                     if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
    #                         pass
    #                     else:
    #                         BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    #                         BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                     # except:
    #                     #     BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                     #     if (os.path.exists(file_path)):
    #                     #         os.remove(file_path)
    #                     #     print('--------------download 2 last except')
    #                     os.remove(file_path)   


    #             else:
    #                 print('--------------download 2 last else')
    #                 # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
    #                 if data_room.is_usa_blob==True:
    #                     block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
    #                 else:
    #                     block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
                    
    #                 container_name ='docullycontainer'
    #                 try:

    #                     print('-------------------------------filename============',file_name)
    #                     print('-------------------------------filepath============',file_path)

    #                     if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exists():
    #                         red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).last()
    #                         url=(red.file).split('/')
    #                         print('====================urllllllll',url)
    #                         temp_name=url[-1]
    #                         print('===================tempname',temp_name)
    #                         file_namee=url[-2]+'/'+url[-1]
    #                         print('===------------------------file_nmeeee',file_namee)
    #                         file_path=file_path.split('.')
    #                         file_path[-1]='pdf'
    #                         temp_file_name='.'.join(file_path)
    #                         block_blob_service.get_blob_to_path(container_name, file_namee, temp_file_name)
    #                         donwload_irm_files(file_path,access_token,file_namee,temp_name)
    #                     else:
    #                         block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            
    #                         donwload_irm_files(file_path,access_token,filename,temp_file_name)

    #                     if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
    #                         pass    
    #                     else:
    #                         BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
    #                         BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

    #                     os.remove(file_path)   
    #                 except Exception as e:
    #                     print('11111111111111111111111111111111111111111111111111111111----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
    #                     BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
    #                     if (os.path.exists(file_path)):
    #                         os.remove(file_path)
           
    #         except Exception as e:

    #                 print('4444444444444444444444444444444444444444444444444444444444----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
    #                 BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            
           






# from data_documents.views import donwload_irm_files

def downloadtwo2(user_id,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name_2):
    user=User.objects.get(id=user_id)
    flagch=0   
    is_irm_protected=False
    is_doculink=False
    is_doc_link=False
    team_irm_protected=False
    group_irm=False
    group_s=" "
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    data_room=Dataroom.objects.get(id=dataroomid)
    print('-------------------------irm group',group_irm)
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas.id,dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
                else:
                    BulkDownloadstatus.objects.filter(id=objid).update(filecount=F('filecount')-1)

                if file_permission.is_irm_protected==True:
                    is_irm_protected=True

                    if data_room.dataroom_version=="Lite":
                        if dataroomProLiteFeatures.objects.filter(dataroom_id=data_room.id,is_irm_protected=True).exists():
                            team_irm_protected=True
                        else:
                            team_irm_protected=False
                    else:
                        team_irm_protected=True

                    group_s=DataroomGroupPermission.objects.filter(dataroom_groups_id=member.end_user_group.first().id,dataroom_id=data_room.id).last()
                    if group_s.is_irm_protected and group_s.is_irm_active:
                        group_irm=True
                    else:
                        group_irm=False

                    print('-------------------------irm group',group_irm)
                    print('-------------------------irm team_irm_protected',team_irm_protected)
                    print('-------------------------irm is_irm_protected',is_irm_protected)
                    if team_irm_protected and group_irm and is_irm_protected:                        
                        is_irm_protected=True
                    else:
                        is_irm_protected=False



                elif file_permission.is_shortcut==True:
                    is_doculink=True

        except Exception as e:
            print('permissionnnnnnn----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            pass
    print('--------------download 2 first')

    if flagch==1:
            import os       
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
            # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
            # indexx=getIndexes(datas)
            indexx=getIndexes_with_queryset(datas)


            # filedata = dataroom_folder_serializer.data
            filename =  str(datas.name)  # be careful with file names
            # if preindex=='' and pindex=='':
            #   filename = index+"_"+str(filename)
            # elif pindex=='':
            #   filename = preindex+'.0.'+index+"_"+str(filename)
            # elif preindex=='':
            #   filename = pindex+'.0.'+index+"_"+str(filename)
            # else:
            #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)
            # file_name_list=list()
            # file_name1 = datas['path'].split("/")
            # file_name_list.append(file_name1[4])
            # file_name_list.append(file_name1[5])
            # print('------filename111111111111111',file_name_list)
            print('------urllllllllllllllllllllllllllllllllllllll',url)
            file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
            file_name=file_name.replace("%E2%80%93","–")
            print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
            temp_file_name=url.split("/")[-1]
            

            # print('----------pathhhhhhm beforeeeeeeeeee',datas['path'],sas_url)
            # datas['path']=datas['path'].replace("%E2%80%93", "")
            # print('----------pathhhhhhafterrrrrr',datas['path'])
            print('------filename befire %20 afterrrrrrrr',file_name)
            if is_irm_protected==False:
                

                if is_doculink==True:
                    is_doc_link=True
                    filename_u=filename.split(".")
                    
                    filename_u[-1]='pdf'
                    
                    filename_u='.'.join(filename)
                    from constants import constants
                    import os
                    base_url = constants.backend_ip2
                    file_name_u = str(request.user.id)+'_'+str(pk)+'.txt'
                    f= open(file_name_u,"w+")

                    url = 'URL='+str(base_url)+'/file-view/'+str(pk)+'/'+str(request.user.id)+'/'

                    data = ['[InternetShortcut]']
                    tempnamereplace=datas.get('name').split('.')[-1]

                    url_file = datas.get('name').replace('.'+str(tempnamereplace),'').replace(' ','_')

                    # url_file = datas.get('name').split('.')[0].replace(' ','_')
                    # #print('url_file',url_file)
                    # #print('url ------',url)
                    url_file_ext = datas.get('name').split('.')
                    # #print("url_file_ext =====>",url_file_ext[1])
                    file_path = os.path.join(dest_folder, filename_u)
                    # icon_path = '/home/cdms_backend/cdms2/static/Doculink_Icon/'
                    # for file_icon in os.listdir(icon_path):
                    #     file_icon_type = file_icon.split('.')
                    #     if file_icon_type[0] == url_file_ext[1]:
                    #         #print("file_icon ==>",file_icon)
                    #         icon_type = file_icon


                    # icon = "IconFile=%USERPROFILE%\\Downloads\\"+str(url_file)+"\\"+"media"+"\\"+"new_icon_type.ico"
                    # icon = icon.replace(" ", "")
                    data.append(url)
                    # data.append('IconIndex=0')
                    # data.append(icon)

                    for i in data:  
                        f.write("%s\r\n" %(i))
                    f.close()

                elif docaspdf==True:
                    pathsort2=file_name.split(".")
                    filename=filename.split(".")

                    if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
                        pathsort2[-1]='pdf'
                        filename[-1]='pdf'
                    file_name='.'.join(pathsort2)
                    filename='.'.join(filename)

                elif exelaspdf==True:
                    pathsort2=file_name.split(".")
                    filename=filename.split(".")
                    if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
                        pathsort2[-1]='pdf'
                        filename[-1]='pdf'
                    file_name='.'.join(pathsort2)
                    filename='.'.join(filename)

            if is_doc_link==False:
                tempname=filename.split('.')
                temp_pdf_file_name=file_name.split('/')
                temp_pdf_file_name=temp_pdf_file_name[-1]
                print('file_name------------------------????????????-',temp_pdf_file_name)
                print(datas,filename,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
                if dataindex==True:
                    filename=str(indexx)+' '+str(filename)
                    # print(filename,'===============')
                    # print(file_name,'@@@@@@@@@@@@@@@@@')

                file_path = os.path.join(dest_folder, filename)
                # print('-----------file patghhg',file_path)
                # BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                # print('--------------------filennameeeee---------',filename)
                url = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

                # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAMhWAA.BQABAwEAAAADAOz_BQD0_yvJVyFPy09dlLYE8P7FyKqXcD76OrOYiAnp5R7OCRD5huWdkmnEo4S7ItdyCh8ill-dPcMcMD614aTr0irmNzYbPE8bElvaTGhfs73FgVxnXtKOyrTUBsopx_eas3yfB-HkA3neQI6t_2lLwb-lF-TozGv6nVi0htsMrMF-oZiCqA2_kKV66L16tBeL2KC_9BFKmRcx8_2Oe_CgpnuR6XJctwIkqlDxlmhjSsnNUJ11cM7KV5LfE8abGVy5AkGyWQedq3E2H4a5PLfw2pHFWCdUIY17fBiqcGLyEg04zcZiwReZ5K5LIQwl6NVgkl6lvH2YCIX142fUXxGz7qCGj-JaBbTAvf8tW2o_33Isj8eaYollOFjs4wpeFV-bOrwlaXjvNOrM-nWkVzx2WiBtfhkglzONbCjR8KK4JEkksJyBBYr83IfldoUotHeUtRPj6zkRnVzVAwxiz_EYnwN_CXbrwFwLklL1qdZ4qgvMdUua9glZ8T6lZsy5Vt07detJNic9dy9Y4bBku5WoqCxw_qX5JdvvDJim3b_1lS-8xk3_kyByfTXjhvX8fTQKs7oujwSJ-b0HRtnkhJWd5A0AbIIQUB-p-I7GTw1SB39Czn3ncPH9Hrs5doNtS2A0I7ZZJ9Udzbg4dCMbJ7R9bnupmU0NNq08O83shzhFwBuGEFdd_zgef6FrNBgTDjS2CbpyA0Yl-QGccVjnwAB2Qr28A3AEoK69gE5O4balu73Nq18kjwUAA2XMEVd_WSvPQXCweKVWXR309APPxwDQzXAdhvUjj6R8FI579DsDK2ErbcDM2pAy3j3d7vm6CtANkk2DS9vbA3Sq_MwCblok3x2blscH5EsThvmJJgJyk7lnheWiopWFyqikJy-HZ9etOx3oU97JYlmMRHtsXxkhcDt5tuyKpAjRAfgP49GdBqMYGVGkdcJ19yhOZOT0JecxPRke-iLtRRESKRx6RhwQN8y0B7dMEWuQERwDBTOgT3QRK_URsenTZ2mQWcIoiIDX39U5d8-esswSKucd_oE6llD0fOG8VAqbQcX0OlMn1VZXKBrkLQ2qYKDOKeBktGvfBQLPCVuk4LgmAzdzntL6e8GceKlf_xS3mzX5hcu6dYJisuqTpfV3N-b26xDM0E_WvuWAS0it6coCxjdirowMgl3d-FL5Mao0SBVTbYrFBKkvqN9jidocGSPX0eUGh220aJwXQ-Pf3fJ1LYhVwIcNEU5d9siQunpFKEV-2aS0ONRGD5J7aGaF-LmBotokMiR17wrH0nVWN43UnrcsBNwIc4TgIOq9Ai-CK4Xr1vyy6lgrdPG7tDc0zm03OIvrO01KMtM6wLR6YLKufAjzjx1EhiUxjoKh5FDObFzw0sNyyTknAJ85Ig-NbBH96LD5fBfkJ8Dgg5dP9gvs-j7j'
                payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_9QeQo0_rnfMxT9H7dzeVdp2rs2lyfFyXNjo-ZVllgwqdGs9B6pLBo9VuldMkCb64bTR_9ehyO30t0lZQHqTayS-9N88efQKxv0thfRYENOwIxhfb2pSHlXO9XXZkAcEPE2ptWZTiRux6Cywg757Tox0f2GQ96QKMR75Zb9KzwnvjuReI8hqkvaal-Ozy4-3kRvqWM3U26AvZnoZZoamHcT53zxhNKFzYxqR1V6KVxJXnlJPEZQM4p_1IuG0EsJrEE_n3Pnrj0r6BlJkdfslFj1axxhZ4LEO-d-0CYhnn994f5tp5k12i0i1uQm173VhK2K_yUOxP1jYMPnsREe52fn4hOV1EvfGH7VLmrdaAd6sAf6aOlrM7UmAJyZsDAr9PbxMBBUcISofnFD70jFjukyJCrP63WGac4kq1ZNTaE4dMaZw9jT2N7mhj3AQwIovcwEOesbOKHMabK7GufSoC9eIwHKl-qqM5Nbp8ATWwyVNgJcEf5m69OomxEEgAPPW1O1xeXSNMSsSholWfL9X3uQE5G73AIPR_jJTzuQtWER2gtWY0T0gxcIdG0UtLJcr-i4-b49YUOa_7MUHpwniQLf_Oh--8f-DACO7ob4ak_Z-5WxbsmZzDRhbgbepAM9Wjv9OjGIp772FQZFFQt_d_BwdgrXcjxCM2N4Lpi3j2rzFSnwVAsC1Sd5cExP0Q5JEEzWsS3qcv7mv5i9LDERZq0M7nEbD3cluUJTwZJOtUEHUKzA7rYl5lTk00BSo8ePqkBwDKzpFNHXCC6Uu9FKMEspDXXHqX_NOXm2UTQ-9XBpbel_8pRwDuz3IaGZAucUiGw4BsHkh8KElTViXjlCD8zYvgTLOrbyX-XY0sQ03HhhhHqM1sFBuWfhDHhN_71lzGiaJaXxN7npROpcu7EcCZsIHmDsQ5IvX_WDQjkZQm2zKdYHNuy5-88PTiPkP_xyTTnZ30IYtV1zutbD0kkFYMaMTraOGLMzuWVN1R5gh_R3RqcxA0H_fnPx_tLMr5DJTM0n_frr7f2FQUf0u1G6_TzLXlaPSxdGW4WeWfxXtYTzVtameKY1kPBsJ8vVE5PGMBg2AOaTtDRubfayQwRSxXrcc9irdeyvCM3anhrixgCMaSgFthGO9wtq6SLTCboWO1F9MAUw3nH6BB8CQu5s_NHS8rb4ROK6_4AkWnBB-4Ssu--cQ-Fn3NKcLIRnf7YO8_7xWQHu7k7eka9SgLtTmZgWdvnA6hvw1WvC4oD76NNY9ADRwR7MHyCNVb3bP0SGSbtlwsm7C873GABNTpq-xTkVF4_nwQKtp0lnylzi-CBb1NDc-GOFrbu4iiolxvi2nZmpJqlEzzMA6mQ8Elgxh3SLaPK2LCgf9irtEcQDiMVDh5Dc969ZH_508yG-9aTp6Yp2s-fggkaqKOQ'
                headers = {
                  'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
                    }

                response = requests.request("GET", url, headers=headers, data=payload)
                resp=response.json()
                access_token=resp['access_token']
                try:
                    if (tempname[-1]=='pdf' or tempname[-1]=='PDF') :
                        # file_path = os.path.join(dest_folder, filename)
                        userid=user.id
                        watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
                        if watermarking.exists() and watermakingcheck :      
                            for i in watermarking:
                                i.user_id=userid
                            serializer = WatermarkingSerializer(watermarking,many=True)
                            data = serializer.data
                        else:
                            data=False
                        if data:
                            
                            tempfile='temp'+str(random.randint(0, 10000))
                            temp_path = os.path.join(dest_folder, tempfile)
                            if data_room.is_usa_blob==True:
                                sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                                block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
                            else:
                                sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                                block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                            
                            # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                            container_name ='docullycontainer'
                            print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTTttttttttttttttttt')
                            # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                            # if member.is_la_user or member.is_dataroom_admin:
                            #     block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                            # else:


                            try:
                                print('--------------download 2 first tryyyy')
                                # file_path = os.path.join(dest_folder, filename)
                                if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                                    red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                                    url=(red.file).split('/')
                                    file_namee=url[-2]+'/'+url[-1]

                                    block_blob_service.get_blob_to_path(container_name, file_namee, temp_path)
                                else:
                                    block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)

                                from userauth import utils
                                ip = ip_add
                            
                                GeneratePDF(data,ip,user,dataroomid,)
                                watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
                                outputfile=file_path
                                # print(str(outputfile),'++++++++++++++++++++++++++++++')
                                pdf_writer=PyPDF2.PdfWriter()
                            
                                if (os.path.exists(temp_path)):

                                    with open(temp_path, 'rb') as fh:
                                        pdf=PyPDF2.PdfReader(fh,strict=False)
                                        with open(watermarkfile,'rb') as watermarkfile:
                                            watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile,strict=False)
                                            for i in range(len(pdf.pages)):
                                                p=pdf.pages[i]
                                                p.merge_page(watermarkfile_pdf.pages[0])
                                                pdf_writer.add_page(p)
                                            # watermarkfile.close()
                                            # fh.close()
                                            with open(outputfile,'wb') as outputfileeee:
                                                pdf_writer.write(outputfileeee)
                                        # outputfileeee.close()                    



                                        if is_irm_protected:
                                            BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                            donwload_irm_files(outputfile,access_token,filename,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                                        # else:
                                        #     if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                        #         print('---------------------insideee ifffff')
                                        #         pass
                                        #     else:
                                        #         print('---------------------ooooutside  ifffff')
                                        #         BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                                        #         BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                        # os.remove(outputfile)
                                        # os.chdir(temp_path)
                                        # os.remove(tempfile)

                                if not is_irm_protected:
                                    if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                        print('---------------------insideee ifffff')
                                        pass
                                    else:
                                        print('---------------------ooooutside  ifffff')
                                        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                                        BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                print('removeeee dirrr insideeee',temp_path)
                                os.remove(temp_path)
                            except Exception as e:
                                print('-----------------------excc----------------',e)
                                # os.chdir(temp_path)
                                print('removeeee dirrr outside',file_path)

                                os.remove(temp_path)
                                if (os.path.exists(file_path)):
                                    os.remove(file_path)

                                # os.chdir(dest_folder)
                                # print('------------------------------filessss',os.listdir())
                                # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                                # if member.is_la_user or member.is_dataroom_admin:
                                #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                                # else:
                                try:
                                    if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                                        red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                                        url=(red.file).split('/')
                                        file_namee=url[-2]+'/'+url[-1]

                                        block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                                        if is_irm_protected:
                                            BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                            donwload_irm_files(file_path,access_token,file_namee,url[-1],datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                                    else:
                                        block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                                        if is_irm_protected:
                                            BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                            donwload_irm_files(file_path,access_token,filename,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                                    if not is_irm_protected:
                                        if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                            pass
                                        else:
                                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                                            BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                    # os.remove(file_path)                            
                                except:
                                    BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                    if (os.path.exists(file_path)):
                                        os.remove(file_path)
                                # os.chdir(dest_folder)
                                # print('------------------------------filessss',os.listdir())

                        else:
                            # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                            if data_room.is_usa_blob==True:
                                sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                                block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                            else:
                                sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                                block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                            
                            container_name ='docullycontainer'
                            print('--------------except pdf  download file location',file_path)
                            print('--------------download 2 elsee')
                            # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            # if member.is_la_user or member.is_dataroom_admin:
                            #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            # else:
                            # try:
                            print('--------------download 2 second try')
                            if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                                red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                                url=(red.file).split('/')
                                file_namee=url[-2]+'/'+url[-1]


                                print("-------------inside redect")

                                block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                                if is_irm_protected:
                                    BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                    donwload_irm_files(file_path,access_token,filename,url[-1],datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                            else:
                                print("-------------outside redect")
                                block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                                if is_irm_protected:
                                    BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                    donwload_irm_files(file_path,access_token,filename,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                            # os.remove(file_path)
                            if not is_irm_protected:
                                if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                    pass
                                else:
                                    BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                                    BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                # except:
                                #     BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            #     if (os.path.exists(file_path)):
                            #         os.remove(file_path)
                            #     print('--------------download 2 last except')
                            # os.remove(file_path)   


                    else:
                        print('--------------download 2 last else')
                        # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                        if data_room.is_usa_blob==True:
                            block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                        else:
                            block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                        
                        container_name ='docullycontainer'
                        try:

                            print('-------------------------------filename============',file_name)
                            print('-------------------------------filepath============',file_path)

                            if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exists():
                                red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).last()
                                url=(red.file).split('/')
                                print('====================urllllllll',url)
                                temp_name=url[-1]
                                print('===================tempname',temp_name)
                                file_namee=url[-2]+'/'+url[-1]
                                print('===------------------------file_nmeeee',file_namee)
                                file_path=file_path.split('.')
                                file_path[-1]='pdf'
                                temp_file_name='.'.join(file_path)
                                block_blob_service.get_blob_to_path(container_name, file_namee, temp_file_name)
                                if is_irm_protected:
                                    BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                    donwload_irm_files(file_path,access_token,file_namee,temp_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                            else:
                                block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                                if is_irm_protected:
                                    BulkDownloadstatus.objects.filter(id=objid).update(is_file_irm=True)
                                    donwload_irm_files(file_path,access_token,filename,temp_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                            if not is_irm_protected:

                                if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                    pass    
                                else:
                                    BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                                    BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                            # os.remove(file_path)   
                        except Exception as e:
                            print('11111111111111111111111111111111111111111111111111111111----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                            BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            if (os.path.exists(file_path)):
                                os.remove(file_path)
               
                except Exception as e:

                        print('4444444444444444444444444444444444444444444444444444444444----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                        BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                
      




















def downloadtwo2_single_file(user_id,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name_2):
    user=User.objects.get(id=user_id)
    flagch=0   
    is_irm_protected=False
    team_irm_protected=False
    group_irm=False
    group_s=" "
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    data_room=Dataroom.objects.get(id=dataroomid)
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas.id,dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1


                if file_permission.is_irm_protected==True:
                    is_irm_protected=True


                    if data_room.dataroom_version=="Lite":
                        if dataroomProLiteFeatures.objects.filter(dataroom_id=data_room.id,is_irm_protected=True).exists():
                            team_irm_protected=True
                        else:
                            team_irm_protected=False
                    else:
                        team_irm_protected=True

                    group_s=DataroomGroupPermission.objects.filter(dataroom_groups_id=member.end_user_group.first().id,dataroom_id=data_room.id).last()
                    if group_s.is_irm_protected and group_s.is_irm_active:
                        group_irm=True
                    else:
                        group_irm=False

                    print('-----------------------------------group_irm',group_irm)
                    print('-----------------------------------team_irm_protected',team_irm_protected)
                    print('-----------------------------------is_irm_protected',is_irm_protected)

                    if team_irm_protected and group_irm and is_irm_protected:
                        is_irm_protected=True

                    else:
                        is_irm_protected=False


                    print('-----------------------------------isrimmmmm',is_irm_protected)

        except Exception as e:
            print('permissionnnnnnn----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            pass
    print('--------------download 2 first')


    if flagch==1:       
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
            # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
            # indexx=getIndexes(datas)
            indexx=getIndexes_with_queryset(datas)


            # filedata = dataroom_folder_serializer.data
            filename =  str(datas.name)  # be careful with file names
            # if preindex=='' and pindex=='':
            #   filename = index+"_"+str(filename)
            # elif pindex=='':
            #   filename = preindex+'.0.'+index+"_"+str(filename)
            # elif preindex=='':
            #   filename = pindex+'.0.'+index+"_"+str(filename)
            # else:
            #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)
            # file_name_list=list()
            # file_name1 = datas['path'].split("/")
            # file_name_list.append(file_name1[4])
            # file_name_list.append(file_name1[5])
            # print('------filename111111111111111',file_name_list)
            print('------urllllllllllllllllllllllllllllllllllllll',url)
            file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
            file_name=file_name.replace("%E2%80%93","–")
            print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])
            temp_file_name=url.split("/")[-1]
            

            # print('----------pathhhhhhm beforeeeeeeeeee',datas['path'],sas_url)
            # datas['path']=datas['path'].replace("%E2%80%93", "")
            # print('----------pathhhhhhafterrrrrr',datas['path'])
            print('------filename befire %20 afterrrrrrrr',file_name)
            if is_irm_protected==False :
                if docaspdf==True:
                    pathsort2=file_name.split(".")
                    filename=filename.split(".")

                    if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
                        pathsort2[-1]='pdf'
                        filename[-1]='pdf'
                    file_name='.'.join(pathsort2)
                    filename='.'.join(filename)

                if exelaspdf==True:
                    pathsort2=file_name.split(".")
                    filename=filename.split(".")
                    if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
                        pathsort2[-1]='pdf'
                        filename[-1]='pdf'
                    file_name='.'.join(pathsort2)
                    filename='.'.join(filename)

            tempname=filename.split('.')
            temp_pdf_file_name=file_name.split('/')
            temp_pdf_file_name=temp_pdf_file_name[-1]
            print('file_name------------------------????????????-',temp_pdf_file_name)
            print(datas,filename,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
            # if dataindex==True:
            #     filename=str(indexx)+' '+str(filename)
                # print(filename,'===============')
                # print(file_name,'@@@@@@@@@@@@@@@@@')

            file_path = os.path.join(dest_folder, filename)
            print('-----------file patghhg$$$$$$$$$$######################',file_path)
            if (os.path.exists(file_path)):
                os.remove(file_path)


            # BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            # print('--------------------filennameeeee---------',filename)
            url = "https://login.microsoftonline.com/182443d6-de18-49a9-8bb9-68979df5d44d/oauth2/v2.0/token"

            # payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAMhWAA.BQABAwEAAAADAOz_BQD0_yvJVyFPy09dlLYE8P7FyKqXcD76OrOYiAnp5R7OCRD5huWdkmnEo4S7ItdyCh8ill-dPcMcMD614aTr0irmNzYbPE8bElvaTGhfs73FgVxnXtKOyrTUBsopx_eas3yfB-HkA3neQI6t_2lLwb-lF-TozGv6nVi0htsMrMF-oZiCqA2_kKV66L16tBeL2KC_9BFKmRcx8_2Oe_CgpnuR6XJctwIkqlDxlmhjSsnNUJ11cM7KV5LfE8abGVy5AkGyWQedq3E2H4a5PLfw2pHFWCdUIY17fBiqcGLyEg04zcZiwReZ5K5LIQwl6NVgkl6lvH2YCIX142fUXxGz7qCGj-JaBbTAvf8tW2o_33Isj8eaYollOFjs4wpeFV-bOrwlaXjvNOrM-nWkVzx2WiBtfhkglzONbCjR8KK4JEkksJyBBYr83IfldoUotHeUtRPj6zkRnVzVAwxiz_EYnwN_CXbrwFwLklL1qdZ4qgvMdUua9glZ8T6lZsy5Vt07detJNic9dy9Y4bBku5WoqCxw_qX5JdvvDJim3b_1lS-8xk3_kyByfTXjhvX8fTQKs7oujwSJ-b0HRtnkhJWd5A0AbIIQUB-p-I7GTw1SB39Czn3ncPH9Hrs5doNtS2A0I7ZZJ9Udzbg4dCMbJ7R9bnupmU0NNq08O83shzhFwBuGEFdd_zgef6FrNBgTDjS2CbpyA0Yl-QGccVjnwAB2Qr28A3AEoK69gE5O4balu73Nq18kjwUAA2XMEVd_WSvPQXCweKVWXR309APPxwDQzXAdhvUjj6R8FI579DsDK2ErbcDM2pAy3j3d7vm6CtANkk2DS9vbA3Sq_MwCblok3x2blscH5EsThvmJJgJyk7lnheWiopWFyqikJy-HZ9etOx3oU97JYlmMRHtsXxkhcDt5tuyKpAjRAfgP49GdBqMYGVGkdcJ19yhOZOT0JecxPRke-iLtRRESKRx6RhwQN8y0B7dMEWuQERwDBTOgT3QRK_URsenTZ2mQWcIoiIDX39U5d8-esswSKucd_oE6llD0fOG8VAqbQcX0OlMn1VZXKBrkLQ2qYKDOKeBktGvfBQLPCVuk4LgmAzdzntL6e8GceKlf_xS3mzX5hcu6dYJisuqTpfV3N-b26xDM0E_WvuWAS0it6coCxjdirowMgl3d-FL5Mao0SBVTbYrFBKkvqN9jidocGSPX0eUGh220aJwXQ-Pf3fJ1LYhVwIcNEU5d9siQunpFKEV-2aS0ONRGD5J7aGaF-LmBotokMiR17wrH0nVWN43UnrcsBNwIc4TgIOq9Ai-CK4Xr1vyy6lgrdPG7tDc0zm03OIvrO01KMtM6wLR6YLKufAjzjx1EhiUxjoKh5FDObFzw0sNyyTknAJ85Ig-NbBH96LD5fBfkJ8Dgg5dP9gvs-j7j'
            payload = 'client_id=bc0cb5d2-ae0b-4e01-bfaf-815a95c2fe09&grant_type=refresh_token&scope=%20offline_access%20Sites.ReadWrite.All%20Files.ReadWrite.All%20Directory.ReadWrite.All&client_secret=H5T8Q~UWnuDB.hAwnFP3vOGXiieI9EH-VHZedbvO&refresh_token=1.AVYA1kMkGBjeqUmLuWiXnfXUTdK1DLwLrgFOv6-BWpXC_gmfAN5WAA.BQABAwEAAAADAOz_BQD0_9QeQo0_rnfMxT9H7dzeVdp2rs2lyfFyXNjo-ZVllgwqdGs9B6pLBo9VuldMkCb64bTR_9ehyO30t0lZQHqTayS-9N88efQKxv0thfRYENOwIxhfb2pSHlXO9XXZkAcEPE2ptWZTiRux6Cywg757Tox0f2GQ96QKMR75Zb9KzwnvjuReI8hqkvaal-Ozy4-3kRvqWM3U26AvZnoZZoamHcT53zxhNKFzYxqR1V6KVxJXnlJPEZQM4p_1IuG0EsJrEE_n3Pnrj0r6BlJkdfslFj1axxhZ4LEO-d-0CYhnn994f5tp5k12i0i1uQm173VhK2K_yUOxP1jYMPnsREe52fn4hOV1EvfGH7VLmrdaAd6sAf6aOlrM7UmAJyZsDAr9PbxMBBUcISofnFD70jFjukyJCrP63WGac4kq1ZNTaE4dMaZw9jT2N7mhj3AQwIovcwEOesbOKHMabK7GufSoC9eIwHKl-qqM5Nbp8ATWwyVNgJcEf5m69OomxEEgAPPW1O1xeXSNMSsSholWfL9X3uQE5G73AIPR_jJTzuQtWER2gtWY0T0gxcIdG0UtLJcr-i4-b49YUOa_7MUHpwniQLf_Oh--8f-DACO7ob4ak_Z-5WxbsmZzDRhbgbepAM9Wjv9OjGIp772FQZFFQt_d_BwdgrXcjxCM2N4Lpi3j2rzFSnwVAsC1Sd5cExP0Q5JEEzWsS3qcv7mv5i9LDERZq0M7nEbD3cluUJTwZJOtUEHUKzA7rYl5lTk00BSo8ePqkBwDKzpFNHXCC6Uu9FKMEspDXXHqX_NOXm2UTQ-9XBpbel_8pRwDuz3IaGZAucUiGw4BsHkh8KElTViXjlCD8zYvgTLOrbyX-XY0sQ03HhhhHqM1sFBuWfhDHhN_71lzGiaJaXxN7npROpcu7EcCZsIHmDsQ5IvX_WDQjkZQm2zKdYHNuy5-88PTiPkP_xyTTnZ30IYtV1zutbD0kkFYMaMTraOGLMzuWVN1R5gh_R3RqcxA0H_fnPx_tLMr5DJTM0n_frr7f2FQUf0u1G6_TzLXlaPSxdGW4WeWfxXtYTzVtameKY1kPBsJ8vVE5PGMBg2AOaTtDRubfayQwRSxXrcc9irdeyvCM3anhrixgCMaSgFthGO9wtq6SLTCboWO1F9MAUw3nH6BB8CQu5s_NHS8rb4ROK6_4AkWnBB-4Ssu--cQ-Fn3NKcLIRnf7YO8_7xWQHu7k7eka9SgLtTmZgWdvnA6hvw1WvC4oD76NNY9ADRwR7MHyCNVb3bP0SGSbtlwsm7C873GABNTpq-xTkVF4_nwQKtp0lnylzi-CBb1NDc-GOFrbu4iiolxvi2nZmpJqlEzzMA6mQ8Elgxh3SLaPK2LCgf9irtEcQDiMVDh5Dc969ZH_508yG-9aTp6Yp2s-fggkaqKOQ'
            headers = {
              'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'fpc=AvPoNvK1eFtEqjoJKyLNrjCTXgNEAQAAAFZUrt8OAAAA'
                }

            response = requests.request("GET", url, headers=headers, data=payload)
            resp=response.json()
            access_token=resp['access_token']
            # try:
            if (tempname[-1]=='pdf' or tempname[-1]=='PDF') :
                # file_path = os.path.join(dest_folder, filename)
                userid=user.id
                watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
                if watermarking.exists() and watermakingcheck :      
                    for i in watermarking:
                        i.user_id=userid
                    serializer = WatermarkingSerializer(watermarking,many=True)
                    data = serializer.data
                else:
                    data=False
                if data:
                    
                    tempfile='temp'+str(random.randint(0, 10000))
                    temp_path = os.path.join(dest_folder, tempfile)
                    if data_room.is_usa_blob==True:
                        sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                        block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==',sas_token = sas_url)
                    else:
                        sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                    
                    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                    container_name ='docullycontainer'
                    print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTTttttttttttttttttt')
                    # block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                    # if member.is_la_user or member.is_dataroom_admin:
                    #     block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                    # else:


                    try:
                        print('--------------download 2 first tryyyy')
                        # file_path = os.path.join(dest_folder, filename)
                        if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                            red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                            url=(red.file).split('/')
                            file_namee=url[-2]+'/'+url[-1]

                            block_blob_service.get_blob_to_path(container_name, file_namee, temp_path)
                        else:
                            block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)

                        from userauth import utils
                        ip = ip_add
                    
                        GeneratePDF(data,ip,user,dataroomid,)
                        watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
                        outputfile=file_path
                        # print(str(outputfile),'++++++++++++++++++++++++++++++')
                        pdf_writer=PyPDF2.PdfWriter()
                    
                        if (os.path.exists(temp_path)):

                            with open(temp_path, 'rb') as fh:
                                pdf=PyPDF2.PdfReader(fh,strict=False)
                                with open(watermarkfile,'rb') as watermarkfile:
                                    watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile,strict=False)
                                    for i in range(len(pdf.pages)):
                                        p=pdf.pages[i]
                                        p.merge_page(watermarkfile_pdf.pages[0])
                                        pdf_writer.add_page(p)
                                    # watermarkfile.close()
                                    # fh.close()
                                    with open(outputfile,'wb') as outputfileeee:
                                        pdf_writer.write(outputfileeee)
                                # outputfileeee.close()                    



                                if is_irm_protected:
                                    donwload_irm_files_single(outputfile,access_token,filename,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                                print('removeeee dirrr insideeee',temp_path)
                                os.remove(temp_path)
                                # os.remove(outputfile)
                                # os.chdir(temp_path)
                                # os.remove(tempfile)

                        if not is_irm_protected:
                            if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                print('---------------------insideee ifffff')
                                pass
                            else:
                                print('---------------------ooooutside  ifffff')
                                BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1,filename=filename)
                            BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                    except Exception as e:
                        print('-----------------------excc----------------',e)
                        # os.chdir(temp_path)
                        print('removeeee dirrr outside',file_path)

                        os.remove(temp_path)
                        if (os.path.exists(file_path)):
                            os.remove(file_path)

                        # os.chdir(dest_folder)
                        # print('------------------------------filessss',os.listdir())
                        # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        # if member.is_la_user or member.is_dataroom_admin:
                        #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        # else:
                        # try:
                        if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                            red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                            url=(red.file).split('/')
                            file_namee=url[-2]+'/'+url[-1]

                            block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                            if is_irm_protected:
                                donwload_irm_files_single(file_path,access_token,file_namee,url[-1],datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                        else:
                            block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                            if is_irm_protected:
                                donwload_irm_files_single(file_path,access_token,filename,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)


                        if not is_irm_protected:

                            if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                                pass
                            else:
                                BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1,filename=filename)
                                BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                                # os.remove(file_path)                            
                        # except Exception as e:
                        #     print('-----------------------------exceptyttt',e)
                        #     BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                        #     if (os.path.exists(file_path)):
                        #         os.remove(file_path)
                        # os.chdir(dest_folder)
                        # print('------------------------------filessss',os.listdir())

                else:
                    # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                    if data_room.is_usa_blob==True:
                        sas_token = '?sp=racwdli&st=2023-09-12T14:00:21Z&se=2024-08-31T22:00:21Z&spr=https&sv=2022-11-02&sr=c&sig=lrUSru11G6%2F8kp1nq4AW30xMbtdKYWJQ3EkQB4mghZk%3D'

                        block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                    else:
                        sas_token = '?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                    
                    container_name ='docullycontainer'
                    print('--------------except pdf  download file location',file_path)
                    print('--------------download 2 elsee')
                    # block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                    # if member.is_la_user or member.is_dataroom_admin:
                    #     block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                    # else:
                    # try:
                    print('--------------download 2 second try')
                    if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').exists():
                        red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exclude(version='0').last()
                        url=(red.file).split('/')
                        file_namee=url[-2]+'/'+url[-1]


                        print("-------------inside redect")

                        block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
                        if is_irm_protected:
                            donwload_irm_files_single(file_path,access_token,filename,url[-1],datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                    else:
                        print("-------------outside redect")
                        block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        if is_irm_protected:

                            donwload_irm_files_single(file_path,access_token,file_name,temp_pdf_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)

                    # os.remove(file_path)
                    if not is_irm_protected:
                        if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            pass
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1,filename=filename)
                            BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                        # except:
                        #     BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                    #     if (os.path.exists(file_path)):
                    #         os.remove(file_path)
                        print('--------------download 2 last except')
                    # os.remove(file_path)   


            else:
                print('--------------download 2 last else')
                # block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                if data_room.is_usa_blob==True:
                    block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
                else:
                    block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
                
                container_name ='docullycontainer'
                try:

                    print('-------------------------------filename============',file_name)
                    print('-------------------------------filepath============',file_path)

                    if Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).exists():
                        red=Redacted_Pdf.objects.filter(folder_id=datas.id,is_deleted=False,is_deleted_permanent=False,current_version=True).last()
                        url=(red.file).split('/')
                        print('====================urllllllll',url)
                        temp_name=url[-1]
                        print('===================tempname',temp_name)
                        file_namee=url[-2]+'/'+url[-1]
                        print('===------------------------file_nmeeee',file_namee)
                        file_path=file_path.split('.')
                        file_path[-1]='pdf'
                        temp_file_name='.'.join(file_path)
                        block_blob_service.get_blob_to_path(container_name, file_namee, temp_file_name)
                        if is_irm_protected:
                            donwload_irm_files_single(file_path,access_token,file_namee,temp_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)
                    else:
                        block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        if is_irm_protected:

                            end=filename.split('.')
                            end=end[-1]
                            print('-------------------------xxxxxxxxxxxxxxxxxxxxxxxx',end)
                            if end=='ppt' or end=='doc' or end=='xls':
                                if end=='doc':
                                    subprocess.run([
                                        "soffice", "--headless", "--convert-to", "docx", filename, "--outdir", '/home/cdms_backend/cdms2/media/irm_files'
                                    ], cwd='/home/cdms_backend/cdms2/media/irm_files')


                                if end=='ppt':
                                    subprocess.run([
                                        "soffice", "--headless", "--convert-to", "pptx", filename, "--outdir", '/home/cdms_backend/cdms2/media/irm_files'
                                    ], cwd='/home/cdms_backend/cdms2/media/irm_files')

                                if end=='xls':
                                    subprocess.run([
                                        "soffice", "--headless", "--convert-to", "xlsx", filename, "--outdir", '/home/cdms_backend/cdms2/media/irm_files'
                                    ], cwd='/home/cdms_backend/cdms2/media/irm_files')

                                filename=filename+'x'
                                print('-------------------------xxxxxxxxxxxxxxxxxxxxxxxx',filename)
                                temp_file_name=temp_file_name+'x'
                                file_path=file_path+'x'
                                print('-------------------------xxxxxxxxxxxxxxxxxxxxxxxx',temp_file_name)
                                print('-------------------------xxxxxxxxxxxxxxxxxxxxxxxxfile_path',file_path)

                                BulkDownloadstatus.objects.filter(id=objid).update(filename=filename)
                            donwload_irm_files_single(file_path,access_token,filename,temp_file_name,datas.id,user_id,dataroomid,bulkid,objid,data,alldata,file_name_2,group_s)


                    if not is_irm_protected:
                        if BulkDownloadFiles.objects.filter(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            pass    
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1,filecount=F('filecount')-1)
                            BulkDownloadFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                    # os.remove(file_path)   
                except Exception as e:
                    print('11111111111111111111111111111111111111111111111111111111----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                    BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                    if (os.path.exists(file_path)):
                        os.remove(file_path)
       
            # except Exception as e:

            #         print('4444444444444444444444444444444444444444444444444444444444----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            #         BulkDownloadfailFiles.objects.create(folder_id=datas.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            
    # return is_file_irm























# def downloadcount(request,datas,count,size):
#   user=request.user
#   flagch=0    
#   dataroomid=datas['dataroom']
#   member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
#   if member.is_la_user or member.is_dataroom_admin:
#       flagch=1
#   else:
#       try:
#           file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
#           if file_permission:
#               if file_permission.is_view_and_print_and_download==True:
#                   flagch=1
#       except:
#           pass
        

#   if flagch==1:       
#       count=count+1
#       print(datas['name'],count,'name')
#       size=size+datas['file_size_mb']
#       print(datas['name'],count,'name')

#   mergedata=str(count)+'*'+str(size)
#   return mergedata





def red_download(request,id1, dest_folder: str,dataroomid,objid,bulkid):

    if not os.path.exists(dest_folder):

        os.makedirs(dest_folder)
    if Redacted_Pdf.objects.filter(id=id1,is_deleted=False,is_deleted_permanent=False,).exists():
        red=Redacted_Pdf.objects.filter(id=id1,is_deleted=False,is_deleted_permanent=False,).last()
        url=(red.file).split('/')
        file_namee=url[-2]+'/'+url[-1]
        filename=red.name.split(".")
        filename[-1]='pdf'
        filename[-2]=filename[-2]+str(red.version)
        filename='.'.join(filename)
        file_path = os.path.join(dest_folder, filename)
        if red.dataroom.is_usa_blob==True:
            block_blob_service = BlockBlobService(account_name='uaestorageaccount', account_key='w7B2do4P0kzcaAWZytcl4dcLq9CSfyDVdyLojw1+drGvJK3EfmqWbtvRlJiqt8xpfGaErwYDd81Z+AStFuaMAQ==')
        else:
            block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==')
        
        container_name ='docullycontainer'
        block_blob_service.get_blob_to_path(container_name, file_namee, file_path)
        BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
        if bulkid!=None:
            r=RedactorVersion.objects.create(folder_id=red.folder.id,redact_id=red.id,user=request.user,event='redact download',dataroom_id=red.folder.dataroom.id,bulk_event_id=bulkid)
            print('----------------',r.bulk_event.id)
        else:
            RedactorVersion.objects.create(folder_id=red.folder.id,redact_id=red.id,user=request.user,event='redact download',dataroom_id=red.folder.dataroom.id)













def get_sub_listcount(request,fileid,count,size,dataroomid,idss):
            dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = fileid,is_folder=True,is_root_folder=False ,is_deleted=False)
            

            member = DataroomMembers.objects.filter(member_id=request.user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
            if member.is_la_user or member.is_dataroom_admin:
                print('---insidee')
                idss11 = DataroomFolder.objects.filter(parent_folder_id = fileid,is_folder=False,is_root_folder=False, is_deleted=False).values('id')
                idss.extend(idss11)
                count =count + DataroomFolder.objects.filter(parent_folder_id = fileid,is_folder=False,is_root_folder=False, is_deleted=False).count()
                size = float(size) + float((DataroomFolder.objects.filter(parent_folder_id = fileid,is_folder=False,is_root_folder=False, is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(parent_folder_id = fileid,is_folder=False,is_root_folder=False, is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)

            else:
                print('---outside')
                file_ids=DataroomGroupFolderSpecificPermissions.objects.filter(folder__is_deleted=False,folder__is_folder=False,dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id,is_view_and_print_and_download=True).values_list('folder_id', flat=True)
                idss11 = DataroomFolder.objects.filter(parent_folder_id= fileid,id__in=file_ids,is_folder=False,is_root_folder=False, is_deleted=False).values('id')
                idss.extend(idss11)
                count=count + DataroomFolder.objects.filter(parent_folder_id= fileid,id__in=file_ids,is_folder=False,is_root_folder=False, is_deleted=False).count()                
                size = float(size) + float((DataroomFolder.objects.filter(parent_folder_id = fileid,id__in=file_ids,is_folder=False,is_root_folder=False, is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(parent_folder_id = fileid,id__in=file_ids,is_folder=False,is_root_folder=False, is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0)

            for file in dataroom_folders:
                
                #print(file['name'],count,'foldername')
                mergedata, idss=get_sub_listcount(request,file.id,count,size,dataroomid,idss)
                datasplitted=mergedata.split('*')
                count=int(datasplitted[0])
                size=float(datasplitted[1])
                # varun-----
                # else:
                #   mergedata=downloadcount(request,file,count,size)
                #   datasplitted=mergedata.split('*')
                #   count=int(datasplitted[0])
                #   size=float(datasplitted[1])
            mergedata=str(count)+'*'+str(size)
            
            return mergedata, idss





def download(request,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid):
    user=request.user
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()              
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except:
            pass
        

    if flagch==1:       
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
            # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
            indexx=getIndexes(datas)

            # filedata = dataroom_folder_serializer.data
            filename =  str(datas['name']).replace(" ", "__")  # be careful with file names
            # if preindex=='' and pindex=='':
            #   filename = index+"_"+str(filename)
            # elif pindex=='':
            #   filename = preindex+'.0.'+index+"_"+str(filename)
            # elif preindex=='':
            #   filename = pindex+'.0.'+index+"_"+str(filename)
            # else:
            #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)

            file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
            # print(file_name,'ttttttt')
            if docaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")

                if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            if exelaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")
                if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            tempname=filename.split('.')
            # print(exelaspdf,tempname,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
            if dataindex==True:
                filename=str(indexx)+'_'+str(filename)
                # print(filename,'===============')
                # print(file_name,'@@@@@@@@@@@@@@@@@')

            file_path = os.path.join(dest_folder, filename)
            BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid)
            print(filename,datas['id'],'uuuuuuuuuuuuuu')

            # try:

            if (tempname[-1]=='pdf' or tempname[-1]=='PDF')  and watermakingcheck:

                # file_path = os.path.join(dest_folder, filename)

                userid=user.id      
                watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
                for i in watermarking:
                    i.user_id=userid
                serializer = WatermarkingSerializer(watermarking,many=True)
                data = serializer.data
                if data:
                                            tempfile='temp'+str(random.randint(0, 10000))
                                            temp_path = os.path.join(dest_folder, tempfile)
                                            block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                                            container_name ='docullycontainer'
                                            # print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTT')
                                            block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                                            from userauth import utils
                                            ip = utils.get_client_ip(request)
                                            GeneratePDF(data,ip,user,dataroomid)
                                            watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
                                            outputfile=file_path
                                            # print(str(outputfile),'++++++++++++++++++++++++++++++')
                                            pdf_writer=PyPDF2.PdfWriter()
                                            if (os.path.exists(temp_path)):
                                                with open(temp_path, 'rb') as fh:
                                                    pdf=PyPDF2.PdfReader(fh,strict=False)
                                                    with open(watermarkfile,'rb') as watermarkfile:
                                                        watermarkfile_pdf=PyPDF2.PdfReader(watermarkfile,strict=False)
                                                        for i in range(len(pdf.pages)):
                                                            p=pdf.pages[i]
                                                            p.merge_page(watermarkfile_pdf.pages[0])
                                                            pdf_writer.add_page(p)
                                                        with open(outputfile,'wb') as outputfileeee:
                                                            pdf_writer.write(outputfileeee)
                                                            os.remove(temp_path)

                else:
                    block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                    container_name ='docullycontainer'
                    print('rushikesh gaikwad',file_name,file_path)
                    print(file_path,'oooooooo')
                    block_blob_service.get_blob_to_path(container_name, file_name ,file_path)

            else:
                block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                container_name ='docullycontainer'
                print('rushikesh gaikwad',file_name,file_path)
                print(file_path,'oooooooo')
                block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            # except:
            #   pass
            # user = request.user
            # bulk_activity_tracker = BulkActivityTracker()
            # bulk_activity_tracker.user_id = user.id
            # bulk_activity_tracker.save()

            # urllib.request.urlretrieve(url,file_path)


            # r = requests.get(url, stream=True)
            # if r.ok:
            #     print("saving to", os.path.abspath(file_path))
            #     with open(file_path, 'wb') as f:
            #         for chunk in r.iter_content(chunk_size=1024 * 8):
            #             if chunk:
            #                 f.write(chunk)
            #                 f.flush()
            #                 os.fsync(f.fileno())
            # else:  # HTTP status code 4XX/5XX
            #     print("Download failed: status code {}\n{}".format(r.status_code, r.text))

def get_sub_list(request,id, directory,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid):
    user=request.user
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()    
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except:
            pass

    if flagch==1: 
        data  = []
        subfolder = []
        uploaded_by = ''
        indexx=getIndexes(datas)
        dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = id, is_root_folder=False, is_deleted=False).order_by('index')
        dataroom_folder_serializer = DataroomFolderSerializer(dataroom_folders, many=True)

        subfolder = dataroom_folder_serializer.data
        for file in subfolder:
            if file['is_folder']:
                os.mkdir(str(directory)+'/'+str(indexx)+'.'+str(file['index'])+'_'+str(file['name']).replace(' ','__'))
                BulkDownloadFiles.objects.create(folder_id=file['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid)
                get_sub_list(request,file['id'], str(directory)+'/'+str(indexx)+'.'+str(file['index'])+'_'+str(file['name']).replace(' ','__'),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid)
            else:
                # print(file['path'], directory,'thischeck')
                download(request,file['path'], str(directory).replace(' ','__'),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid)




def get_sub_listtwo(request,id, directory,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid):
    user=request.user
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()    
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except:
            pass

    if flagch==1: 
        data  = []
        subfolder = []
        uploaded_by = ''
        indexx=getIndexes(datas)
        dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = id, is_root_folder=False, is_deleted=False).order_by('index')
        dataroom_folder_serializer = DataroomFolderSerializer(dataroom_folders, many=True)

        subfolder = dataroom_folder_serializer.data
        for file in subfolder:
            if file['is_folder']:
                print("0000000000000000-----------",file['index'],file['name'])
                if dataindex == True:
                    os.mkdir(str(directory)+'/'+str(indexx)+'.'+str(file['index'])+' '+str(file['name']))
                    BulkDownloadFiles.objects.create(folder_id=file['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid)
                    get_sub_listtwo(request,file['id'], str(directory)+'/'+str(indexx)+'.'+str(file['index'])+' '+str(file['name']),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid)
                else:
                    os.mkdir(str(directory)+'/'+str(file['name']))
                    BulkDownloadFiles.objects.create(folder_id=file['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid)
                    get_sub_listtwo(request,file['id'], str(directory)+'/'+str(file['name']),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid)
            else:
                # print(file['path'], directory,'thischeck')
                downloadtwo(request,file['path'], str(directory),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid)




def get_sub_listtwo2(user_id,id, directory,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name):
    user=User.objects.get(id=user_id)
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas.id,dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()    
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except:
            pass

    if flagch==1: 
        data  = []
        subfolder = []
        uploaded_by = ''
        indexx=getIndexes_with_queryset(datas)
        dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = id, is_root_folder=False, is_deleted=False).order_by('index')
        # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_folders, many=True)

        # subfolder = dataroom_folder_serializer.data
        # for file in subfolder:
        for file in dataroom_folders:
            if file.is_folder:
                print("0000000000000000-----------",file.index,file.name)
                if dataindex == True:
                    os.mkdir(str(directory)+'/'+str(indexx)+'.'+str(file.index)+' '+str(file.name))
                    BulkDownloadFiles.objects.create(folder_id=file.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid)
                    get_sub_listtwo2(user_id,file.id, str(directory)+'/'+str(indexx)+'.'+str(file.index)+' '+str(file.name),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)
                else:
                    os.mkdir(str(directory)+'/'+str(file.name))
                    BulkDownloadFiles.objects.create(folder_id=file.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid)
                    get_sub_listtwo2(user_id,file.id, str(directory)+'/'+str(file.name),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)
            else:
                # print(file['path'], directory,'thischeck')
                try:
                    downloadtwo2(user_id,file.path.url, str(directory),file,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid,ip_add,data,alldata,file_name)
                except Exception as e:
                    print('-------------------------------------------exception utils get_sub_list',e)
                    BulkDownloadfailFiles.objects.create(folder_id=file.id,user_id=user_id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)





def download_drm(request,url: str, dest_folder: str,datas,dataroomid,dataindex,bulkid):
        user=request.user
        flagch=0    
        member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
        if member.is_la_user or member.is_dataroom_admin:
            flagch=1
        else:
            try:
                file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()    
                if file_permission:
                    if file_permission.is_shortcut==True:
                        flagch=1
            except:
                pass

        if flagch==1: 
                from constants import constants
                import os
                import shutil
                from .models import FolderDrmDownload
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                indexx=getIndexes(datas)


                base_url = constants.backend_ip2
                # print("the value of pk",pk)
                docu = DataroomFolder.objects.get(id = datas['id'])

                docu_serializer = DataroomFolderSerializer(docu)
                datas = docu_serializer.data
                file_name = datas.get('name')
                iconFile = 'default.ico'
                #print(datas.get('name').split('.')[0])
                if datas.get('name'):
                    iconFile = file_name[len(file_name)-1]+'.ico'

                if not request.user.is_icon_downloaded:
                    User.objects.filter(id=request.user.id).update(is_icon_downloaded=True)
                os.chdir('/home/cdms_backend/cdms2/media/fileviewcatche/')
                file_name =str(file_name)+'.txt'
                print('---------file location',file_name)
                if dataindex==True:
                    file_name=str(indexx)+'_'+str(file_name)
                    print('---------file location',file_name)
                print('pwddddddddddddddd',os.getcwd())
                
                f= open(file_name,"w+")
                print('-------ffff',f)
                url = 'URL='+str(base_url)+'/file-view/'+str(datas.get('id'))+'/'+str(request.user.id)+'/'

                data = ['[InternetShortcut]']
                tempnamereplace=datas.get('name').split('.')[-1]
                url_file = datas.get('name').replace('.'+str(tempnamereplace),'').replace(' ','_')
                # print('url_file',url_file)
                # #print('url ------',url)
                url_file_ext = datas.get('name').split('.')
                data.append(url)

                url_file=str(url_file)+'.url'

                if dataindex==True:
                    url_file=str(indexx)+'_'+str(url_file)
                file_path = os.path.join(dest_folder, url_file)

                for i in data:  
                    f.write("%s\r\n" %(i))
                f.close()

                new_filename = file_name.split('.')

                shutil.copy2("/home/cdms_backend/cdms2/media/fileviewcatche/"+file_name, file_path)

                # file_name_split = file_name.split("/")
                # if os.path.exists(file_name_split[-1]):
                #   with open(file_name_split[-1], 'rb') as fh:
                #       print("fh.read==>",fh.read())
                # user = request.user
                # bulk_activity_tracker = BulkActivityTracker()
                # bulk_activity_tracker.user_id = user.id
                # bulk_activity_tracker.save()


                FolderDrmDownload.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid)


def get_sub_list_drm(request,id, directory,datas,dataroomid,dataindex,bulkid):
        user=request.user
        flagch=0    
        member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
        if member.is_la_user or member.is_dataroom_admin:
            flagch=1
        else:
            try:                    
                file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()    
                if file_permission:
                    if file_permission.is_shortcut==True:
                        flagch=1
            except:
                pass

        if flagch==1:

            data  = []
            subfolder = []
            uploaded_by = ''
            indexx=getIndexes(datas)
            dataroom_folders = DataroomFolder.objects.filter(parent_folder_id = id, is_root_folder=False, is_deleted=False).order_by('index')
            dataroom_folder_serializer = DataroomFolderSerializer(dataroom_folders, many=True)

            subfolder = dataroom_folder_serializer.data

            for file in subfolder:
                if file['is_folder']:
                    os.mkdir(str(directory)+'/'+str(indexx)+'.'+str(file['index'])+'_'+str(file['name']).replace(' ','__'))
                    FolderDrmDownload.objects.create(user_id=request.user.id,dataroom_id=dataroomid,folder_id=file['id'],bulk_event_id=bulkid)
                    get_sub_list_drm(request,file['id'], str(directory)+'/'+str(indexx)+'.'+str(file['index'])+'_'+str(file['name']).replace(' ','__'),file,dataroomid,dataindex,bulkid)
                else:
                    # print(file['path'], directory,'thischeck')
                    download_drm(request,file['path'], str(directory).replace(' ','__'),file,dataroomid,dataindex,bulkid)
                    # print("here see the file of drm download here -->",file['id'])
                    # FolderDrmDownload.objects.create(user_id=request.user.id,dataroom_id=dataroomid,folder_id=file['id'],bulk_event_id=bulk_activity_tracker.id)










from datetime import datetime
import pytz










def convert_to_kolkata(dubai_datetime,timezone):
    # Set the timezone for Dubai
    dubai_tz = pytz.timezone('Asia/Dubai')
    # Set the timezone for Kolkata
    kolkata_tz = pytz.timezone(timezone)

    # Ensure the datetime is timezone-aware for Dubai
    dubai_aware = dubai_tz.localize(dubai_datetime)

    # Convert the datetime to Kolkata timezone
    kolkata_aware = dubai_aware.astimezone(kolkata_tz)

    return kolkata_aware




def getIndexes12(data):
    indexes = True
    if data['folder__is_folder'] == True:
        index = str(data['folder__index'])
    else:
        index = "0."+str(data['folder__index'])
    parent_folder = data['folder__parent_folder']
    while indexes == True:
        if parent_folder == None:
            indexes = False
        else:
            folder = DataroomFolder.objects.get(id=parent_folder)
            index = str(folder.index)+'.'+str(index)
            parent_folder = folder.parent_folder_id
    # print("Index------", index)
    return index



def downloadtwoUpstatus(request,url: str, dest_folder: str,datas,docaspdf,exelaspdf,dataroomid,dataindex,watermakingcheck,bulkid,objid):
    user=request.user
    flagch=0    
    member = DataroomMembers.objects.filter(member_id=user.id, dataroom_id=dataroomid,is_deleted=False,memberactivestatus=True).first()
    if member.is_la_user or member.is_dataroom_admin:
        flagch=1
    else:
        try:
            file_permission = DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=datas['folder_id'],dataroom_id=dataroomid, dataroom_groups_id=member.end_user_group.first().id).first()               
            if file_permission:
                if file_permission.is_view_and_print_and_download==True:
                    flagch=1
        except Exception as e:
            print('permissionnnnnnn----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            pass
        

    if flagch==1:       
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            # dataroom_file = DataroomFolder.objects.get(id = id, is_root_folder=False, is_deleted=False,is_folder=False)
            # dataroom_folder_serializer = DataroomFolderSerializer(dataroom_file, many=True)
            indexx=getIndexes12(datas)

            # filedata = dataroom_folder_serializer.data
            filename =  str(datas['folder__name'])  # be careful with file names
            # if preindex=='' and pindex=='':
            #   filename = index+"_"+str(filename)
            # elif pindex=='':
            #   filename = preindex+'.0.'+index+"_"+str(filename)
            # elif preindex=='':
            #   filename = pindex+'.0.'+index+"_"+str(filename)
            # else:
            #   filename = preindex+'.'+pindex+'.0.'+index+"_"+str(filename)
            # file_name_list=list()
            # file_name1 = datas['path'].split("/")
            # file_name_list.append(file_name1[4])
            # file_name_list.append(file_name1[5])
            # print('------filename111111111111111',file_name_list)
            print('------urllllllllllllllllllllllllllllllllllllll',url)
            #------
            file_name=url

            # file_name = url.split("/")[-2].replace("%20", " ")+"/"+url.split("/")[-1].replace("%20", " ")
            # file_name=file_name.replace("%E2%80%93","–")
            # print('=====',url.split("/")[-2],'rreeeeeeeeeee',url.split("/")[-1])

            #----
            # print('----------pathhhhhhm beforeeeeeeeeee',datas['path'],sas_url)
            # datas['path']=datas['path'].replace("%E2%80%93", "")
            # print('----------pathhhhhhafterrrrrr',datas['path'])
            print('------filename befire %20 afterrrrrrrr',file_name)
            if docaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")

                if pathsort2[-1]=='pptx' or pathsort2[-1]=='docx' or pathsort2[-1]=='ppt' or pathsort2[-1]=='doc':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            if exelaspdf==True:
                pathsort2=file_name.split(".")
                filename=filename.split(".")
                if pathsort2[-1]=='xlsx' or pathsort2[-1]=='xls' or pathsort2[-1]=='csv':
                    pathsort2[-1]='pdf'
                    filename[-1]='pdf'
                file_name='.'.join(pathsort2)
                filename='.'.join(filename)

            tempname=filename.split('.')
            # print('--------------------------------------',filename)
            # print(datas,filename,'RRRRRRRRRRRRRRRRRRHHHHHHHHHHHHHHHHHHHHHSSSSSSSSSSSSSSSSSSSSSSS')
            if dataindex==True:
                filename=str(indexx)+' '+str(filename)
                # print(filename,'===============')
                # print(file_name,'@@@@@@@@@@@@@@@@@')

            file_path = os.path.join(dest_folder, filename)
            # print('-----------file patghhg',file_path)
            # BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            # BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            # print('--------------------filennameeeee---------',filename)
            try:
                if (tempname[-1]=='pdf' or tempname[-1]=='PDF') and watermakingcheck:
                    # file_path = os.path.join(dest_folder, filename)
                    userid=user.id      
                    watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
                    for i in watermarking:
                        i.user_id=userid
                    serializer = WatermarkingSerializer(watermarking,many=True)
                    data = serializer.data
                    if data:
                        tempfile='temp'+str(random.randint(0, 10000))
                        temp_path = os.path.join(dest_folder, tempfile)
                        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                        container_name ='docullycontainer'
                        print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTTttttttttttttttttt')
                        block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
                        from userauth import utils
                        ip = utils.get_client_ip(request)
                        try:
                            GeneratePDF(data,ip,user,dataroomid)
                            watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
                            outputfile=file_path
                            # print(str(outputfile),'++++++++++++++++++++++++++++++')
                            pdf_writer=PyPDF2.PdfFileWriter()
                        
                            if (os.path.exists(temp_path)):
                                with open(temp_path, 'rb') as fh:
                                    pdf=PyPDF2.PdfFileReader(fh,strict=False)
                                    with open(watermarkfile,'rb') as watermarkfile:
                                        watermarkfile_pdf=PyPDF2.PdfFileReader(watermarkfile,strict=False)
                                        for i in range(pdf.getNumPages()):
                                            p=pdf.getPage(i)
                                            p.mergePage(watermarkfile_pdf.getPage(0))
                                            pdf_writer.addPage(p)
                                        # watermarkfile.close()
                                        # fh.close()
                                        with open(outputfile,'wb') as outputfileeee:
                                            pdf_writer.write(outputfileeee)
                                    # outputfileeee.close()                                 
                                    os.remove(temp_path)
                        except:
                            os.remove(temp_path)
                            block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        if BulkDownloadFiles.objects.filter(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            BulkDownloadfailFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            pass
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                    else:
                        block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                        container_name ='docullycontainer'
                        print('--------------except pdf  download file location',file_path)
                        block_blob_service.get_blob_to_path(container_name, file_name ,file_path)

                        if BulkDownloadFiles.objects.filter(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            BulkDownloadfailFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            pass
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

                else:
                    block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
                    container_name ='docullycontainer'
                    try:

                        print('-------------------------------filename============',file_name)
                        print('-------------------------------filepath============',file_path)


                        block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
                        if BulkDownloadFiles.objects.filter(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
                            BulkDownloadfailFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                            pass    
                        else:
                            BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
                            BulkDownloadFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                    except Exception as e:
                        print('11111111111111111111111111111111111111111111111111111111----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                        BulkDownloadfailFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            # except AzureMissingResourceHttpError:
            #   if os.path.exists(temp_path):
            #       os.remove(temp_path)
            #   try:
            #       forblob_notfoundissue(datas)
            #       if (tempname[-1]=='pdf' or tempname[-1]=='PDF') and watermakingcheck:
            #           # file_path = os.path.join(dest_folder, filename)
            #           userid=user.id      
            #           watermarking = Watermarking.objects.filter(dataroom_id=int(dataroomid)).order_by('id')
            #           for i in watermarking:
            #               i.user_id=userid
            #           serializer = WatermarkingSerializer(watermarking,many=True)
            #           data = serializer.data
            #           if data:
            #               tempfile='temp'+str(random.randint(0, 10000))
            #               temp_path = os.path.join(dest_folder, tempfile)
            #               block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
            #               container_name ='docullycontainer'
            #               # print(container_name,file_name,temp_path,'TTTTTTTTTTTTTTT')
            #               block_blob_service.get_blob_to_path(container_name, file_name ,temp_path)
            #               from userauth import utils
            #               ip = utils.get_client_ip(request)
            #               try:
            #                   GeneratePDF(data,ip,user,dataroomid)
            #                   watermarkfile="/home/cdms_backend/cdms2/Admin_Watermark/"+str(dataroomid)+".pdf"
            #                   outputfile=file_path
            #                   # print(str(outputfile),'++++++++++++++++++++++++++++++')
            #                   pdf_writer=PyPDF2.PdfFileWriter()
                            
            #                   if (os.path.exists(temp_path)):
            #                       with open(temp_path, 'rb') as fh:
            #                           pdf=PyPDF2.PdfFileReader(fh,strict=False)
            #                           with open(watermarkfile,'rb') as watermarkfile:
            #                               watermarkfile_pdf=PyPDF2.PdfFileReader(watermarkfile,strict=False)
            #                               for i in range(pdf.getNumPages()):
            #                                   p=pdf.getPage(i)
            #                                   p.mergePage(watermarkfile_pdf.getPage(0))
            #                                   pdf_writer.addPage(p)
                                            
            #                               with open(outputfile,'wb') as outputfileeee:
            #                                   pdf_writer.write(outputfileeee)
            #                                   outputfileeee.close()
            #                                   watermarkfile.close()
            #                                   fh.close()
            #                                   os.remove(temp_path)
            #               except:
            #                   os.remove(temp_path)
            #                   block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)

            #           else:
            #               block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
            #               container_name ='docullycontainer'
            #               block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #       else:
            #           block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
            #           container_name ='docullycontainer'
            #           try:
            #               block_blob_service.get_blob_to_path(container_name, file_name ,file_path)
            #               if BulkDownloadFiles.objects.filter(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid).exists():
            #                   pass
            #               else:
            #                   BulkDownloadstatus.objects.filter(id=objid).update(successfilescount=F('successfilescount')+1)
            #                   BulkDownloadFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #           except Exception as e:
            #               print('22222222222222222222222222222222222222222222222222----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            #               BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            #   except Exception as e:
            #       if os.path.exists(temp_path):
            #           os.remove(temp_path)
            #       print('33333333333333333333333333333333333333333333333333333333333----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
            #       BulkDownloadfailFiles.objects.create(folder_id=datas['id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
                ddddd=BulkDownloadstatus.objects.filter(id=objid).first()
                print('/=/=/=/=/=/=/==/=/counttt939393939)))',ddddd.successfilescount)
            except Exception as e:
                    if (os.path.exists(temp_path)):
                        os.remove(temp_path)
                    print('4444444444444444444444444444444444444444444444444444444444----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- e',e)
                    BulkDownloadfailFiles.objects.create(folder_id=datas['folder_id'],user_id=request.user.id,dataroom_id=dataroomid,bulk_event_id=bulkid,batch_id=objid)
            







