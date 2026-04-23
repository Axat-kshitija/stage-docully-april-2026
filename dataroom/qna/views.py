from django.shortcuts import render
from .models import QuestionAnswer, FAQ
		# from .models import QuestionAnswer

from .serializers import QuestionAnswerSerializer, FAQSerializer
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from data_documents.serializers import ManageDataroomCategoriesSerializer
from data_documents.models import ManageDataroomCategories
import json
from django.http import HttpResponse, Http404, JsonResponse
from users_and_permission.models import DataroomMembers
from . import utils


class AcceptQuestion(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		user = request.user
		qna_obj = QuestionAnswer.objects.filter(id=int(request.data)).first()
		qna_obj.final = True
		qna_obj.save()
		return Response({'data': 'Final question added successfully!'}, status=status.HTTP_201_CREATED)
		# return Response(serializer.errors, status=status.HTTP_201_CREATED)


class GetQaReplyView(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		question_list = []
		user = request.user
		data = request.data
		question = QuestionAnswer.objects.filter(qna_id=pk)
		qna_serializer_list = QuestionAnswerSerializer(question, many=True)
		for qna_serializer in qna_serializer_list.data:
			category_details = ManageDataroomCategories.objects.filter(category_id=qna_serializer['category']['id'])
			serializer = ManageDataroomCategoriesSerializer(category_details, many=True)
			question_list.append({'question_details': qna_serializer, 'category_details': serializer.data})
		print('list data +++++++++++++++++>',question_list)
		# import pdb;pdb.set_trace();
		return Response(json.dumps(question_list), status=status.HTTP_201_CREATED)
		# return Response(question_list,status=status.HTTP_201_CREATED)



class UserQnaDetails(APIView):
	"""docstring for UserQnaDetails"""
	def get(self, request, pk, format=None):
		user = request.user
		data = request.data
		quest = QuestionAnswer.objects.filter(id=pk).first()
		quest_categ = ManageDataroomCategories.objects.filter(category_id = quest.category_id, dataroom_id=quest.dataroom_id).values_list('user_id', flat=True)
		categ = ManageDataroomCategories.objects.filter(dataroom_id=quest.dataroom_id).values_list('user_id', flat=True)
		member = DataroomMembers.objects.filter(dataroom_id=quest.dataroom_id,member_id=user.id).first()
		print(member.is_q_a_user, categ, user.id)
		if member.is_q_a_user == True and  user.id not in categ:
			print("not in")
			reply = True
		elif user.id == quest.user.id or user.id in quest_categ:
			reply = True
			print("in")
		else:
			reply = False
			print("False")
		print("REPLYYYYYYYY", reply)
		return Response({'reply':reply},status=status.HTTP_201_CREATED)

class QuestionAnswerDetails(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		question_list = []
		user = request.user
		data = request.data
		question = QuestionAnswer.objects.filter(id=pk).first()
		qna_serializer = QuestionAnswerSerializer(question, many=False)
		
		category_details = ManageDataroomCategories.objects.filter(category_id=qna_serializer.data['category']['id'])
		print(category_details)
		print(qna_serializer.data['category']['id'])
		serializer = ManageDataroomCategoriesSerializer(category_details, many=True)
		question_list.append({'question_details': qna_serializer.data, 'category_details': serializer.data})
		# import pdb;pdb.set_trace();
		return Response(json.dumps(question_list), status=status.HTTP_201_CREATED)
		# return Response(question_list,status=status.HTTP_201_CREATED)


class QuestionAnswerView(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		question_list = []
		user = request.user
		data = request.data
		q_list = []
		members = DataroomMembers.objects.filter(member=user.id,dataroom_id=pk).first()
		if members.is_q_a_submitter_user:
			question = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id, qna_id=None, answer=None)
			print(question)
			qna_serializer = QuestionAnswerSerializer(question, many=True).data
			return Response(qna_serializer, status=status.HTTP_201_CREATED)
		elif members.is_q_a_user:
			# categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
			question = QuestionAnswer.objects.filter(dataroom_id=pk, qna_id=None, answer=None)
			print(question)
			qna_serializer = QuestionAnswerSerializer(question, many=True).data
			return Response(qna_serializer, status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, pk, format=None):
		user = request.user
		data = request.data
		data['dataroom'] = int(pk)
		data['user'] = user.id
		print("dataaaaaaaa", data)
		serializer = QuestionAnswerSerializer(data=data)
		print("serializers is valid", serializer.is_valid())
		print("serializers is valid", serializer.errors)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data , status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_201_CREATED)


class SendQuestionView(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, pk, format=None):
		q_n = QuestionAnswer.objects.filter(id=pk).first()
		if q_n:
			q_n.acc = True
			q_n.reg = False
			q_n.save()
			serializer = QuestionAnswerSerializer(q_n)
		return Response(serializer.data , status=status.HTTP_201_CREATED)


class RegQuestionView(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, pk, format=None):
		q_n = QuestionAnswer.objects.filter(id=pk).first()
		if q_n:
			q_n.acc = False
			q_n.reg = True
			q_n.save()
			serializer = QuestionAnswerSerializer(q_n)
		return Response(serializer.data , status=status.HTTP_201_CREATED)


class QAnswerView(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, pk, format=None):
		user = request.user
		data = request.data
		data['dataroom'] = int(pk)
		data['user'] = user.id
		data.update(QuestionAnswer.objects.filter(id=pk).first().__dict__)
		print("dataaaaaaaa", data)
		obj_dict = QuestionAnswer.objects.create(user_id=user.id, dataroom_id=data['dataroom_id'], question=data['question'], answer=data['reply'], qna_id=data['id'], folder_id=data['folder_id'], category_id=data['category_id'])
		serializer = QuestionAnswerSerializer(obj_dict, many=False)
		# utils.send_qna_reply_mail(serializer.data)

		data = serializer.data
		print('data------->',data)
		print('---',data.get('qna'))
		qna = QuestionAnswer.objects.get(id=data.get('qna'))
		subject = "Replied to your Question****"
		to = [qna.user.email]
		# from_email = data.get('user').get('email')

		from constants.constants import backend_ip
		from django.template.loader import render_to_string, get_template
		from django.core.mail import EmailMessage, EmailMultiAlternatives
		ctx = {
			'email': to,
			'subject': subject,
			'data':data,
			'qna':qna
			}
		print('ctx-------',ctx)
		print('---------------------------to',to)
		print('from email',from_email)

		message = get_template('emailer/replied_question.html').render(ctx)
		# message = "hello world "
		from_email = settings.EMAIL_HOST_USER

		msg = EmailMessage(subject, message, to=to, from_email=from_email)
		# msg.attach_file(data.path.path)
		msg.content_subtype = 'html'
		msg.send()
		# if serializer.is_valid():
		# 	serializer.save()
		return Response(serializer.data , status=status.HTTP_201_CREATED)
		# return Response(serializer.errors, status=status.HTTP_201_CREATED)

class AddOrRemoveFaq(APIView):
	"""docstring for AddOrRemoveFaq"""
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		faq = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
		print(faq)
		serializer = FAQSerializer(faq, many=True)
		return Response(serializer.data , status=status.HTTP_201_CREATED)

	def post(self, request, pk, format=None):
		print(request.data)
		user = request.user
		if(request.data.get('id')=='' or request.data.get('id')==None):
			serializer = FAQSerializer(data={'user':request.data.get('user').get('id'),'question':request.data.get('question'),'answer':request.data.get('answer'),'qna':request.data.get('qna'),'folder':request.data.get('folder').get('id'),'is_faq':True,'dataroom':request.data.get('dataroom'),'created_by':request.user.id, 'updated_by':request.user.id})
			print("serializers is valid", serializer.is_valid())
			print("serializers is valid", serializer.errors)
			if serializer.is_valid():
				serializer.save()
				faq = FAQ.objects.filter(id=serializer.data.get('id')).update( updated_by='')
				faq = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
				serializer = FAQSerializer(faq, many=True)
				return Response(serializer.data , status=status.HTTP_201_CREATED)
		elif(request.data.get('status')):
			faq = FAQ.objects.filter(id=request.data.get('id')).update(question = request.data.get('question'), answer=request.data.get('answer'), updated_by=request.user.id)

			faq_data = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
			print(request.user.id)
			serializer = FAQSerializer(faq_data, many=True)
			return Response(serializer.data , status=status.HTTP_201_CREATED)
		else:
			faq = FAQ.objects.filter(id=request.data.get('id')).update(status = request.data.get('status'), updated_by=request.user.id)

			faq_data = FAQ.objects.filter(dataroom=pk, status=True).order_by('-updated_date').order_by('-created_date')
			print(request.user.id)
			serializer = FAQSerializer(faq_data, many=True)
			return Response(serializer.data , status=status.HTTP_201_CREATED)
		return Response([] , status=status.HTTP_201_CREATED)
		# return Response(serializer.errors, status=status.HTTP_201_CREATED)

		

class QAnswerReport(APIView):
	"""docstring for QAnswerReport"""
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		user = request.user
		data = request.data
		from_date = request.GET.get('from_date')
		to_date = request.GET.get('to_date')
		import datetime
		todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
		first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

		obj_dict = QuestionAnswer.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date, qna_id=None, answer=None)
		serializer = QuestionAnswerSerializer(obj_dict, many=True)
		data = serializer.data
		data.sort(key=lambda item:item['created_date'], reverse=True)
		return Response(data , status=status.HTTP_201_CREATED)


class ExportQNA(APIView):
	"""docstring for QAnswerReport"""
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		user = request.user
		data = request.data
		from_date = request.GET.get('from_date')
		to_date = request.GET.get('to_date')
		import datetime
		todays_date = datetime.datetime.strftime(datetime.datetime.strptime( to_date, '%Y-%m-%d'),'%Y-%m-%d 23:59:59+05:30')
		first_date = datetime.datetime.strftime(datetime.datetime.strptime( from_date, '%Y-%m-%d'),'%Y-%m-%d 00:00:00+05:30')

		obj_dict = QuestionAnswer.objects.filter(dataroom_id=pk, created_date__gte=first_date, created_date__lte=todays_date, qna_id=None, answer=None)
		serializer = QuestionAnswerSerializer(obj_dict, many=True)
		data = serializer.data
		data.sort(key=lambda item:item['created_date'], reverse=True)
		from . import utils
		import csv
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="QNA.csv"'
		writer = csv.writer(response)

		header_data, datas = utils.getExcelDataQnaReport(data)

		writer.writerow(header_data)
		writer.writerows(datas)
		return response
		# return Response(serializer.data , status=status.HTTP_201_CREATED)

class QAnswerAnalytics(APIView):
	"""docstring for QAnswerReport"""
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		user = request.user
		data = {}
		members = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id, is_deleted=False).first()
		if members.is_dataroom_admin or members.is_la_user:
			qna_obj = QuestionAnswer.objects.filter(dataroom_id=pk, answer=None, qna_id=None)
			data['total_questions'] = qna_obj.count()
			data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=pk).exclude(answer=None, qna_id=None).count()
		else:
			qna_obj = QuestionAnswer.objects.filter(dataroom_id=pk,user_id=user.id, answer=None, qna_id=None)
			data['total_questions'] = qna_obj.count()
			data['total_answer'] = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id).exclude(answer=None, qna_id=None).count()
		answered = 0
		pending = 0
		for qna in qna_obj:
			answered_count = QuestionAnswer.objects.filter(qna_id=qna.id).count()
			if answered_count > 0:
				answered += 1
			else:
				pending += 1
		data['answered'] = answered
		data['pending'] = pending
		return Response(data , status=status.HTTP_201_CREATED)

