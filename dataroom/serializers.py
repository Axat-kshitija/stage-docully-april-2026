from rest_framework import serializers
from dms.settings import sas_url
from django.contrib.auth.models import User, Group 
from django.utils.crypto import get_random_string
from .models import Dataroom, DataroomStage, \
                    DataroomModules, DataroomOverview, Contacts, \
                    DataroomDisclaimer, ContactGroup, ContactGroupMembers, \
                    DataroomRoles, Watermarking, DataroomView,dataroomProLiteFeatures

                     #DataroomOverviewHeading,\
                    #CustomLink


from django.utils import timezone 
import datetime
from userauth.models import User
from userauth.serializers import UserSerializer



def get_primary_key_related_model(model_class, **kwargs):
    """
    Nested serializers are a mess. https://stackoverflow.com/a/28016439/2689986
    This lets us accept ids when saving / updating instead of nested objects.
    Representation would be into an object (depending on model_class).
    """
    class PrimaryKeyNestedMixin(model_class):

        def to_internal_value(self, data):
            try:
                return model_class.Meta.model.z.get(pk=data)
            except model_class.Meta.model.DoesNotExist:
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)

        def to_representation(self, data):
            return model_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)


class DataroomStageSerializer(serializers.ModelSerializer):
    class Meta:
        Model = DataroomStage
        fields = ('dataroom_stage')


    # def validate(self, data):
       #  """
       #  Check that the start is before the stop.
       #  """
    #   if data['start'] > data['finish']:
    #       raise serializers.ValidationError("finish must occur after start")
    #   return data

    def create(self, validated_data):
        return DataroomStage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.dataroom_stage = validated_data.get('dataroom_stage', instance.dataroom_stage)
        instance.save()
        return instance     



class DataroomModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataroomModules
        fields = (
            'id',
            'is_watermarking',
            'is_drm',
            'is_question_and_answers',
            'is_collabration', 
            'is_ocr', 
            'is_editor'

        )

    def create(self, validated_data):
        """
        Create and return a new `DataroomModules` instance, given the validated data.
        """
        # print ("data under cretae ", validated_data)
        #data = validated_data.get("account_modules")
        dataroom_modules = DataroomModules.objects.create(**validated_data)
        
        return dataroom_modules

    def update(self, instance, validated_data):
        """
        Update and return an existing `DataroomModules` instance, given the validated data.
        """
        instance.is_watermarking = validated_data.get('is_watermarking', instance.is_watermarking)
        instance.is_drm = validated_data.get('is_drm', instance.is_drm)
        instance.is_question_and_answers = validated_data.get('is_question_and_answers', instance.is_question_and_answers)
        instance.is_collabration = validated_data.get('is_collabration', instance.is_collabration)
        instance.is_ocr = validated_data.get('is_ocr', instance.is_ocr)        
        instance.is_editor = validated_data.get('is_editor', instance.is_editor)        

        instance.save()
        return instance

