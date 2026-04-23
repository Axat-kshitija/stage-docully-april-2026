from rest_framework import serializers
from .models import *
from userauth.serializers import UserSerializer,InviteUserSerializer,InviteUserSerializernotification
from users_and_permission.serializers import DataroomMembersSerializer, DataroomGroupsSerializer, RcentUpdateSerializer
from data_documents.serializers import DataroomFolderSerializer1,BulkuploadstatusSerializer
from dataroom.serializers import DataroomSerializer
from qna.serializers import QuestionAnswerSerializer
from dataroom.serializers import get_primary_key_related_model


class MessageSerializer(serializers.ModelSerializer):
    user_send = get_primary_key_related_model(UserSerializer)
    user_rec = get_primary_key_related_model(UserSerializer)
    class Meta:
        model = Message
        fields = "__all__"

from data_documents.serializers import BulkuploadstatusSerializer

class AllNotificationsSerializer(serializers.ModelSerializer):
	user_send = UserSerializer(read_only=True,)
	qna = get_primary_key_related_model(QuestionAnswerSerializer)
	dataroom_member = get_primary_key_related_model(DataroomMembersSerializer)
	dataroom_groups = get_primary_key_related_model(DataroomGroupsSerializer)
	dataroom_folder = get_primary_key_related_model(DataroomFolderSerializer1)
	dataroom_updates = get_primary_key_related_model(RcentUpdateSerializer)
	dataroom = get_primary_key_related_model(DataroomSerializer)
	bulkuploadd = get_primary_key_related_model(BulkuploadstatusSerializer)
	dataroom_member_invitation_accept = get_primary_key_related_model(InviteUserSerializernotification)

	class Meta:
		model = AllNotifications
		fields = "__all__"

	def to_representation(self, instance):
		representation = super(AllNotificationsSerializer, self).to_representation(instance)		
		representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
		return representation

class newAllNotificationsSerializer(serializers.ModelSerializer):
	# user_send = UserSerializer(read_only=True,)
	user = get_primary_key_related_model(UserSerializer)

	qna = get_primary_key_related_model(QuestionAnswerSerializer)
	dataroom_member = get_primary_key_related_model(DataroomMembersSerializer)
	dataroom_groups = get_primary_key_related_model(DataroomGroupsSerializer)
	dataroom_folder = get_primary_key_related_model(DataroomFolderSerializer1)
	dataroom_updates = get_primary_key_related_model(RcentUpdateSerializer)
	dataroom = get_primary_key_related_model(DataroomSerializer)
	bulkuploadd = get_primary_key_related_model(BulkuploadstatusSerializer)
	dataroom_member_invitation_accept = get_primary_key_related_model(InviteUserSerializernotification)

	class Meta:
		model = AllNotifications
		fields = "__all__"

	# def to_representation(self, instance):
	# 	representation = super(AllNotificationsSerializer, self).to_representation(instance)		
	# 	representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
	# 	return representation