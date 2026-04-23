from rest_framework import serializers
from django.contrib.auth.models import User, Group 
from django.utils.crypto import get_random_string
from django.utils import timezone 
import datetime
from userauth.models import User
from userauth.serializers import UserSerializer
from .models import *
from dataroom.serializers import DataroomSerializer
from users_and_permission.models import DataroomMembers



def get_primary_key_related_model(model_class, **kwargs):
    """
    Nested serializers are a mess. https://stackoverflow.com/a/28016439/2689986
    This lets us accept ids when saving / updating instead of nested objects.
    Representation would be into an object (depending on model_class).
    """
    # class PrimaryKeyNestedMixin(model_class):

    #     def to_internal_value(self, data):
    #         # print("---------", model_class.Meta.model.z.get(pk=data), "==========", data)
    #         try:
    #             return model_class.Meta.model.z.get(pk=data)
    #         except model_class.Meta.model.DoesNotExist:
    #             self.fail('does_not_exist', pk_value=data)
    #         except (TypeError, ValueError):
    #             self.fail('incorrect_type', data_type=type(data).__name__)

    #     def to_representation(self, data):
    #         return model_class.to_representation(self, data)

    # return PrimaryKeyNestedMixin(**kwargs)


class VotingSerializer(serializers.ModelSerializer):
	# vote_created_by = get_primary_key_related_model(UserSerializer, many=False)
	# dataroom = get_primary_key_related_model(DataroomSerializer, many=False)

	class Meta:
		model = Vote
		fields = (
		'id',
		'title',
		'dataroom',
		'vote_created',
		'vote_updated',
		'vote_created_by',
		'start',
		'end',
		'is_deleted',
		'status', 
		'description',
		'path',
		'document_file_name',
		'dataroomfile',
		'file_size',
		'file_size_mb',

		)
		def create(self, validated_data):
			vote = Vote.objects.create(**validated_data)

			if self.context['file']:
				for file_name in self.context['file']:                    
					if file_name:
						tt = time.time()
						import re
						import string
						x = re.sub('['+string.punctuation+']', '', vote.subject).split()
						# ind_obj = Individual.objects.filter(id=instance.id).first()
						fs = FileSystemStorage(location='media/'+"/"+str(x[0])+"_"+str(tt))
						filename = fs.save(file_name.name, file_name)
						uploaded_file_url = fs.url(filename)
						uploaded_file_url = uploaded_file_url.replace("/media/", "/"+str(x[0])+"_"+str(tt)+'/')
						vote.document = uploaded_file_url
						vote.document_file_name = file_name.name
						vote.save()
			return vote


		def update(self, instance, validated_data):
			return instance

class VotingListSerializer(serializers.ModelSerializer):
	vote_created_by = get_primary_key_related_model(UserSerializer, many=False)
	dataroom = get_primary_key_related_model(DataroomSerializer, many=False)

	class Meta:
		model = Vote
		fields = (
		'id',
		'title',
		'dataroom',
		'vote_created',
		'vote_updated',
		'vote_created_by',
		'start',
		'end',
		'is_deleted',
		'status', 
		'description',
		'path',
		'document_file_name',
		'dataroomfile',
		'file_size',
		'file_size_mb',
		)
		def create(self, validated_data):
			return Vote.objects.create(**validated_data)

		def update(self, instance, validated_data):
			return instance


class VoterGroupSerializer(serializers.ModelSerializer):
	# created_by = get_primary_key_related_model(UserSerializer, many=False)
	# dataroom = get_primary_key_related_model(DataroomSerializer, many=False)
	
	class Meta:
		model = VoterGroup
		fields = '__all__'

		def create(self, validated_data):
			return VoterGroup.objects.create(**validated_data)

class VoterGroupSerializerList(serializers.ModelSerializer):
	created_by = get_primary_key_related_model(UserSerializer, many=False)
	dataroom = get_primary_key_related_model(DataroomSerializer, many=False)
	
	class Meta:
		model = VoterGroup
		fields = '__all__'
		

class VoterGroupMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = VoterGroupMember
		fields = '__all__'
		def create(self, validated_data):
			return VoterGroupMember.objects.create(**validated_data)

		def update(self, instance, validated_data):
			return instance

class VoterGroupMemberListSerializer(serializers.ModelSerializer):
	member = get_primary_key_related_model(DataroomMembers)
	votergroup = get_primary_key_related_model(VoterGroupSerializerList)
	class Meta:
		model = VoterGroupMember
		fields = '__all__'
			

class VotingDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = VotingResult
		fields = '__all__'
		def create(self, validated_data):
			return VotingResult.objects.create(**validated_data)

		def update(self, instance, validated_data):
			return instance


class VotingDetailsListSerializer(serializers.ModelSerializer):
	vote = get_primary_key_related_model(VotingSerializer)
	member = get_primary_key_related_model(DataroomMembers)
	dataroom = get_primary_key_related_model(DataroomSerializer)
	user = get_primary_key_related_model(User)
	class Meta:
		model = VotingResult
		fields = '__all__'