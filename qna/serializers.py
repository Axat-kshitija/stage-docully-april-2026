from rest_framework import serializers
from .models import QuestionAnswer, FAQ
from data_documents.serializers import DataroomFolderSerializer, CategoriesSerializer
from userauth.serializers import UserSerializer
from django.db.models import Q

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
                # return {}
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)

        def to_representation(self, data):
            return model_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)


from users_and_permission.models import DataroomMembers

class QuestionAnswerSerializer(serializers.ModelSerializer):
    folder = get_primary_key_related_model(DataroomFolderSerializer, many=False)
    user = get_primary_key_related_model(UserSerializer, many=False)
    category = get_primary_key_related_model(CategoriesSerializer)
    replies = serializers.SerializerMethodField('replies_to_question')
    # answerd_ad = serializers.SerializerMethodField('answerd_admin')
    pending = serializers.SerializerMethodField('question_status')

    def replies_to_question(self, obj):
        count = QuestionAnswer.objects.filter(qna_id=obj.id).count()
        return count


    # def answerd_admin(self, obj):
    #     count = QuestionAnswer.objects.filter(qna_id=obj.id)
    #     ans=False
    #     for i in count:
    #         dd=DataroomMembers.objects.filter(member_id=i.user.id,dataroom_id=i.dataroom.id,is_deleted=False,is_dataroom_admin=True).exists()
    #         if dd:
    #             ans=True
    #             return ans
    #         else:
    #             return ans

        # return count

    def question_status(self, obj):
        count = QuestionAnswer.objects.filter(qna_id=obj.id)
        pending=True
        for i in count:
            dd=DataroomMembers.objects.filter(member_id=i.user.id,dataroom_id=i.dataroom.id,is_deleted=False,is_end_user=False).filter(Q(is_dataroom_admin=True)| Q(is_la_user=True)).exists()
            if dd:
        # if count > 0 :
                pending = False
            # else:
            #     pending = True
        return pending

    class Meta:
        model = QuestionAnswer
        fields = (
            'id',
            'user',
            'dataroom',
            'question',
            'answer', 
            'qna', 
            'folder',
            'created_date',
            'updated_date',
            'category',
            'acc',
            'final',
            'replies',
            # 'answerd_ad',
            'pending',
            'is_faq'
        )
    # def to_representation(self, instance):
    #     representation = super(QuestionAnswerSerializer, self).to_representation(instance)
    #     representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
    #     representation['updated_date'] = instance.updated_date.strftime('%d/%m/%Y %H:%M:%S')
    #     return representation

    def create(self, validated_data):
        return QuestionAnswer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.question = validated_data.get('question', instance.question)
        instance.answer = validated_data.get('answer', instance.answer)
        instance.save()
        return instance


class QuestionFileViewerAnswerSerializer(serializers.ModelSerializer):
    folder = get_primary_key_related_model(DataroomFolderSerializer, many=False)
    user = get_primary_key_related_model(UserSerializer, many=False)
    category = get_primary_key_related_model(CategoriesSerializer)
    replies = serializers.SerializerMethodField('replies_to_question')
    pending = serializers.SerializerMethodField('question_status')

    def replies_to_question(self, obj):
        count = QuestionAnswer.objects.filter(qna_id=obj.id).count()
        return count

    def question_status(self, obj):
        count = QuestionAnswer.objects.filter(qna_id=obj.id).count()
        if count > 0 :
            pending = False
        else:
            pending = True
        return pending

    class Meta:
        model = QuestionAnswer
        fields = (
            'id',
            'user',
            'dataroom',
            'question',
            'answer', 
            'qna', 
            'folder',
            'created_date',
            'updated_date',
            'category',
            'acc',
            'final',
            'replies',
            'pending',
            'is_faq'
        )

    def create(self, validated_data):
        return QuestionAnswer.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super(QuestionFileViewerAnswerSerializer, self).to_representation(instance)
        representation['created_date'] = instance.created_date.strftime('%d/%m/%Y %H:%M:%S')
        return representation

    def update(self, instance, validated_data):
        instance.question = validated_data.get('question', instance.question)
        instance.answer = validated_data.get('answer', instance.answer)
        instance.save()
        return instance



class FAQSerializer(serializers.ModelSerializer):
    folder = get_primary_key_related_model(DataroomFolderSerializer, many=False, allow_null=True)
    user = get_primary_key_related_model(UserSerializer, many=False, allow_null=True)
    created_by = get_primary_key_related_model(UserSerializer, many=False, allow_null=True)
    updated_by = get_primary_key_related_model(UserSerializer, many=False, allow_null=True)
    # category = get_primary_key_related_model(CategoriesSerializer)

    class Meta:
        model = FAQ
        fields = (
            'id',
            'user',
            'dataroom',
            'question',
            'answer', 
            'qna', 
            'folder',
            'created_date',
            'updated_date',
            'status',
            'created_by',
            'updated_by',
            # 'category',
            'acc',
            'final',
            'is_faq',
            'file_flag'
        )

    def create(self, validated_data):
        return FAQ.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.question = validated_data.get('question', instance.question)
        instance.answer = validated_data.get('answer', instance.answer)
        instance.save()
        return instance