class DataroomSerializer(serializers.ModelSerializer):
    dataroom_modules = DataroomModulesSerializer(many=False)
    dataroom_logo = serializers.SerializerMethodField('dataroom_logo_url')

    class Meta:
        model = Dataroom
        fields = (
            'id',
            'dataroom_name',
            'dataroom_logo',
            'account_level_branding',
            'created_date', 
            'updated_date', 
            'dataroom_modules', 
            'is_dataroom_on_live', 
            'is_dataroom_cloned',
            'is_request_for_archive',
            'is_request_for_deletion', 
            'dataroom_storage_allocated',
            'user', 
            'my_team',
            'trial_days',
            'trial_expired',
            'trial_expiry_date',
            'is_paid',
            'dataroom_id',
            'is_expired',
            'dataroom_nameFront',
            'event',
            'event_timestamp',
            'dataroom_cloned_from',
            'notify',
            'addon_payment_overdue',
            'plan_payment_overdue',
            'is_deleted',
            'delete_at',
            'storage_exceed_block',
            'delete_request_at',
            'offlinedataroom',
            'deleterequestactivityby',
            'archiveequestactivityby',
            'dataroom_users_permitted',
            'is_usa_blob',
            'dataroom_version'
        )


    def dataroom_logo_url(self, obj):
        if obj.dataroom_logo:
            return str(obj.dataroom_logo.url) + str(sas_url)
        else:
            return None

    # def to_representation(self, instance):
    #     representation = super(DataroomSerializer, self).to_representation(instance)
    #     representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
    #     representation['updated_date'] = instance.updated_date.strftime('%d/%m/%Y %H:%M:%S')
    #     return representation

    def create(self, validated_data):
        """
        Create and return a new `Dataroom` instance, given the validated data.
        """
        dataroom_serializer = DataroomModulesSerializer(data=self.context["dataroom_modules"])
        
        if dataroom_serializer.is_valid():
            dataroom_serializer.save()
            validated_data["dataroom_modules"] = DataroomModules.objects.get(id=dataroom_serializer.data.get("id"))
            dataroom = Dataroom.objects.create(**validated_data)
            return dataroom


  

    def update(self, instance, validated_data):
     
        dataroom_modules_validated_data = validated_data.get("dataroom_modules")
        dataroom_modules = DataroomModules.objects.get(id = instance.dataroom_modules.id)
        dataroom_modules_serializer = DataroomModulesSerializer(dataroom_modules, data=dataroom_modules_validated_data)
        
        if dataroom_modules_serializer.is_valid():
            dataroom_modules_serializer.save()
        instance.user = validated_data.get('user', instance.user)
        instance.dataroom_name = validated_data.get('dataroom_name', instance.dataroom_name)
        instance.dataroom_id = validated_data.get('dataroom_id', instance.dataroom_id)
        #instance.dataroom_logo = validated_data.get('dataroom_logo', instance.dataroom_logo)
        instance.account_level_branding = validated_data.get('account_level_branding', instance.account_level_branding)
        instance.dataroom_modules = dataroom_modules#dataroom_modules_serializer.data#validated_data.get('dataroom_modules', instance.dataroom_modules)
        instance.updated_date = datetime.datetime.now()
        instance.is_dataroom_on_live = validated_data.get('is_dataroom_on_live', instance.is_dataroom_on_live)        
        instance.is_dataroom_cloned= validated_data.get('is_dataroom_cloned', instance.is_dataroom_cloned)
        instance.is_request_for_deletion = validated_data.get('is_request_for_deletion', instance.is_request_for_deletion)
        instance.is_request_for_archive= validated_data.get('is_request_for_archive', instance.is_request_for_archive)
        instance.my_team = validated_data.get('my_team', instance.my_team)
        instance.dataroom_storage_allocated = validated_data.get('dataroom_storage_allocated', instance.dataroom_storage_allocated)
        instance.is_expired = validated_data.get('is_expired', instance.is_expired)
        instance.is_usa_blob = validated_data.get('is_usa_blob', instance.is_usa_blob)
        instance.dataroom_version = validated_data.get('dataroom_version', instance.dataroom_version)
        instance.save()
        return instance

