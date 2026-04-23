from rest_framework import serializers
from django.contrib.auth.models import User, Group 
from django.utils.crypto import get_random_string
from .models import *
from userauth.serializers import UserSerializer
from django.utils import timezone 
import datetime
import os, errno
#from dms.aws.conf import MEDIA_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# import boto3  # Disabled - not needed for local development
import time
from django.core.files.storage import FileSystemStorage
from users_and_permission.models import RcentUpdate,DataroomMembers
from dataroom.serializers import DataroomSerializer
from notifications.models import AllNotifications

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
                return model_class.Meta.model.objects.get(pk=data)
            except model_class.Meta.model.DoesNotExist:
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)

        def to_representation(self, data):
            return model_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)

class DataroomFolderSerializer1(serializers.ModelSerializer):
    dataroom = DataroomSerializer(many=False)
    # deleted_by = get_primary_key_related_model(UserSerializer, many = False)
    path = serializers.SerializerMethodField('file_path')
    class Meta:
        model = DataroomFolder
        fields = ('id', 'user', 'dataroom', 'name', 
                'path', 'index', 'parent_path', 
                'is_root_folder', 'created_date',
                'last_updated_user', 'updated_date', 
                'is_infected', 'version', 'pages', 'parent_folder', 
                'file_size', 'file_content_type', 'is_folder', 
                'dataroom_folder_uuid', 'is_file_index', 'deleted_by', 'deleted_by_date', 'file_size_mb','is_compatable',
                )

    def file_path(self, obj):
        # return obj.change_video_ppt.url
        if obj.path:
            
            return obj.path.url
        else:
            return None



    def to_representation(self, instance):
        representation = super(DataroomFolderSerializer1, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        representation['updated_date'] = instance.updated_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

class DataroomFolderSerializer(serializers.ModelSerializer):
    # dataroom = DataroomSerializer(many=False)
    # deleted_by = get_primary_key_related_model(UserSerializer, many = False)
    number = serializers.SerializerMethodField()
    # created_date = serializers.DateField()

    # path = serializers.SerializerMethodField('file_path')
    class Meta:
        model = DataroomFolder
        fields = ('id', 'user', 'dataroom', 'name', 
                'path', 'index', 'parent_path', 
                'is_root_folder', 'created_date',
                'last_updated_user', 'updated_date', 
                'is_infected', 'version', 'pages', 'parent_folder', 
                'file_size', 'file_content_type', 'is_folder', 'number',
                'dataroom_folder_uuid', 'is_file_index', 'deleted_by', 'deleted_by_date', 'file_size_mb','is_deleted_permanent','uploadedin_batch','notifymember','is_compatable',
                )

    # def file_path(self, obj):
    #     # return obj.change_video_ppt.url
    #     if obj.path:

    #         return obj.path.url
    #     else:
    #         return None


    def file_path(self, obj):
        # return obj.change_video_ppt.url
        if obj.path:
            
            return obj.path.url
        else:
            return None

    def to_representation(self, instance):
        representation = super(DataroomFolderSerializer, self).to_representation(instance)
        # representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')

        # print(representation)
        return representation

    def get_number(self, obj):
        indexes = True
        # print(obj)
        if obj.is_folder == True:
            index = obj.index
        else:
            index = "0."+str(obj.index)
        parent_folder = obj.parent_folder_id
        while indexes == True:
            # print(parent_folder)
            if parent_folder == None:
                indexes = False
            else:
                folder = DataroomFolder.objects.get(id=parent_folder)
                index = str(folder.index)+'.'+str(index)
                parent_folder = folder.parent_folder_id
                # print(folder.name)
        # print("Index------", index)
        return index

    def create_folder_on_s3_storage(self, expected_path):
        #print ("media url is", MEDIA_URL)
        confiex_dataroom_url = 'confiex-dataroom-media/media/datarooms/'
        # s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # for bucket in s3.buckets.all():
        #   for key in bucket.objects.all():
        #       print ("key is", key)
        #   print ("bucket name", bucket.name)

    def create_new_root_folder(self, validated_data, dataroom_folder):
        #media_path_is = MEDIA_URL
        #media_path_is = media_path_is.replace("media/", "media")
        new_path = ""
        data = validated_data
        if dataroom_folder.is_folder:
            if dataroom_folder.is_root_folder:
                try:
                    dataroom_name = dataroom_folder.dataroom.dataroom_name
                    dataroom_uuid = dataroom_folder.dataroom.dataroom_uuid
                    folder_name = dataroom_folder.name
                    dataroom_folder_uuid = dataroom_folder.dataroom_folder_uuid
                    expected_path = '{0}'.format(dataroom_folder_uuid)
                    #self.create_folder_on_s3_storage(expected_path)
                    is_path_exist = os.path.exists(expected_path)
                    if not is_path_exist:
                        new_path = expected_path#os.mkdir(expected_path)
                        # print ("path is exist coming here Rushi2")

                        return True, new_path, expected_path
                    else: 
                        print ("path is exist coming here Rushi1")
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        print ("path is exist coming here Rushi3")

                        raise
            else:
                # print ("create new subfolder here ")
                try:
                    dataroom_name = dataroom_folder.dataroom.dataroom_name
                    dataroom_uuid = dataroom_folder.dataroom.dataroom_uuid
                    folder_name = dataroom_folder.name
                    dataroom_folder_uuid = dataroom_folder.dataroom_folder_uuid
                    expected_path = '{0}'.format(dataroom_folder_uuid)
                    # print ("expected path is", expected_path)
                    #self.create_folder_on_s3_storage(expected_path)
                    is_path_exist = os.path.exists(expected_path)
                    #print ("is path exist", is_path_exist)
                    if not is_path_exist:
                        new_path = expected_path
                        return True, new_path, expected_path
                    else:
                        print ("path is exist ")
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

        else:
            # parent_folder = dataroom_folder.parent_folder
            # print ("parent folder id is", parent_folder)
            # expected_path = '{0}_{1}/{2}'.format(dataroom_folder.dataroom.dataroom_name, parent_folder.dataroom.dataroom_uuid, dataroom_folder.name)
            # #self.create_folder_on_s3_storage(expected_path)
            # is_path_exist = os.path.exists(expected_path)
            # if not is_path_exist:
            new_path = dataroom_folder.path
            expected_path = dataroom_folder.path
            return True, new_path, expected_path
            # else: 
            #   print ("path is exist")
        
    def create(self, validated_data):
        
        dataroom_folder = DataroomFolder.objects.create(**validated_data) 
        is_folder_created, new_path, expected_path = self.create_new_root_folder(validated_data, dataroom_folder)
        dataroom_folder.path = expected_path
        dataroom_folder.save()
        return dataroom_folder

    def update(self, instance, validated_data):
        
        instance.user = validated_data.get('user', instance.user)
        instance.deleted_by = validated_data.get('deleted_by', instance.deleted_by)
        instance.name = validated_data.get('name', instance.name)
        instance.dataroom = validated_data.get('dataroom', instance.dataroom)
        instance.index = validated_data.get('index', instance.index)
        instance.path = validated_data.get('path', instance.path)
        # instance.parent_path = validated_data.get('user', instance.user)
        instance.is_root_folder = validated_data.get('is_root_folder', instance.is_root_folder)
        instance.last_updated_user = validated_data.get('last_updated_user', instance.last_updated_user)
        instance.file_content_type = validated_data.get('file_content_type', instance.file_content_type)
        instance.file_size = validated_data.get('file_size', instance.file_size)
        instance.parent_folder = validated_data.get('parent_folder', instance.parent_folder)
        instance.pages = validated_data.get('pages', instance.pages)
        instance.version = validated_data.get('version', instance.version)
        instance.is_infected = validated_data.get('is_infected', instance.is_infected)
        instance.is_folder = validated_data.get('is_folder', instance.is_folder)
        instance.dataroom_folder_uuid = validated_data.get('dataroom_folder_uuid', instance.dataroom_folder_uuid)
        instance.updated_date = validated_data.get('updated_date', instance.updated_date)
        print("----------created date", instance.updated_date)
        instance.save()
        dataroom_folder = DataroomFolder.objects.get(id=instance.id)
        is_folder_created, new_path, dataroom_folder.path = self.create_new_root_folder(validated_data, dataroom_folder)
        dataroom_folder.save()
        return instance





class DataroomFolderSerializerForTrash(serializers.ModelSerializer):
    # dataroom = DataroomSerializer(many=False)
    # deleted_by = get_primary_key_related_model(UserSerializer, many = False)
    number = serializers.SerializerMethodField()
    # created_date = serializers.DateField()

    # path = serializers.SerializerMethodField('file_path')
    class Meta:
        model = DataroomFolder
        fields = ('id', 'user', 'dataroom', 'name', 
                'path', 'index', 'parent_path', 
                'is_root_folder', 'created_date',
                'last_updated_user', 'updated_date', 
                'is_infected', 'pages', 'parent_folder', 
                'file_size', 'file_content_type', 'is_folder', 'number',
                'dataroom_folder_uuid', 'is_file_index', 'deleted_by', 'deleted_by_date', 'file_size_mb','is_deleted_permanent','uploadedin_batch','notifymember','is_compatable',
                )


    
    def to_representation(self, instance):
        representation = super(DataroomFolderSerializerForTrash, self).to_representation(instance)
        # representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')

        # print(representation)
        return representation

    def get_number(self, obj):
        indexes = True
        # print(obj)
        if obj.is_folder == True:
            index = obj.index
        else:
            index = "0."+str(obj.index)
        parent_folder = obj.parent_folder_id
        while indexes == True:
            # print(parent_folder)
            if parent_folder == None:
                indexes = False
            else:
                folder = DataroomFolder.objects.get(id=parent_folder)
                index = str(folder.index)+'.'+str(index)
                parent_folder = folder.parent_folder_id
                # print(folder.name)
        # print("Index------", index)
        return index


class  IndexDownloadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    
    class Meta:
        model = IndexDownload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'created_date')

    def to_representation(self, instance):
        representation = super(IndexDownloadSerializer, self).to_representation(instance)
        # representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return IndexDownload.objects.create(**validated_data)


