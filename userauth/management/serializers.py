from rest_framework import serializers
from django.contrib.auth.models import Group 
from django.utils.crypto import get_random_string
from . import constants
from .models import Profile, AccessHistory, User, InviteUser, EndUserType,pendinginvitations,planinvoiceuserwise,subscriptionplan
from django.utils import timezone 
import datetime

class EndUserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUserType
        fields = (
            'id', 
            'end_user_types', 
            'is_dataroom_admin', 
            'is_dataroom_la_admin', 
            'is_dataroom_enduser'
            )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'company_name',
            'country', 
            'is_superadmin',
            'is_admin', 
            'is_developer', 
            'is_staff', 
            'is_active', 
            'avatar',
            'is_end_user',
            'date_joined', 
            'agree',
            'is_team',
            'is_team_member',
            'is_icon_downloaded',
            'is_subscriber',
            'receive_email'
        )

    


    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        user = User.objects.create(**validated_data)
        print ("password is ", validated_data.get("password"))
        user.set_password(validated_data.get('password'))
        user.save()
        unique_id = get_random_string(length=400)
        link = constants.link+"/activate/"+unique_id
        profile = Profile()
        profile.user = user
        profile.activation_key = unique_id
        profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
        profile.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.phone = validated_data.get('phone', instance.phone)        
        instance.company_name = validated_data.get('company_name', instance.company_name)        
        instance.country = validated_data.get('country', instance.country)                
        instance.is_superadmin = validated_data.get('is_superadmin', instance.is_superadmin)
        instance.is_admin = validated_data.get('is_admin', instance.is_admin)
        instance.is_developer = validated_data.get('is_developer', instance.is_developer)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_end_user = validated_data.get('is_end_user', instance.is_end_user)
        instance.is_subscriber = validated_data.get('is_subscriber', instance.is_subscriber)
        instance.receive_email = validated_data.get('receive_email', instance.receive_email)
        #instance.end_user_type = validated_data.get('end_user_type', instance.end_user_type)
        instance.save()
        return instance

#InviteUser

class InviteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteUser
        fields = (
            'id',
            'invitiation_sender',
            'invitatation_sent_date',
            'invitatation_acceptance_date',
            'invitiation_receiver', 
            'invitation_status', 
            'is_invitation_accepted', 
            'is_invitation_expired', 
            'invitation_link', 
            'invitation_token', 
            'dataroom_invitation'

        )


    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        invite_user = InviteUser.objects.create(**validated_data)
    
        return invite_user

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.invitiation_sender = validated_data.get('invitiation_sender', instance.invitiation_sender)
        instance.invitatation_sent_date = validated_data.get('invitatation_sent_date', instance.invitatation_sent_date)
        instance.invitatation_acceptance_date = validated_data.get('invitatation_acceptance_date', instance.invitatation_acceptance_date)
        instance.invitiation_receiver = validated_data.get('invitiation_receiver', instance.invitiation_receiver)
        instance.invitation_status = validated_data.get('invitation_status', instance.invitation_status)        
        instance.is_invitation_accepted = validated_data.get('is_invitation_accepted', instance.is_invitation_accepted)
        instance.is_invitation_expired = validated_data.get('is_invitation_expired', instance.is_invitation_expired)
        instance.invitation_link = validated_data.get('invitation_link', instance.invitation_link)
        instance.invitation_token = validated_data.get('invitation_token', instance.invitation_token)
        instance.dataroom_invitation = validated_data.get('dataroom_invitation', instance.dataroom_invitation)
        instance.save()
        return instance



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

class AccessHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessHistory
        fields = (
            'id',
            'logged_in_ip',
            'logged_in_time',
            'logged_out_time',
            'user', 
            'is_logged_in'
        )

    def to_representation(self, instance):
        representation = super(AccessHistorySerializer, self).to_representation(instance)
        representation['logged_in_time'] = instance.logged_in_time.strftime('%d/%m/%Y %H:%M:%S')
        representation['logged_out_time'] = instance.logged_out_time.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        """
        Create and return a new `AccessHistory` instance, given the validated data.
        """
        access_history = AccessHistory.objects.create(**validated_data)
        return access_history

    
class pendinginvitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pendinginvitations
        fields = '__all__'

class subscriptionplanSerializer(serializers.ModelSerializer):
    class Meta:
        model = subscriptionplan
        fields = '__all__'

class planinvoiceuserwiseSerializer(serializers.ModelSerializer):
    user=UserSerializer(many=False)
    plan=subscriptionplanSerializer(many=False)
    class Meta:
        model = planinvoiceuserwise
        fields = '__all__'