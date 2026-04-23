from django.shortcuts import render
from rest_framework.views import APIView
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from .models import Message, AllNotifications
from .serializers import MessageSerializer, AllNotificationsSerializer
import operator
from django.db.models import Max, F, Min, Q, Sum
from datetime import datetime, timedelta
from users_and_permission.models import DataroomMembers
from dataroom.models import Dataroom
from userauth.models import TokenAuthentication,Token
try:
    from functools import reduce
except ImportError:  # Python < 3
    pass

from . import utils
# from users_and_permission import DataroomMembers

class SendMessage(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("send message get method")
        user = request.user
        # print("User", user.id)
        unreaddataa = []
        # q_list = []
        # query = reduce(operator.or_, q_list)
        # print("query", query)
        all_dataroom_qs = [i.id for i in Dataroom.objects.filter()]
        dataroom_member_qs = [i.dataroom_id for i in DataroomMembers.objects.filter(member_id=user.id,dataroom_id__in=all_dataroom_qs)]
        all_member_qs = [i.member_id for i in DataroomMembers.objects.filter(dataroom_id__in=dataroom_member_qs)]
        # message_list = Message.objects.filter(main=True).filter(Q(user_rec_id=user.id) | Q(user_send_id=user.id)).order_by('-latestmessage_at')
        message_list = Message.objects.filter(main=True).filter(Q(user_rec_id__in=all_member_qs) | Q(user_send_id__in=all_member_qs)).filter(Q(user_rec_id=user.id) | Q(user_send_id=user.id)).order_by('-latestmessage_at')
        message_list_serializer = MessageSerializer(message_list, many=True)
        for i in message_list_serializer.data:
            if Message.objects.filter(main=False,msg_id=int(i['id']),read=False,user_rec_id=user.id).count()>0:
                i['newmessagecount']=Message.objects.filter(main=False,msg_id=int(i['id']),read=False,user_rec_id=user.id).count()
            else:
                i['newmessagecount']=Message.objects.filter(msg_id=int(i['id']),read=False,user_rec_id=user.id).count()

        # Message.objects.filter().update(read=True)
        return Response(message_list_serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk, format=None):
        # try:
            user = request.user
            data = request.data
            print("send message post method test1", data)
            msg = Message()
            msg.user_rec_id = pk
            msg.user_send_id = user.id
            msg.send_message = data['update']['message']
            msg.subject = data['update']['subject']
            msg.msg_id = data['update']['msg']
            msg.latestsender_id=user.id
            msg.latestmessage_at=datetime.now()

            # msg.read=True
            msg.save()
            # print(data['update']['msg'],'oooooooooooooooooooooooppppppppppppppppp')
            msgdata=Message.objects.get(id=data['update']['msg'])
            msgdata.latestsender_id=user.id
            msgdata.read=False
            msgdata.latestmessage_at=datetime.now()
            msgdata.save()
            # msgdata1=Message.objects.get(id=data['update']['msg'])


            # print(msgdata.read,'uuuuuuuuuuuuuuuuuuuyyyyyyyyyyyyyyyttttttttttttttttttt')
            utils.send_replied_message(msg)
            return Response({'data': 'Send message successfully!'}, status=status.HTTP_201_CREATED)
        # # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)


class GetDataroomMessage(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        # print("dataroom messages")
        user = request.user
        # print("======================================user id ==============================") 
        # print(user.id)
        # print("======================================dataroom id ==============================") 
        # print(pk)
        
        message_list = Message.objects.filter(user_rec_id=user.id, dataroom_id=pk)
        message_list_serializer = MessageSerializer(message_list, many=True)
        # print ("message serializer data", message_list_serializer.data)
        return Response(message_list_serializer.data, status=status.HTTP_201_CREATED)


class ChatMessageList(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        chat = []
        serializer = []
        # print("chat message list")
        user = request.user
        Message.objects.filter(msg_id=int(pk),main=True).filter(~Q(latestsender_id=user.id)).update(read=True)
        Message.objects.filter(msg_id=int(pk)).filter(main=False,user_rec_id=user.id).update(read=True)

        message_list = Message.objects.filter(msg_id=int(pk)).filter(Q(user_rec_id=user.id) | Q(user_send_id=user.id))
        
        ordered = sorted(message_list, key=operator.attrgetter('id'))
        message_list_serializer = MessageSerializer(ordered, many=True)
        datas=message_list_serializer.data
        # for da in datas:
        #     # da['received_at'] = str(da['received_at']).replace('T',' ',1)
        #     # print(da['received_at'])
        #     dateobject=datetime.strptime(str(da.get('received_at')).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
        #     da['received_at']=dateobject.strftime("%Y-%d-%m %H:%M:%S")

        # print ("message serializer data", datas)
        return Response(datas, status=status.HTTP_201_CREATED)

# class GetDataroomNotification(APIView):
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def get(self, request, pk, format=None):
#         print("get method called")
#         user = request.user
#         data = []
#         dataroom_notification_list = AllNotifications.objects.filter(dataroom_id=pk)
#         for each in dataroom_notification_list:
#             d_m = DataroomMembers.objects.all()
#             data.append(each)
#         return Response(data, status=status.HTTP_201_CREATED)


# class SendMessageToUser(APIView):
#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )

#     def post(self, request, format=None):
#         data = request.data
#         print("dataaaaa", data)
#         try:
#             user = request.user
#             data = request.data
#             msg = Message.objects.create(user_rec_id=int(data.get('user').get('id')), user_send_id=user.id, send_message=data.get('message'), subject=data.get('subject'))
#             msg.msg_id = msg.id
#             msg.save()
#             utils.send_personal_message(msg)
#             return Response({'data': 'Send message successfully to '+data.get('email')}, status=status.HTTP_201_CREATED)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


class SendMessageToUser(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        data = request.data
        # print("sent notification to user ", data)
        try:
            user = request.user
            data = request.data
            if int(data.get('user').get('id'))!=int(user.id):
                msg = Message.objects.create(user_rec_id=int(data.get('user').get('id')),latestsender_id=user.id, user_send_id=user.id, send_message=data.get('message'), subject=data.get('subject'))
                msg.msg_id = msg.id
                msg.save()
                utils.send_personal_message(msg)
                to = data.get('user').get('first_name') if data.get('user').get('first_name')!=None else data.get('email')
                return Response({'data': ' Message sent to '+str(to)+' successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'data': 'Please Check Emails.You trying to send Message to yourself!!'},status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)