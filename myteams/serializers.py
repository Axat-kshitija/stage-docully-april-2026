from rest_framework import serializers
from userauth.models import *
from django.utils.crypto import get_random_string
from .models import *
from userauth.serializers import *#serializers as get_primary_key_related_model


def get_primary_key_related_model(model_class, **kwargs):
    """
    Nested serializers are a mess. https://stackoverflow.com/a/28016439/2689986
    This lets us accept ids when saving / updating instead of nested objects.
    Representation would be into an object (depending on model_class).
    """
    class PrimaryKeyNestedMixin(model_class):

        def to_internal_value(self, data):
            # print("---------", model_class, "==========", data)
            try:
                return model_class.Meta.model.z.get(pk=data)
            except model_class.Meta.model.DoesNotExist:
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)

        def to_representation(self, data):
            return model_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)

class MychanelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mychanels
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `My Team` instance, given the validated data.
        """
        Mchanels = Mychanels.objects.create(**validated_data)

        return Mchanels

    def update(self, instance, validated_data):
        """
        Update and return an existing `My Team` instance, given the validated data.
        """
        instance.user = validated_data.get('user', instance.user)
        instance.chanel_by = validated_data.get('chanel_by', instance.chanel_by)
        instance.chanel_created_at = validated_data.get('chanel_created_at', instance.chanel_created_at)
        instance.chanel_updated_at = validated_data.get('chanel_updated_at', instance.chanel_updated_at)
        instance.chanel_name = validated_data.get('chanel_name', instance.chanel_name)
        instance.dataroom_allowed = validated_data.get('dataroom_allowed', instance.dataroom_allowed)
        instance.dataroom_admin_allowed = validated_data.get('dataroom_admin_allowed', instance.dataroom_admin_allowed)
        instance.dataroom_storage_allowed = validated_data.get('dataroom_storage_allowed', instance.dataroom_storage_allowed)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.usage_alertemail = validated_data.get('usage_alertemail', instance.usage_alertemail)
        instance.usage_alertemailtwo = validated_data.get('usage_alertemailtwo', instance.usage_alertemailtwo)
        instance.storage_exceed = validated_data.get('storage_exceed', instance.storage_exceed)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.is_deleted_request = validated_data.get('is_deleted_request', instance.is_deleted_request)
        instance.is_deleted_requestat = validated_data.get('is_deleted_requestat', instance.is_deleted_requestat)
        instance.is_deleted_deletedat = validated_data.get('is_deleted_deletedat', instance.is_deleted_deletedat)
        instance.save()
        return instance


class MyTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyTeams
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `My Team` instance, given the validated data.
        """
        validated_data['dataroom_admin_allowed']=int(validated_data['dataroom_admin_allowed'])
        myteam = MyTeams.objects.create(**validated_data)
        # print ("my team user id", myteam.user.id)
        # print ("my team id is", myteam.id)
        data = {
            'my_team_branding_done_by': myteam.user, 
            'my_team_branding' : myteam
        }
        my_team_branding = MyTeamBranding.objects.create(**data)
        # print ("my team branding id", my_team_branding.id)
        return myteam

    def update(self, instance, validated_data):
        """
        Update and return an existing `My Team` instance, given the validated data.
        """
        instance.team_name = validated_data.get('team_name', instance.team_name)
        instance.dataroom_allowed = validated_data.get('dataroom_allowed', instance.dataroom_allowed)
        instance.dataroom_admin_allowed = validated_data.get('dataroom_admin_allowed', instance.dataroom_admin_allowed)
        instance.user = validated_data.get('user', instance.user)
        instance.team_created_by = validated_data.get('team_created_by', instance.team_created_by)
        instance.dataroom_storage_allowed = validated_data.get('dataroom_storage_allowed', instance.dataroom_storage_allowed)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.onlinesubscriber = validated_data.get('onlinesubscriber', instance.onlinesubscriber)
        instance.usage_alertemail = validated_data.get('usage_alertemail', instance.usage_alertemail)
        instance.usage_alertemailtwo = validated_data.get('usage_alertemailtwo', instance.usage_alertemailtwo)
        instance.storage_exceed = validated_data.get('storage_exceed', instance.storage_exceed)
        instance.chanel = validated_data.get('chanel', instance.chanel)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.is_deleted_request = validated_data.get('is_deleted_request', instance.is_deleted_request)
        instance.is_deleted_requestat = validated_data.get('is_deleted_requestat', instance.is_deleted_requestat)
        instance.is_deleted_deletedat = validated_data.get('is_deleted_deletedat', instance.is_deleted_deletedat)
        instance.save()
        return instance

class MyTeamBrandingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MyTeamBranding
        fields = (
                'id',
                'my_team_branding_done_by', 
                'my_team_branding', 
                'border_top_color', 
                'background_color',
                'email_background_color', 
                'custom_login_border_color', 
                'branding_logo', 
                'email_header', 
                'favicon_icon'
            )


    def create(self, validated_data):
        return MyTeamBranding.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.my_team_branding_done_by = validated_data.get('my_team_branding_done_by', instance.my_team_branding_done_by)
        instance.my_team_branding = validated_data.get('my_team_branding', instance.my_team_branding)
        instance.border_top_color = validated_data.get('border_top_color', instance.border_top_color)
        instance.background_color = validated_data.get('background_color', instance.background_color)
        instance.email_background_color = validated_data.get('email_background_color', instance.email_background_color)
        instance.custom_login_border_color = validated_data.get('custom_login_border_color', instance.custom_login_border_color)
        instance.save()
        return instance


class TeamMembersSerializer(serializers.ModelSerializer):
    #member = get_primary_key_related_model(UserSerializer, many=False)
    #myteam = get_primary_key_related_model(MyTeamsSerializer, many = False)
    class Meta:
        model = TeamMembers
        fields = '__all__'

    def create(self, validated_data):
        return TeamMembers.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.member = validated_data.get('member', instance.member)
        instance.myteam = validated_data.get('myteam', instance.myteam)
        instance.member_added_by = validated_data.get('member_added_by', instance.member_added_by)
        instance.accesstodataroomusers = validated_data.get('accesstodataroomusers', instance.accesstodataroomusers)
        instance.allowtoaddnewmember = validated_data.get('allowtoaddnewmember', instance.allowtoaddnewmember)
        instance.allowtoaddnewdataroom = validated_data.get('allowtoaddnewdataroom', instance.allowtoaddnewdataroom)
        instance.save()
        return instance

class chanelMembersSerializer(serializers.ModelSerializer):
    #member = get_primary_key_related_model(UserSerializer, many=False)
    #myteam = get_primary_key_related_model(MyTeamsSerializer, many = False)
    class Meta:
        model = chanelMembers
        fields = '__all__'

    def create(self, validated_data):
        return chanelMembers.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.member = validated_data.get('member', instance.member)
        instance.chanel = validated_data.get('chanel', instance.chanel)
        instance.member_added_by = validated_data.get('member_added_by', instance.member_added_by)
        instance.accesstodataroomusers = validated_data.get('accesstodataroomusers', instance.accesstodataroomusers)
        instance.allowtoaddnewmember = validated_data.get('allowtoaddnewmember', instance.allowtoaddnewmember)
        instance.allowtoaddnewteam = validated_data.get('allowtoaddnewteam', instance.allowtoaddnewteam)
        instance.save()
        return instance