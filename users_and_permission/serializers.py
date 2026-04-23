from rest_framework import serializers
from django.contrib.auth.models import Group 
from django.utils.crypto import get_random_string
from django.utils import timezone 
import datetime
from .models import DataroomMembers, DataroomGroups, DataroomGroupPermission, \
                    DataroomMemberInvitation, DataroomGroupFolderSpecificPermissions, RcentUpdate
from dataroom.models import Dataroom
from userauth.models import User
from userauth.serializers import UserSerializer
from data_documents.models import DataroomFolder 

class DataroomMembersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DataroomMembers
        depth = 1
        fields = (
            'id',
            'dataroom',
            'member',
            'member_type',
            'member_added_by',
            'is_primary_user',
            'is_q_a_user',
            'is_dataroom_admin', 
            'is_end_user', 
            'date_joined',
            'date_updated',
            'is_la_user',
            'is_end_user',
            'is_q_a_submitter_user',
            'disclaimer_status',
            'memberactivestatus'
        )

    def to_representation(self, instance):
        representation = super(DataroomMembersSerializer, self).to_representation(instance)
        representation['date_joined'] = instance.date_joined.strftime('%Y-%m-%d %H:%M:%S.%f')
        return representation

    def create(self, validated_data):
        # CONTEXT_OBJ = self.context.get('member_data')
        # print("start serializer debugger:-", **validated_data)
        # CONTEXT_OBJ['dataroom'] = Dataroom.objects.get(id=CONTEXT_OBJ.get('dataroom'))
        # return DataroomMembers.objects.create(**CONTEXT_OBJ)
        return DataroomMembers(**validated_data)

    def update(self, instance, validated_data):
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.member = validated_data.get('member', instance.member)
        instance.member_type = validated_data.get('member_type', instance.member_type)
        instance.member_added_by = validated_data.get('member_added_by', instance.member_added_by)
        instance.is_dataroom_admin = validated_data.get('is_dataroom_admin', instance.is_dataroom_admin)
        instance.is_end_user = validated_data.get('is_end_user', instance.is_end_user)
        instance.date_joined = validated_data.get('date_joined', instance.date_joined)
        instance.date_updated = validated_data.get('date_updated', instance.date_updated)        
        instance.save()
        return instance

class DataroomGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataroomGroups
        depth = 1 
        fields = (
            'id',
            'group_name',
            'dataroom',
            'group_created',
            'group_updated', 
            'group_created_by',
            'limited_access',
            'end_user',
            'is_deleted',
            'is_active',
            'access_revoke'
            # 'is_watermarking'
        )

    def create(self, validated_data):
        validated_data["dataroom"] = Dataroom.objects.get(id=self.context['dataroom'])
        validated_data["group_created_by"] = User.objects.get(id=self.context['group_created_by'])
        return DataroomGroups.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.group_name = validated_data.get('group_name', instance.group_name)
        instance.group_created = validated_data.get('group_created', instance.group_created)
        instance.group_updated = validated_data.get('group_updated', instance.group_updated)
        instance.group_created_by = validated_data.get('group_created_by', instance.group_created_by)
        instance.limited_access = validated_data.get('limited_access', instance.limited_access)
        instance.end_user = validated_data.get('end_user', instance.end_user)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.access_revoke = validated_data.get('access_revoke', instance.access_revoke)

        instance.save()
        return instance

class DataroomGroupPermissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DataroomGroupPermission
        depth = 1
        fields = ('id','is_edit_index', 'dataroom', 
                'dataroom_groups', 'is_watermarking', 'is_drm', 
                'is_overview', 'is_q_and_a', 
                'is_users_and_permission', 'is_updates', 'is_reports',
                'is_doc_as_pdf', 'is_excel_as_pdf','is_voting','viewer_limit_count','upload_ristrict_with_timer','is_irm_protected'
                )
    
    def create(self, validated_data):
        d_r_p = DataroomGroupPermission.objects.create(**validated_data)
        if d_r_p:
            d_r_p.dataroom_id = self.context['dataroom']
            d_r_p.dataroom_groups_id = self.context['dataroom_groups']
            d_r_p.save()
            return d_r_p
            
    def update(self, instance, validated_data):
        instance.is_edit_index = validated_data.get('is_edit_index', instance.is_edit_index)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.dataroom_groups = validated_data.get('dataroom_groups', instance.dataroom_groups)
        instance.is_watermarking = validated_data.get('is_watermarking', instance.is_watermarking)
        instance.is_drm = validated_data.get('is_drm', instance.is_drm)
        instance.is_overview = validated_data.get('is_overview', instance.is_overview)
        instance.is_q_and_a = validated_data.get('is_q_and_a', instance.is_q_and_a)
        instance.is_users_and_permission = validated_data.get('is_users_and_permission', instance.is_users_and_permission)
        instance.is_updates = validated_data.get('is_updates', instance.is_updates)
        instance.is_voting = validated_data.get('is_voting', instance.is_voting)
        instance.is_reports = validated_data.get('is_reports', instance.is_reports)
        instance.is_doc_as_pdf = validated_data.get('is_doc_as_pdf', instance.is_doc_as_pdf)
        instance.is_excel_as_pdf = validated_data.get('is_excel_as_pdf', instance.is_excel_as_pdf)
        instance.viewer_limit_count = validated_data.get('viewer_limit_count', instance.viewer_limit_count)
        instance.upload_ristrict_with_timer = validated_data.get('upload_ristrict_with_timer', instance.upload_ristrict_with_timer)
        instance.save()
        return instance

class DataroomMemberInvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataroomMemberInvitation
        depth = 1
        fields = ('dataroom_member', 'invitation_sent', 'invitation_expiry', 'invitation_status')


    def create(self, validated_data):
        return DataroomMemberInvitation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.dataroom_member = validated_data.get('dataroom_member', instance.dataroom_member)
        instance.invitation_sent = validated_data.get('invitation_sent', instance.invitation_sent)
        instance.invitation_expiry = validated_data.get('invitation_expiry', instance.invitation_expiry)
        instance.invitation_status = validated_data.get('invitation_status', instance.invitation_status)  
        instance.save()
        return instance 


class DataroomGroupFolderSpecificPermissionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataroomGroupFolderSpecificPermissions
        depth = 1
        fields = ('is_no_access', 'is_view_only', 'is_view_and_print', 'is_view_and_print_and_download', \
                'is_upload', 'is_watermarking', 'is_drm', 'is_editor', 'folder', 'dataroom', 'dataroom_groups', \
                'permission_given_by', 'is_access','is_shortcut','access_revoke'
                )

    def create(self, validated_data):
        validated_data["folder"] = DataroomFolder.objects.get(id=self.context['folder'])
        validated_data["dataroom"] = Dataroom.objects.get(id=self.context['dataroom'])
        validated_data["dataroom_groups"] = DataroomGroups.objects.get(id=self.context['dataroom_groups'])
        validated_data["permission_given_by"] = self.context['permission_given_by']
        return DataroomGroupFolderSpecificPermissions.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.is_no_access = validated_data.get('is_no_access', instance.is_no_access)
        instance.is_view_only = validated_data.get('is_view_only', instance.is_view_only)
        instance.is_view_and_print = validated_data.get('is_view_and_print', instance.is_view_and_print)
        instance.is_view_and_print_and_download = validated_data.get('is_view_and_print_and_download', instance.is_view_and_print_and_download)
        instance.is_upload = validated_data.get('is_upload', instance.is_upload)
        instance.is_watermarking = validated_data.get('is_watermarking', instance.is_watermarking)
        instance.is_drm = validated_data.get('is_drm', instance.is_drm)
        instance.is_editor = validated_data.get('is_editor', instance.is_editor)
        instance.folder = validated_data.get('folder', instance.folder)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.dataroom_groups = validated_data.get('dataroom_groups', instance.dataroom_groups)
        instance.permission_given_by = validated_data.get('permission_given_by', instance.permission_given_by)
        instance.is_shortcut = validated_data.get('is_shortcut', instance.is_shortcut)
        instance.access_revoke = validated_data.get('access_revoke', instance.access_revoke)

        instance.save()
        return instance


class RcentUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = RcentUpdate
        fields = '__all__'        

class DataroomMembersSerializerone(serializers.ModelSerializer):
    member=UserSerializer(many=False)
    class Meta:
        model = DataroomMembers
        fields = (
            'id',
            'dataroom',
            'member',
            'is_primary_user',
            'is_q_a_user',
            'is_dataroom_admin', 
            'is_end_user', 
            'is_la_user',
            'is_end_user',
            'is_q_a_submitter_user',
            'memberactivestatus'
        )