class DataroomSerializertwo(serializers.ModelSerializer):
    # dataroom_modules = DataroomModulesSerializer(many=False)

    dataroom_logo = serializers.SerializerMethodField('dataroom_logo_url')
    class Meta:
        model = Dataroom
        fields = (
            'id',
            'dataroom_name',
            'dataroom_logo',
            'account_level_branding',
            'created_date', 
            'updated_date', 
            'dataroom_modules', 
            'is_dataroom_on_live', 
            'is_dataroom_cloned',
            'is_request_for_archive',
            'is_request_for_deletion', 
            'dataroom_storage_allocated',
            'user', 
            'my_team',
            'trial_days',
            'trial_expired',
            'trial_expiry_date',
            'is_paid',
            'dataroom_id',
            'is_expired',
            'dataroom_nameFront',
            'event',
            'event_timestamp',
            'dataroom_cloned_from',
            'notify',
            'addon_payment_overdue',
            'plan_payment_overdue',
            'is_deleted',
            'delete_at',
            'offlinedataroom',
            'dataroom_users_permitted',
            'storage_exceed_block',
            'is_usa_blob',
            'dataroom_version'
        )


    # def to_representation(self, instance):
    #     representation = super(DataroomSerializer, self).to_representation(instance)
    #     representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
    #     representation['updated_date'] = instance.updated_date.strftime('%d/%m/%Y %H:%M:%S')
    #     return representation
    def dataroom_logo_url(self, obj):
        if obj.dataroom_logo:
            return str(obj.dataroom_logo.url) + str(sas_url)
        else:
            return None


    def create(self, validated_data):
        """
        Create and return a new `Dataroom` instance, given the validated data.
        """

        dataroom = Dataroom.objects.create(**validated_data)
        return dataroom


  

    def update(self, instance, validated_data):
     
        dataroom_modules_validated_data = validated_data.get("dataroom_modules")
        dataroom_modules = DataroomModules.objects.get(id = instance.dataroom_modules.id)
        dataroom_modules_serializer = DataroomModulesSerializer(dataroom_modules, data=dataroom_modules_validated_data)
        
        if dataroom_modules_serializer.is_valid():
            dataroom_modules_serializer.save()
        instance.user = validated_data.get('user', instance.user)
        instance.dataroom_name = validated_data.get('dataroom_name', instance.dataroom_name)
        instance.dataroom_nameFront = validated_data.get('dataroom_nameFront', instance.dataroom_nameFront)
        instance.dataroom_id = validated_data.get('dataroom_id', instance.dataroom_id)
        #instance.dataroom_logo = validated_data.get('dataroom_logo', instance.dataroom_logo)
        instance.account_level_branding = validated_data.get('account_level_branding', instance.account_level_branding)
        instance.dataroom_modules = dataroom_modules#dataroom_modules_serializer.data#validated_data.get('dataroom_modules', instance.dataroom_modules)
        instance.updated_date = datetime.datetime.now()
        instance.is_dataroom_on_live = validated_data.get('is_dataroom_on_live', instance.is_dataroom_on_live)        
        instance.is_dataroom_cloned= validated_data.get('is_dataroom_cloned', instance.is_dataroom_cloned)
        instance.is_request_for_deletion = validated_data.get('is_request_for_deletion', instance.is_request_for_deletion)
        instance.is_request_for_archive= validated_data.get('is_request_for_archive', instance.is_request_for_archive)
        instance.my_team = validated_data.get('my_team', instance.my_team)
        instance.dataroom_storage_allocated = validated_data.get('dataroom_storage_allocated', instance.dataroom_storage_allocated)
        instance.is_expired = validated_data.get('is_expired', instance.is_expired)
        instance.dataroom_users_permitted = validated_data.get('dataroom_users_permitted', instance.dataroom_users_permitted)
        instance.storage_exceed_block = validated_data.get('storage_exceed_block', instance.storage_exceed_block)
        instance.is_usa_blob = validated_data.get('is_usa_blob', instance.is_usa_blob)
        instance.dataroom_version = validated_data.get('dataroom_version', instance.dataroom_version)
        instance.save()
        return instance



class DataroomdashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataroom
        fields = (
            'id',
            'dataroom_name',
            'account_level_branding',
            'created_date', 
            'updated_date', 
            'dataroom_modules', 
            'is_dataroom_on_live', 
            'is_request_for_archive',
            'is_request_for_deletion', 
            'dataroom_storage_allocated',
            'user', 
            'trial_days',
            'trial_expired',
            'trial_expiry_date',
            'is_paid',
            'dataroom_id',
            'is_expired',
            'dataroom_nameFront',
            'event',
            'event_timestamp',
            'addon_payment_overdue',
            'plan_payment_overdue',
            'is_deleted',
            'storage_exceed_block',
            'is_usa_blob',
            'dataroom_version',
        )