class  FolderViewSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    class Meta:
        model = FolderView 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderViewSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderView.objects.create(**validated_data)





class  FolderActivityViewSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    class Meta:
        model = FolderView 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderActivityViewSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderView.objects.create(**validated_data)

class  FolderDrmDownloadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')

    
    class Meta:
        model = FolderDrmDownload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderDrmDownloadSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderDrmDownload.objects.create(**validated_data)



class  FolderDownloadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')

    
    class Meta:
        model = FolderDownload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderDownloadSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderDownload.objects.create(**validated_data)

class  BulkDataActivitySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()

    
    class Meta:
        model = FolderOrFileMove 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkDataActivitySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkDataActivitySerializer.objects.create(**validated_data)

class  BulkDataCopyActivitySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()

    
    class Meta:
        model = FolderOrFileCopy 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkDataCopyActivitySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkDataCopyActivitySerializer.objects.create(**validated_data)

class  BulkDataDrmActivitySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()

    
    class Meta:
        model = FolderOrFileCopy 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkDataDrmActivitySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkDataDrmActivitySerializer.objects.create(**validated_data)

class  RestoreFileActivitySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')

    
    class Meta:
        model = RestoreFiles 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(RestoreFileActivitySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return RestoreFileActivitySerializer.objects.create(**validated_data)



class  BulkDataDownloadActivitySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    # created_date = serializers.DateTimeField()

    
    class Meta:
        model = BulkDownloadFiles 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkDataDownloadActivitySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkDataDownloadActivitySerializer.objects.create(**validated_data)

class  FolderActivityDownloadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    
    class Meta:
        model = FolderDownload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderActivityDownloadSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderDownload.objects.create(**validated_data)


class  FolderPrintSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = FolderPrint 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderPrintSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderPrint.objects.create(**validated_data)

class  BulkActivityTrackerlistsSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    
    class Meta:
        model = BulkActivityTracker 
        fields = ('id', 
                'user', 
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkActivityTrackerlistsSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkActivityTracker.objects.create(**validated_data)



class  BulkDownloadFilesSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')

    class Meta:
        model = BulkDownloadFiles 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(BulkDownloadFilesSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return BulkDownloadFiles.objects.create(**validated_data)


class  FolderuploadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = Folderupload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event',
                'file_name')

    def to_representation(self, instance):
        representation = super(FolderuploadSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return Folderupload.objects.create(**validated_data)

class  Folderupload1Serializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = Folderupload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event',
                'file_name')

    # def to_representation(self, instance):
    #   representation = super(FolderuploadSerializer, self).to_representation(instance)
    #   representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
    #   return representation

    def create(self, validated_data):
        return Folderupload.objects.create(**validated_data)



class  FolderOrFileMoveSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')

    class Meta:
        model = FolderOrFileMove 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderOrFileMoveSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderOrFileMove.objects.create(**validated_data)

class  FolderOrFileCopySerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = FolderOrFileCopy 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderOrFileCopySerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderOrFileCopy.objects.create(**validated_data)

class  FolderDeleteDownloadSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    
    class Meta:
        model = FolderDeleteDownload 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderDeleteDownloadSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderDeleteDownload.objects.create(**validated_data)

# class  FolderDrmDownloadSerializer(serializers.ModelSerializer):
#   user = get_primary_key_related_model(UserSerializer, many = False)
#   folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    
#   class Meta:
#       model = FolderDrmDownload 
#       fields = ('id', 
#               'user', 
#               'dataroom', 
#               'folder',
#               'created_date',
#               'event')

#   def to_representation(self, instance):
#       representation = super(FolderDrmDownloadSerializer, self).to_representation(instance)
#       representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
#       return representation

#   def create(self, validated_data):
#       return FolderDrmDownload.objects.create(**validated_data)









class  FolderActivityPrintSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    
    class Meta:
        model = FolderPrint 
        fields = ('id', 
                'user', 
                'dataroom', 
                'folder',
                'created_date',
                'event')

    def to_representation(self, instance):
        representation = super(FolderActivityPrintSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def create(self, validated_data):
        return FolderPrint.objects.create(**validated_data)

class RecentUpdateSerializer(serializers.ModelSerializer):
    # user = get_primary_key_related_model(UserSerializer)
    # file = get_primary_key_related_model(DataroomFolderSerializer)
    class Meta:
        model = RcentUpdate
        fields = ('id', 'user', 'member', 'categories','dataroom',
                    'subject', 'message','send_update_email',
                    'created_at', 'modified_at', 'document', 'file'
                )

    def create(self, validated_data):
        recent_update =  RcentUpdate.objects.create(**validated_data) 
        from . import utils
        if recent_update:
            for user_id in self.context['member']:
                if user_id:
                    recent_update.member.add(user_id)
                    AllNotifications.objects.create(dataroom_updates_id=recent_update.id, dataroom_id=recent_update.dataroom_id, user_id=user_id)


            for group in self.context['groups']:
                if group:
                    recent_update.group.add(group)

            if len(self.context['groups']) > 0:
                member = DataroomMembers.objects.filter(end_user_group__in=self.context['groups'],dataroom_id = recent_update.dataroom_id, is_deleted=False,memberactivestatus=True)
                for mem in member:
                    recent_update.member.add(mem.member.id)
                    AllNotifications.objects.create(dataroom_updates_id=recent_update.id, dataroom_id=recent_update.dataroom_id, user_id=mem.member.id)

            if recent_update.send_update_email == True:
                utils.send_email_to_members(self.context['groups'],self.context['member'], recent_update)
        return recent_update


class RcentUpdateSerializer(serializers.ModelSerializer):
    # user = get_primary_key_related_model(UserSerializer)
    class Meta:
        model = RcentUpdate
        fields = ('id', 'user', 'member', 'categories','dataroom',
                    'subject', 'message','send_update_email',
                    'created_at', 'modified_at', 'document'
                )

    def create(self, validated_data):
        recent_update = RcentUpdate.objects.create(**validated_data) 
        if recent_update:
            for user_id in self.context['member']:
                if user_id:
                    recent_update.member.add(user_id)

            for group in self.context['groups']:
                if group:
                    recent_update.group.add(group)
                    
            for cat in self.context['categories']:
                if cat:
                    recent_update.categories.add(cat)
            if self.context['file']:
                for file_name in self.context['file']:
                    # if file_name.content_type == 'image/png' or file_name.content_type == 'image/jpg' or file_name.content_type == 'image/jpeg':                      
                    if file_name:
                        tt = time.time()
                        import re
                        import string
                        x = re.sub('['+string.punctuation+']', '', recent_update.subject).split()
                        # ind_obj = Individual.objects.filter(id=instance.id).first()
                        fs = FileSystemStorage(location='media/'+"/"+str(x[0])+"_"+str(tt))
                        filename = fs.save(file_name.name, file_name)
                        uploaded_file_url = fs.url(filename)
                        uploaded_file_url = uploaded_file_url.replace("/media/", "/"+str(x[0])+"_"+str(tt)+'/')
                        recent_update.document = uploaded_file_url
                        recent_update.document_file_name = file_name.name
                        recent_update.save()
        return recent_update





class CategoriesSerializer(serializers.ModelSerializer):
    # category_details = ManageDataroomCategoriesSerializer(many=False)
    class Meta:
        model = Categories
        fields = '__all__'

class ManageDataroomCategoriesSerializer(serializers.ModelSerializer):
    category = get_primary_key_related_model(CategoriesSerializer)
    user = get_primary_key_related_model(UserSerializer)
    dataroom = get_primary_key_related_model(DataroomSerializer)
    
    class Meta:
        model = ManageDataroomCategories
        fields = '__all__'

class Categories1Serializer(serializers.ModelSerializer):
    category_details = ManageDataroomCategoriesSerializer(many=False,)
    class Meta:
        model = Categories
        fields = '__all__'

class BulkuploadstatusSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    parentfolder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    class Meta:
        model = Bulkuploadstatus
        fields = '__all__'
    def to_representation(self, instance):
        representation = super(BulkuploadstatusSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

class Bulkuploadstatus1Serializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    parentfolder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom= serializers.SlugRelatedField(read_only=True,slug_field='dataroom_nameFront')
    class Meta:
        model = Bulkuploadstatus
        fields = '__all__'
    # def to_representation(self, instance):
    #   representation = super(BulkuploadstatusSerializer, self).to_representation(instance)
    #   representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
    #   return representation

class FolderuploadinbulkSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    folder = get_primary_key_related_model(DataroomFolderSerializer, many =False)
    dataroom = get_primary_key_related_model(DataroomSerializer, many=False)
    bulkupload = get_primary_key_related_model(BulkuploadstatusSerializer, many=False)

    class Meta:
        model = Folderuploadinbulk
        fields = '__all__'
    def to_representation(self, instance):
        representation = super(FolderuploadinbulkSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation
class FolderfailinbulkSerializer(serializers.ModelSerializer):
    user = get_primary_key_related_model(UserSerializer, many = False)
    dataroom = get_primary_key_related_model(DataroomSerializer, many=False)
    bulkupload = get_primary_key_related_model(BulkuploadstatusSerializer, many=False)

    class Meta:
        model = Folderfailinbulk
        fields = '__all__'


class BulkDownloadstatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = BulkDownloadstatus
        fields = '__all__'


class BulkDownloadstatus2Serializer(serializers.ModelSerializer):

    class Meta:
        model = BulkDownloadstatus
        fields = '__all__'
        # exclude = ['filename']
