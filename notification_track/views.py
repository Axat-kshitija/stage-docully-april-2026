from django.shortcuts import render
from rest_framework.views import APIView
from userauth.models import TokenAuthentication,Token
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from notifications.models import AllNotifications, Message
from notifications.serializers import AllNotificationsSerializer,newAllNotificationsSerializer
import operator
from users_and_permission.models import DataroomMembers, DataroomGroups, RcentUpdate, DataroomGroupFolderSpecificPermissions,DataroomGroupPermission
from users_and_permission.serializers import DataroomMembersSerializer, DataroomGroupsSerializer, RcentUpdateSerializer
from data_documents.models import *
from data_documents.serializers import *
from userauth.serializers import UserSerializer
import datetime
from django.db.models import Max, F, Min, Q, Sum
from rest_framework import pagination, serializers
paginator = pagination.PageNumberPagination()
from data_documents.models import *

class GetDataroomNotificationCount(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("get method called")
        user = request.user
        data = []
        dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk, read=False).count()
        
        user_notification_list = AllNotifications.objects.filter(user_id=user.id, read=False).count()
        
        # print("user.id", user.id, int(pk))
        user_dataroom_notification_list = AllNotifications.objects.filter(dataroom_id = int(pk),user_id=user.id, read=False).count()
        # print("user_dataroom_notification_list", user_dataroom_notification_list)
        a = []
        message_list = Message.objects.filter(main=True).filter(Q(user_rec_id=user.id) | Q(user_send_id=user.id))
        msg_count = 0
        for msg in message_list:
            msg_msg_count = Message.objects.filter(msg_id=msg.id, read=False, user_rec_id=user.id).filter(~Q(latestsender_id=user.id)).count()
            if msg_msg_count > 0:
                msg_count =msg_count+1
        # print(msg_count,'&&&&&&&&&***************')
        datas = {'user_notification_count':user_notification_list,'user_datroom_count':user_dataroom_notification_list, 'dataroom_notification_count': dataroom_notification_list, 'dataroom_message_count': msg_count}
        # print(datas)
        return Response(datas, status=status.HTTP_201_CREATED)