class DataroomOverviewSerializer(serializers.ModelSerializer):
    """docstring for DataroomOverviewSerializer"""
    dataroom_overview_heading = serializers.JSONField()
    dataroom_custom_links = serializers.JSONField()
    change_video_ppt = serializers.SerializerMethodField('change_video_ppt_url')
    class Meta:
        model = DataroomOverview
        fields = ('id', 
                'user', 
                'send_daily_email_updates', 
                'choose_overview_default_page', 
                'hide_file_indexing', 
                'dataroom', 
                'dataroom_overview_heading', 
                'dataroom_custom_links', 
                'change_video_ppt',
                'show_multiple_times_disclaimer'
                )

    def change_video_ppt_url(self, obj):
        # return obj.change_video_ppt.url
        if obj.change_video_ppt:
            return obj.change_video_ppt.url
        else:
            return None

    def create(self, validated_data):
        """
        Create and return a new `DataroomModules` instance, given the validated data.
        """
        # print ("validated data is", validated_data)
        return DataroomOverview.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing `DataroomModules` instance, given the validated data.
        """
        instance.send_daily_email_updates = validated_data.get('send_daily_email_updates', instance.send_daily_email_updates)
        instance.choose_overview_default_page = validated_data.get('choose_overview_default_page', instance.choose_overview_default_page)
        instance.hide_file_indexing = validated_data.get('hide_file_indexing', instance.hide_file_indexing)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
    #   instance.change_video_ppt = validated_data.get('change_video_ppt', instance.change_video_ppt)        
        instance.user = validated_data.get('user', instance.user)        
        instance.dataroom_overview_heading = validated_data.get('dataroom_overview_heading', instance.dataroom_overview_heading)
        instance.dataroom_custom_links = validated_data.get('dataroom_custom_links', instance.dataroom_custom_links)
        instance.show_multiple_times_disclaimer = validated_data.get('show_multiple_times_disclaimer', instance.show_multiple_times_disclaimer)
        instance.save()
        return instance



class ContactSerializer(serializers.ModelSerializer):
    """docstring for DataroomOverviewSerializer"""
    class Meta:
        model = Contacts
        fields = ('id', 
                    'first_name', 
                    'last_name', 
                    'email', 
                    'user', 
                    'dataroom'
                )

    def create(self, validated_data):
        """
        Create and return a new `DataroomModules` instance, given the validated data.
        """
        # print ("validated data is", validated_data)
        return Contacts.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing `DataroomModules` instance, given the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.user = validated_data.get('user', instance.user)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.save()
        return instance


class DataroomDisclaimerSerializerupload(serializers.ModelSerializer):

    dataroom_disclaimer = serializers.SerializerMethodField('dataroom_disclaimer_url')

    class Meta:
        model = DataroomDisclaimer
        fields = (
            'id', 
            'user', 
            'dataroom', 
            'dataroom_disclaimer', 
            'is_dataroom_disclaimer_default', 
            'dataroom_disclaimer_preview_status', 
            'disclaimer_added_date', 
            'disclaimer_updated_date', 
            'dataroom_disclaimer_name',
            'file_size',
            'file_size_mb',

            )

    def dataroom_disclaimer_url(self, obj):
        # return obj.dataroom_disclaimer.url
        if obj.dataroom_disclaimer:
            return obj.dataroom_disclaimer.url
        else:
            return None

    def create(self, validated_data):
        # print ("validated data", validated_data)
        return DataroomDisclaimer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.is_dataroom_disclaimer_default = validated_data.get('is_dataroom_disclaimer_default', instance.is_dataroom_disclaimer_default)
        instance.dataroom_disclaimer_preview_status= validated_data.get('dataroom_disclaimer_preview_status', instance.dataroom_disclaimer_preview_status)
        instance.dataroom_disclaimer_name = validated_data.get('dataroom_disclaimer_name', instance.dataroom_disclaimer_name)
        instance.save()
        return instance






class DataroomDisclaimerSerializer(serializers.ModelSerializer):
    dataroom=DataroomSerializer(many=False)
    dataroom_disclaimer = serializers.SerializerMethodField('dataroom_disclaimer_url')
    class Meta:
        model = DataroomDisclaimer
        fields = (
            'id', 
            'user', 
            'dataroom', 
            'dataroom_disclaimer', 
            'is_dataroom_disclaimer_default', 
            'dataroom_disclaimer_preview_status', 
            'disclaimer_added_date', 
            'disclaimer_updated_date', 
            'dataroom_disclaimer_name',
            'file_size',
            'file_size_mb',

            )

    def dataroom_disclaimer_url(self, obj):
        if obj.dataroom_disclaimer:
            return obj.dataroom_disclaimer.url
        else:
            return None


    def create(self, validated_data):
        # print ("validated data", validated_data)
        return DataroomDisclaimer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.is_dataroom_disclaimer_default = validated_data.get('is_dataroom_disclaimer_default', instance.is_dataroom_disclaimer_default)
        instance.dataroom_disclaimer_preview_status= validated_data.get('dataroom_disclaimer_preview_status', instance.dataroom_disclaimer_preview_status)
        instance.dataroom_disclaimer_name = validated_data.get('dataroom_disclaimer_name', instance.dataroom_disclaimer_name)
        instance.save()
        return instance


class ContactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactGroup
        fields = (
            'id',
            'user',
            'group_name',
            'dataroom'
            )

    def create(self, validated_data):
        return ContactGroup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.group_name = validated_data.get('group_name', instance.group_name)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.save()
        return instance

class ContactGroupMembersSerializer(serializers.ModelSerializer):
    #contact = get_primary_key_related_model(ContactSerializer, many=False)
    #contact_group = get_primary_key_related_model(ContactGroupSerializer, many=False)
    class Meta:
        model = ContactGroupMembers
        fields = (
                'id', 
                'user', 
                'contact_group', 
                'contact'
                )

        def create(self, validated_data):
            # it will create new contact group member serializer
            return ContactGroupMembers.objects.create(**validated_data)

        def update(self, instance, validated_data):
            # instance contact group members update functionality
            instance.user = validated_data.get('user', instance.user)
            instance.contact_group = validated_data.get('contact_group', instance.contact_group)
            instance.contact = validated_data.get('contact', instance.contact)
            instance.save()
            return instance

class DataroomRolesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DataroomRoles 
        fields = ('id', 
                'user', 
                'dataroom', 
                'roles')

        def create(self, validated_data):
            return DataroomRoles.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.user = validated_data.get('user', instance.user)
            instance.dataroom = validated_data.get('dataroom', instance.dataroom)
            instance.roles = validated_data.get('roles', instance.roles)
            instance.save()
            return instance

class WatermarkingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Watermarking 
        fields = ('id', 'user', 'dataroom', 'font_size', 'opacity', 'rotation',
                'user_ipaddress', 'user_name', 'user_email','current_time', 'dataroom_name',
                'vtop', 'vcenter', 'vbottom', 'hleft', 'hmiddle', 'hright', 'custom_text',
                'type','name')

        def to_representation(self, instance):
            representation = super(WatermarkingSerializer, self).to_representation(instance)
            representation['current_time'] = instance.current_time.strftime('%d/%m/%Y %H:%M:%S')
            return representation

        def create(self, validated_data):
            return Watermarking.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.font_size = validated_data.get('font_size', instance.font_size)
            instance.opacity = validated_data.get('opacity', instance.opacity)
            instance.rotation = validated_data.get('rotation', instance.rotation)
            instance.user_ipaddress = validated_data.get('user_ipaddress', instance.user_ipaddress)
            instance.user_name = validated_data.get('user_name', instance.user_name)
            instance.user_email = validated_data.get('user_email', instance.user_email)
            instance.current_time = validated_data.get('current_time', instance.current_time)
            instance.dataroom_name = validated_data.get('dataroom_name', instance.dataroom_name)
            instance.vtop = validated_data.get('vtop', instance.vtop)
            instance.vcenter = validated_data.get('vcenter', instance.vcenter)
            instance.vbottom = validated_data.get('vbottom', instance.vbottom)
            instance.hleft = validated_data.get('hleft', instance.hleft)
            instance.hmiddle = validated_data.get('hmiddle', instance.hmiddle)
            if instance.dataroom.dataroom_version=="Lite":
                if dataroomProLiteFeatures.objects.filter(dataroom_id=instance.dataroom.id,custom_watermarking=True).exists():
                    instance.custom_text = validated_data.get('custom_text', instance.custom_text)
            else:
                instance.custom_text = validated_data.get('custom_text', instance.custom_text)
            instance.save()
            return instance

class DataroomViewSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many=False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = DataroomView
        fields = '__all__'

        def create(self, validated_data):
            return DataroomView.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super(DataroomViewSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        return representation

