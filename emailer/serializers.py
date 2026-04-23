from .models import Emailer
from rest_framework import serializers

class EmailerSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Emailer
		fields = ('id', 
				'user', 
				'from_email', 
				'subject', 
				'body_html', 
				'emailer_type' , 
				'to_email'				)

	def create(self, validated_data):
		"""
		Create and return a new `DataroomModules` instance, given the validated data.
		"""
		# print ("validated data is", validated_data)
		return Emailer.objects.create(**validated_data)


	def update(self, instance, validated_data):
		"""
		Update and return an existing `DataroomModules` instance, given the validated data.
		"""
		instance.user = validated_data.get('user', instance.user)
		instance.from_email = validated_data.get('from_email', instance.from_email)
		instance.subject = validated_data.get('subject', instance.subject)
		instance.body_html = validated_data.get('body_html', instance.body_html)        
		instance.emailer_type = validated_data.get('emailer_type', instance.emailer_type)
		instance.to_email = validated_data.get('to_email', instance.to_email)
		instance.save()
		return instance