class QuestionAnswerFilteringView(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk,pk1, format=None):
		question_list = []
		user = request.user
		data = request.data
		q_list = []
		members = DataroomMembers.objects.filter(member=user.id,dataroom_id=pk).first()
		pk1 = int(pk1)
		print(pk1)
		if pk1 == -1:
			categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
			question = QuestionAnswer.objects.filter(dataroom_id=pk,category_id__in=categories, qna_id=None, answer=None)
			print("questionsssss", question)
			qna_serializer = QuestionAnswerSerializer(question, many=True).data
			return Response(qna_serializer, status=status.HTTP_201_CREATED)
		elif pk1 == 0:
			categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
			answer = QuestionAnswer.objects.filter(dataroom_id=pk,category_id__in=categories).exclude(qna_id=None).values('qna_id')
			question = QuestionAnswer.objects.filter(dataroom_id=pk, id__in=answer, category_id__in=categories)
			print("questionsssss", question)
			qna_serializer = QuestionAnswerSerializer(question, many=True).data
			return Response(qna_serializer, status=status.HTTP_201_CREATED)
		else:
			if members.is_q_a_submitter_user:
				question = QuestionAnswer.objects.filter(dataroom_id=pk, user_id=user.id,category_id=pk1, qna_id=None, answer=None)
				qna_serializer = QuestionAnswerSerializer(question, many=True).data
				return Response(qna_serializer, status=status.HTTP_201_CREATED)
			elif members.is_q_a_user:
				# categories = ManageDataroomCategories.objects.filter(dataroom_id=pk, user=members.member_id).values('category_id')
				question = QuestionAnswer.objects.filter(dataroom_id=pk,category_id=pk1, qna_id=None, answer=None)
				print("questionsssss", question)
				qna_serializer = QuestionAnswerSerializer(question, many=True).data
				return Response(qna_serializer, status=status.HTTP_201_CREATED)
			else:
				return Response(status=status.HTTP_400_BAD_REQUEST)