class GetDataroomNotification(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("get method called")
        user = request.user
        data = []
        count = 0
        type = request.GET.get("type")
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

        # print(type)
        members = DataroomMembers.objects.filter(member_id=user.id).values('member_id')
        # print("Members", members, pk)
        permission_member_group = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=pk).last()
        qna_permission_group = False
        if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
            qna_permission_group = True
        try:
            qna_permission = DataroomGroupPermission.objects.filter(dataroom_id=pk,dataroom_groups_id=permission_member_group.end_user_group.last().id,is_q_and_a=True)
            if qna_permission is not None:
                qna_permission_group = True
                exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=permission_member_group.end_user_group.last().id,is_view_only=False,is_no_access=True)]
        except Exception as e:
            exclude_no_access_file = []
        # print("exclude_no_access_file",exclude_no_access_file)
        if type == "fixed":
            # print("fixed")
            if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
                dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                count = AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).count()
                all_notification_list = list(AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date').values())
                file_or_folder_moved_list = list(FolderOrFileMove.objects.filter(dataroom_id=pk,user_id=user.id).exclude(folder_id__in=exclude_no_access_file).values())
            else:
                qs_without_qna_perm = AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                qs_with_qna_perm = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                if qna_permission_group:
                    dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
                else:
                    dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
                # dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).order_by('-created_date')
                count = dataroom_notification_list.count()
                all_notification_list = list(AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date').values())
                file_or_folder_moved_list = list(FolderOrFileMove.objects.filter(dataroom_id=pk,user_id=user.id).exclude(folder_id__in=exclude_no_access_file).exclude(Q(folder_id=None) | Q(folder__is_deleted=False)).values())
            for i in all_notification_list:
                for j in file_or_folder_moved_list:
                    date_time_obj_one = datetime.datetime.strftime(i["created_date"], '%Y-%m-%d %H:%M')
                    date_time_obj_two = datetime.datetime.strftime(j["created_date"], '%Y-%m-%d %H:%M')
                    if date_time_obj_one == date_time_obj_two:
                        if j["event"] == 'Move Folder':
                            i["event"] = "Moved Folder"
                        elif j["event"] == 'Move File':
                            i["event"] = "Moved File"
                        else:
                            pass
        else:
            # print("else")
            if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
                AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder__is_deleted=True).update(read=True)
                dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                count = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder__is_deleted=True).count()
                all_notification_list = list(AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder_id__is_deleted=True).order_by('-created_date').values())
                file_or_folder_moved_list = list(FolderOrFileMove.objects.filter(dataroom_id=pk,user_id=user.id).exclude(folder_id__in=exclude_no_access_file,folder__is_deleted=True).values())
            else:
                # print("dataroom else not")
                AllNotifications.objects.filter(dataroom_id=pk, user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder__is_deleted=True).update(read=True)
                qs_without_qna_perm = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                qs_with_qna_perm = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                if qna_permission_group:
                    # print("permission true")
                    dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
                else:
                    # print("permission is false")
                    dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
                # dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
                
                count = dataroom_notification_list.count()
                # count = AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder__is_deleted=True).count()
                all_notification_list = list(AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).exclude(dataroom_folder_id__in=exclude_no_access_file,dataroom_folder_id__is_deleted=True).order_by('-created_date').values())
                file_or_folder_moved_list = list(FolderOrFileMove.objects.filter(dataroom_id=pk,user_id=user.id).exclude(folder_id__in=exclude_no_access_file,folder__is_deleted=True).values())

            for i in all_notification_list:
                for j in file_or_folder_moved_list:
                    date_time_obj_one = datetime.datetime.strftime(i["created_date"], '%Y-%m-%d %H:%M')
                    date_time_obj_two = datetime.datetime.strftime(j["created_date"], '%Y-%m-%d %H:%M')
                    if date_time_obj_one == date_time_obj_two:

                        if j["event"] == 'Move Folder' :
                            i["dataroom"] = list(Dataroom.objects.filter(id=i["dataroom_id"]).values())
                            i["event"] = "Moved Folder"
                        elif j["event"] == 'Move File':
                            i["dataroom"] = list(Dataroom.objects.filter(id=i["dataroom_id"]).values())
                            i["event"] = "Moved File"
                        else:
                            pass


        # print("see data --->",AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).order_by('-created_date').values())
        # new_list = list(AllNotifications.objects.filter(dataroom_id=pk , user_id__in=members).order_by('-created_date').values())
        # another_list = list(FolderOrFileMove.objects.filter(dataroom_id=pk,user_id=user.id).values())
        # for i in new_list:
        #     for j in another_list:
        #         date_time_obj_one = datetime.datetime.strftime(i["created_date"], '%Y-%m-%d %H:%M')
        #         date_time_obj_two = datetime.datetime.strftime(j["created_date"], '%Y-%m-%d %H:%M')
        #         if date_time_obj_one == date_time_obj_two:
        #             if int(j["event"]) == 1:
        #                 i["event"] = "Moved Folder"
        #             elif int(j["event"]) == 2:
        #                 i["event"] = "Moved File"
        #             else:
        #                 pass
        # print(new_list)
                    # print(date_time_obj_one,"true",date_time_obj_two,j["event"],j["file_name"])
        # print(list(page),"Notification type")
        data = newAllNotificationsSerializer(dataroom_notification_list, many=True).data
        # print(data[0]['created_date'],'99999999999999900000000000000')
        # updatedata=Bulkuploadstatus.objects.filter(user_id=user.id, dataroom_id=pk).order_by('-created_date')
        # count= count+int(updatedata.count())
        # data1 = BulkuploadstatusSerializer(updatedata, many=True).data
        # data.extend(data1)
        # for each in dataroom_notification_list:
        #     if each.dataroom_member:
        #         d_m = DataroomMembers.objects.filter(id=int(each.dataroom_member)).first()
        #         if d_m:
        #             # if user.id != d_m.member.id and user.id != d_m.member_added_by_id and user.date_joined < d_m.date_updated:
        #             # if user.id != d_m.member_added_by_id.id:
        #             serializers = DataroomMembersSerializer(d_m)
        #             data.append(serializers.data)

        #     if each.dataroom_groups:
        #         d_g = DataroomGroups.objects.filter(id=int(each.dataroom_groups)).first()
        #         if d_g:
        #             # if user.id != d_g.group_created_by.id:
        #             serializers = DataroomGroupsSerializer(d_g)
        #             data.append(serializers.data)

        #     if each.dataroom_folder:
        #         d_folder = DataroomFolder.objects.filter(id=int(each.dataroom_folder)).first()
        #         if d_folder:
        #             # if user.id != d_folder.user.id:
        #             serializers = DataroomFolderSerializer1(d_folder)
        #             data.append(serializers.data)

        #     if each.dataroom_updates:
        #         d_update = RcentUpdate.objects.filter(id=int(each.dataroom_updates)).first()
        #         if d_update:
        #             # if user.id != d_update.user.id:
        #             serializers = RcentUpdateSerializer(d_update)
        #             data.append(serializers.data)
        #     for da in data:
        #         da['created_date'] = str(each.created_date)
        # import datetime
        data = sorted(data,key=lambda x : x['created_date'],reverse=True)[page2:page1]
        for i in data:
            dateobject=datetime.datetime.strptime(str(i['created_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            i['created_date'] = dateobject.strftime('%Y-%m-%d %H:%M:%S.%f')
            # print(i['dataroom']['dataroom_name'],'dataroom ------>')
            
            i['dataroom']['dataroom_name'] = i['dataroom']['dataroom_name'].replace('_'," ")
            i['dataroom']['dataroom_nameFront'] =   i['dataroom']['dataroom_nameFront'].replace('_'," ")
            # i['dataroom_folder']['dataroom']['dataroom_name'] = i['dataroom_folder']['dataroom']['dataroom_name'].replace('_'," ").replace('_'," ").replace('_'," ")

            # i['dataroom_folder']['dataroom']['dataroom_nameFront'] = i['dataroom_folder']['dataroom']['dataroom_nameFront'].replace('_'," ").replace('_'," ").replace('_'," ")
        




        return Response({'data':data,'size':count,'event':all_notification_list}, status=status.HTTP_201_CREATED)



# harish 
class GetAllNotification(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


    def get(self, request, format=None):
        # print("get method called")
        user = request.user
        type = request.GET.get("type")
        # print("dataaaaaaaaaaaa", type)
        data = []
        count = 0
        # member = DataroomMembers.objects.filter(member_id=user.id).values('dataroom_id')
        # qna_permission_group = False
        # permission_member_group = DataroomMembers.objects.filter(member_id=user.id,dataroom_id__in=member,is_deleted=False).last()
        
        # try:
        #   exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=permission_member_group.end_user_group.last().id,is_view_only=False,is_no_access=True)]
        #   qna_permission = DataroomGroupPermission.objects.filter(dataroom_groups_id=permission_member_group.end_user_group.first().id,is_q_and_a=True)
        #   if qna_permission is not None:
        #       qna_permission_group = True
        # except Exception as e:
        #   exclude_no_access_file = []
        # print("exclude_no_access_file",exclude_no_access_file)
        dataroom_notification_list=AllNotifications.objects.filter(user_id=user.id).order_by('-created_date')
        dataroom_notification_listcount=AllNotifications.objects.filter(user_id=user.id,read=False)
        if type == "fixed":
            pass
            # if permission_member_group:
            #   if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
            #       qna_permission_group = True
            #       count = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).count()
            #       dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #       unread_count=AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file).count()
            #   else:
            #       qs_without_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #       qs_with_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #       unread1 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)
            #       unread2 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)
                    
            #       if qna_permission_group:
            #           dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
            #           dataroom_notification_listcount = unread1.union(unread2)

            #       else:
            #           dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
            #           dataroom_notification_listcount = unread1.union(unread2)

            #       count = dataroom_notification_list.count()
            #       unread_count=dataroom_notification_listcount.count()
            # else:
            #       qs_without_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #       qs_with_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #       unread1 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)
            #       unread2 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)
                    
            #       if qna_permission_group:
            #           dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
            #           dataroom_notification_listcount = unread1.union(unread2)

            #       else:
            #           dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
            #           dataroom_notification_listcount = unread1.union(unread2)

            #       count = dataroom_notification_list.count()
            #       unread_count=dataroom_notification_listcount.count()
            # print("other list if",AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).values('dataroom_folder'))
        else:
            AllNotifications.objects.filter(user_id=user.id).update(read=True)
            # if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
            #   dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #   # print("other list else",AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).values('dataroom_folder'))
            #   count = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).count()
            #   unread_count=AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file).count()
            # else:
            #   qs_without_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #   qs_with_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
            #   unread1 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)
            #   unread2 = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group,read=False).exclude(dataroom_folder_id__in=exclude_no_access_file)

            #   if qna_permission_group:
            #       dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
            #       dataroom_notification_listcount = unread1.union(unread2)

            #   else:
            #       dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
            #       dataroom_notification_listcount = unread1.difference(unread2)

        count = dataroom_notification_list.count()
        unread_count=dataroom_notification_listcount.count()
        # updatedata=Bulkuploadstatus.objects.filter(user_id=user.id, dataroom_id__in=member).order_by('-created_date')
        # count= count+int(updatedata.count())
        page = paginator.paginate_queryset(dataroom_notification_list, request)
        # page1 = paginator.paginate_queryset(updatedata, request)
        data = newAllNotificationsSerializer(page, many=True).data
        data = sorted(data,key=lambda x : x['created_date'])

        # data1 = BulkuploadstatusSerializer(updatedata, many=True).data
        # print("-----------------------",data[1]['dataroom']['id'])
        # i=0
        # for da in data:
        #   # print('values -----',da['dataroom']['id'])
        #   q = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=da['dataroom']['id']).last()
        #   # print(da['dataroom']['is_expired'] == False)
        #   if q.is_deleted == False and da['dataroom']['is_expired'] == False:
        #       da['permissions'] =True
        #   else:
        #       da['permissions'] = False

            
        # data.extend(data1)
        for i in data:
            dateobject=datetime.datetime.strptime(str(i['created_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            i['created_date'] = dateobject.strftime('%Y-%m-%d %H:%M:%S.%f')
            i['dataroom']['dataroom_name'] = i['dataroom']['dataroom_name'].replace('_'," ").replace('_'," ").replace('_'," ")
            i['dataroom']['dataroom_nameFront'] = i['dataroom']['dataroom_nameFront'].replace('_'," ").replace('_'," ").replace('_'," ")
            try:
                i['dataroom_folder']['dataroom']['dataroom_name'] = i['dataroom_folder']['dataroom']['dataroom_name'].replace('_'," ").replace('_'," ").replace('_'," ")

                i['dataroom_folder']['dataroom']['dataroom_nameFront'] = i['dataroom_folder']['dataroom']['dataroom_nameFront'].replace('_'," ").replace('_'," ").replace('_'," ")
            except:
                pass
        # print("******************************",data,')))))))))))))))))))))))')

        # data=paginator.paginate_queryset(data, request)
        # print("=============", dataroom_notification_list)
        # for each in dataroom_notification_list:
        #     if each.dataroom_member:
        #         d_m = DataroomMembers.objects.filter(id=int(each.dataroom_member)).first()
        #         if d_m:
        #             # if user.id != d_m.member.id and user.id != d_m.member_added_by_id and user.date_joined < d_m.date_updated:
        #             # if user.id != d_m.member_added_by_id.id:
        #             serializers = DataroomMembersSerializer(d_m)
        #             data.append(serializers.data)

        #     if each.dataroom_groups:
        #         d_g = DataroomGroups.objects.filter(id=int(each.dataroom_groups)).first()
        #         if d_g:
        #             # if user.id != d_g.group_created_by.id:
        #             serializers = DataroomGroupsSerializer(d_g)
        #             data.append(serializers.data)

        #     if each.dataroom_folder:
        #         d_folder = DataroomFolder.objects.filter(id=int(each.dataroom_folder)).first()
        #         if d_folder:
        #             # if user.id != d_folder.user.id:
        #             serializers = DataroomFolderSerializer1(d_folder)
        #             data.append(serializers.data)

        #     if each.dataroom_updates:
        #         d_update = RcentUpdate.objects.filter(id=int(each.dataroom_updates)).first()
        #         if d_update:
        #             # if user.id != d_update.user.id:
        #             serializers = RcentUpdateSerializer(d_update)
        #             data.append(serializers.data)
        #     for da in data:
        #         da['created_date'] = str(each.created_date)
        # import datetime
        # userserializer =UserSerializer(user).data
        # datas = DataroomMembers.objects.filter(member_id=user.id)
        # dataserializer = DataroomMembersSerializer(datas,many=True).data
        return Response({'data':data,'size':count,'unread_count':unread_count}, status=status.HTTP_201_CREATED)












# himanshu work 
# class GetAllNotification(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )


#   def get(self, request, format=None):
#       # print("get method called")
#       user = request.user
#       type = request.GET.get("type")
#       # print("dataaaaaaaaaaaa", type)
#       data = []
#       count = 0
#       member = DataroomMembers.objects.filter(member_id=user.id).values('dataroom_id')
#       qna_permission_group = False
#       permission_member_group = DataroomMembers.objects.filter(member_id=user.id,dataroom_id__in=member,is_deleted=False).first()
#       try:
#           exclude_no_access_file = [i.folder_id for i in DataroomGroupFolderSpecificPermissions.objects.filter(dataroom_groups_id=permission_member_group.end_user_group.first().id,is_view_only=False,is_no_access=True)]
#           qna_permission = DataroomGroupPermission.objects.filter(dataroom_id=pk,dataroom_groups_id=permission_member_group.end_user_group.first().id,is_q_and_a=True)
#           if qna_permission is not None:
#               qna_permission_group = True
#       except Exception as e:
#           exclude_no_access_file = []
#       # print("exclude_no_access_file",exclude_no_access_file)
#       if type == "fixed":
#           if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
#               qna_permission_group = True
#               count = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).count()
#               dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).order_by('-created_date')
#           else:
#               qs_without_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).order_by('-created_date')
#               qs_with_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
#               if qna_permission_group:
#                   dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
#               else:
#                   dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
#               count = dataroom_notification_list.count()

#           # print("other list if",AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).values('dataroom_folder'))
#       else:
#           AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).update(read=True)
#           if permission_member_group.is_dataroom_admin or permission_member_group.is_la_user:
#               dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).order_by('-created_date')
#               # print("other list else",AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).values('dataroom_folder'))
#               count = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).count()
#           else:
#               qs_without_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member).exclude(dataroom_folder_id__in=exclude_no_access_file).exclude(Q(dataroom_folder_id=None) | Q(dataroom_folder__is_deleted=True)).order_by('-created_date')
#               qs_with_qna_perm = AllNotifications.objects.filter(user_id=user.id,dataroom_id__in=member,qna_id__isnull=qna_permission_group).exclude(dataroom_folder_id__in=exclude_no_access_file).order_by('-created_date')
#               if qna_permission_group:
#                   dataroom_notification_list = qs_without_qna_perm.union(qs_with_qna_perm)
#               else:
#                   dataroom_notification_list = qs_without_qna_perm.difference(qs_with_qna_perm)
#               count = dataroom_notification_list.count()

#       # updatedata=Bulkuploadstatus.objects.filter(user_id=user.id, dataroom_id__in=member).order_by('-created_date')
#       # count= count+int(updatedata.count())
#       # page = paginator.paginate_queryset(dataroom_notification_list, request)
#       # page1 = paginator.paginate_queryset(updatedata, request)
#       data = newAllNotificationsSerializer(dataroom_notification_list, many=True).data
#       data = sorted(data,key=lambda x : x['created_date'])

#       # data1 = BulkuploadstatusSerializer(updatedata, many=True).data
#       # print("-----------------------",data[1]['dataroom']['id'])
#       # i=0
#       for da in data:
#           # print('values -----',da['dataroom']['id'])
#           q = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=da['dataroom']['id']).last()
#           # print(da['dataroom']['is_expired'] == False)
#           if q.is_deleted == False and da['dataroom']['is_expired'] == False:
#               da['permissions'] =True
#           else:
#               da['permissions'] = False

            
#       # data.extend(data1)
#       for i in data:
#           dateobject=datetime.datetime.strptime(str(i['created_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
#           i['created_date'] = dateobject.strftime('%d/%m/%Y %H:%M:%S')
#       # print("******************************",data,')))))))))))))))))))))))')

#       # data=paginator.paginate_queryset(data, request)
#       # print("=============", dataroom_notification_list)
#       # for each in dataroom_notification_list:
#       #     if each.dataroom_member:
#       #         d_m = DataroomMembers.objects.filter(id=int(each.dataroom_member)).first()
#       #         if d_m:
#       #             # if user.id != d_m.member.id and user.id != d_m.member_added_by_id and user.date_joined < d_m.date_updated:
#       #             # if user.id != d_m.member_added_by_id.id:
#       #             serializers = DataroomMembersSerializer(d_m)
#       #             data.append(serializers.data)

#       #     if each.dataroom_groups:
#       #         d_g = DataroomGroups.objects.filter(id=int(each.dataroom_groups)).first()
#       #         if d_g:
#       #             # if user.id != d_g.group_created_by.id:
#       #             serializers = DataroomGroupsSerializer(d_g)
#       #             data.append(serializers.data)

#       #     if each.dataroom_folder:
#       #         d_folder = DataroomFolder.objects.filter(id=int(each.dataroom_folder)).first()
#       #         if d_folder:
#       #             # if user.id != d_folder.user.id:
#       #             serializers = DataroomFolderSerializer1(d_folder)
#       #             data.append(serializers.data)

#       #     if each.dataroom_updates:
#       #         d_update = RcentUpdate.objects.filter(id=int(each.dataroom_updates)).first()
#       #         if d_update:
#       #             # if user.id != d_update.user.id:
#       #             serializers = RcentUpdateSerializer(d_update)
#       #             data.append(serializers.data)
#       #     for da in data:
#       #         da['created_date'] = str(each.created_date)
#       # import datetime
#       # userserializer =UserSerializer(user).data
#       # datas = DataroomMembers.objects.filter(member_id=user.id)
#       # dataserializer = DataroomMembersSerializer(datas,many=True).data
#       print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',data,')))))))))))))))))))))))))))))))))))))))))')
#       return Response({'data':data,'size':count}, status=status.HTTP_201_CREATED)


# class GetAllNotification(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )


#   def get(self, request, format=None):
#       print("get method called")
#       user = request.user
#       type = request.GET.get("type")
#       print("dataaaaaaaaaaaa", type)
#       data = []
#       count = 0
#       member = DataroomMembers.objects.filter(member_id=user.id).values('dataroom_id')
#       print("member", member, user.id)
#       memberr2 = DataroomMembers.objects.filter(member_id=user.id,dataroom_id__in=member).last()

#       if type == "fixed":
#           count = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).count()

#           dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).order_by('-created_date')
#       else:
#           AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).update(read=True)

#           dataroom_notification_list = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).order_by('-created_date')

#           count = AllNotifications.objects.filter(user_id=user.id, dataroom_id__in=member).count()
#       data = AllNotificationsSerializer(dataroom_notification_list, many=True).data
#       for da in data:
#           print('values -----',da['dataroom']['id'])
#           q = DataroomMembers.objects.filter(member_id=user.id,dataroom_id=da['dataroom']['id']).last()
#           print(da['dataroom']['is_expired'] == False)
#           if q.is_deleted == False and da['dataroom']['is_expired'] == False:
#               da['permissions'] =True
#           else:
#               da['permissions'] = False

#       # if Bulkuploadstatus.objects.filter(dataroom_id__in=member,notifymember=True,isuploadfail=False).exists():
#       #   updatedata1=Bulkuploadstatus.objects.filter(dataroom_id__in=member,notifymember=True,isuploadfail=False).order_by('-created_date')
#       #   for i in updatedata1:
#       #           if memberr2.is_la_user == True or memberr2.is_dataroom_admin == True or i.is_root_folder==True:
#       #               updatedata=Bulkuploadstatus.objects.filter(id=i.id)
#       #               count= count+int(updatedata.count())
#       #               data1 = BulkuploadstatusSerializer(updatedata).data
#       #               data.extend(data1)

#       #           else:
#       #               if memberr2.end_user_group.first():
#       #                       if DataroomGroupFolderSpecificPermissions.objects.filter(folder_id=i.parentfolder,dataroom_id__in=member, dataroom_groups_id=memberr2.end_user_group.first().id).exists():
#       #                           perm_obj = DataroomGroupFolderSpecificPermissions.objects.get(folder_id=i.parentfolder,dataroom_id__in=member, dataroom_groups_id=memberr2.end_user_group.first().id)
#       #                           if perm_obj.is_no_access==False: 
#       #                               updatedata=Bulkuploadstatus.objects.filter(id=i.id)
#       #                               count= count+int(updatedata.count())
#       #                               data1 = BulkuploadstatusSerializer(updatedata).data
#       #                               data.extend(data1)






#       page = paginator.paginate_queryset(dataroom_notification_list, request)
#       # page1 = paginator.paginate_queryset(updatedata, request)

#       # print("-----------------------",data[1]['dataroom']['id'])
#       # i=0


            
#       data = sorted(data,key=lambda x : x['created_date'])
#       t=1
#       for i in data:
#           print(t,count,i['created_date'],'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
#           t+=1
#       # print("******************************",data,')))))))))))))))))))))))')

#       # data=paginator.paginate_queryset(data, request)
#       # print("=============", dataroom_notification_list)
#       # for each in dataroom_notification_list:
#       #     if each.dataroom_member:
#       #         d_m = DataroomMembers.objects.filter(id=int(each.dataroom_member)).first()
#       #         if d_m:
#       #             # if user.id != d_m.member.id and user.id != d_m.member_added_by_id and user.date_joined < d_m.date_updated:
#       #             # if user.id != d_m.member_added_by_id.id:
#       #             serializers = DataroomMembersSerializer(d_m)
#       #             data.append(serializers.data)

#       #     if each.dataroom_groups:
#       #         d_g = DataroomGroups.objects.filter(id=int(each.dataroom_groups)).first()
#       #         if d_g:
#       #             # if user.id != d_g.group_created_by.id:
#       #             serializers = DataroomGroupsSerializer(d_g)
#       #             data.append(serializers.data)

#       #     if each.dataroom_folder:
#       #         d_folder = DataroomFolder.objects.filter(id=int(each.dataroom_folder)).first()
#       #         if d_folder:
#       #             # if user.id != d_folder.user.id:
#       #             serializers = DataroomFolderSerializer1(d_folder)
#       #             data.append(serializers.data)

#       #     if each.dataroom_updates:
#       #         d_update = RcentUpdate.objects.filter(id=int(each.dataroom_updates)).first()
#       #         if d_update:
#       #             # if user.id != d_update.user.id:
#       #             serializers = RcentUpdateSerializer(d_update)
#       #             data.append(serializers.data)
#       #     for da in data:
#       #         da['created_date'] = str(each.created_date)
#       # import datetime
#       # userserializer =UserSerializer(user).data
#       # datas = DataroomMembers.objects.filter(member_id=user.id)
#       # dataserializer = DataroomMembersSerializer(datas,many=True).data
#       # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',data,')))))))))))))))))))))))))))))))))))))))))')
#       return Response({'data':data,'size':count}, status=status.HTTP_201_CREATED)


