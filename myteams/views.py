from django.shortcuts import render
from .models import MyTeams
from rest_framework.views import APIView
from .serializers import *
from rest_framework import permissions, routers, serializers, viewsets
from userauth.models import TokenAuthentication,Token
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from userauth.models import User, InviteUser
from userauth.serializers import UserSerializer, InviteUserSerializer
from userauth import constants
from emailer import utils as emailer_utils
from dataroom.models import Dataroom,dataroomProLiteFeatures
from dataroom.serializers import DataroomSerializer
from django.db.models import Count, Min, Sum, Avg
# Create your MyTeamApiView views here.
from decimal import Decimal
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse, StreamingHttpResponse
from rest_framework import pagination, serializers
paginator = pagination.PageNumberPagination()


class MyTeamsApiView(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)
	
	def post(self, request, format=None):
		user = request.user
		data = request.data
		chaneldata=Mychanels.objects.filter(id=data["chanel"]).last()
		if request.data.get('edit')==False:			
			team_consumed =MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_storage_allowed')).get('dataroom_storage_allowed__sum') if MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_storage_allowed')).get('dataroom_storage_allowed__sum') else Decimal(0.00)
		else:
			team_consumed =MyTeams.objects.filter(chanel_id=data["chanel"]).exclude(id=request.data.get('id')).aggregate(Sum('dataroom_storage_allowed')).get('dataroom_storage_allowed__sum') if MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_storage_allowed')).get('dataroom_storage_allowed__sum') else Decimal(0.00)
		
		team_consumed=Decimal(team_consumed if team_consumed != None else Decimal(0.00))+Decimal(data["dataroom_storage_allowed"])
		remainingspace=Decimal(chaneldata.dataroom_storage_allowed)-Decimal(team_consumed)
		if Decimal(remainingspace)>=0.00:
			if request.data.get('edit')==False:			
				team_dataroom =(MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_allowed')).get('dataroom_allowed__sum')) if MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_allowed')).get('dataroom_allowed__sum') else 0
			else:
				team_dataroom =(MyTeams.objects.filter(chanel_id=data["chanel"]).exclude(id=request.data.get('id')).aggregate(Sum('dataroom_allowed')).get('dataroom_allowed__sum')) if MyTeams.objects.filter(chanel_id=data["chanel"]).aggregate(Sum('dataroom_allowed')).get('dataroom_allowed__sum') else 0
			team_dataroom= team_dataroom if team_dataroom != None else 0 + data["dataroom_storage_allowed"]
			remainingdataroom=chaneldata.dataroom_allowed-team_dataroom
			if remainingdataroom>=0:
				if request.data.get('edit')==False:			
					data["user"] = user.id
					data["team_created_by"] = user.id
					data['onlinesubscriber']=False
					my_team_serializer = MyTeamsSerializer(data=data)
				else:
					myteamdata=MyTeams.objects.get(id=request.data.get('id'))
					my_team_serializer = MyTeamsSerializer(myteamdata,data=data)
				print(data,'000000000000000000')
				if my_team_serializer.is_valid():
					my_team_serializer.save()
					return Response(my_team_serializer.data, status=status.HTTP_201_CREATED)
				return Response(my_team_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response('Dataroom Number exceed', status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response('storage space exceed', status=status.HTTP_400_BAD_REQUEST)


	def get(self, request, format=None):
		user = request.user
		my_team = []
		serializer1=[]
		if user.is_superadmin:
			my_team = MyTeams.objects.filter(onlinesubscriber=False)
			serializer1 = MyTeamsSerializer(my_team, many=True).data
		else:   
			print('user.id',user.id)
			if MyTeams.objects.filter(user_id=user.id,onlinesubscriber=False).exists():
				my_team = MyTeams.objects.filter(user_id=user.id)
				serializer1 = MyTeamsSerializer(my_team, many=True).data     
			if TeamMembers.objects.filter(member_id=user.id).exists():
				print('999999999')                  
				my_team_id = [my_team.myteam.id for my_team in TeamMembers.objects.filter(member_id=user.id)]
				my_team = MyTeams.objects.filter(id__in = my_team_id,onlinesubscriber=False)
				serializer2 = MyTeamsSerializer(my_team, many=True).data
				serializer1.append(serializer2)
				print(serializer1)
		return Response(serializer1)

		# if user.is_team:
		#     my_team = MyTeams.objects.filter(user_id=user.id)
		#     serializer1 = MyTeamsSerializer(my_team, many=True).data

		# if user.is_team_member:
		#     my_team_id = [my_team.myteam.id for my_team in TeamMembers.objects.filter(member_id=user.id)]
		#     my_team = MyTeams.objects.filter(id__in = my_team_id)
		#     serializer2 = MyTeamsSerializer(my_team, many=True).data
		#     if user.is_team:
		#         serializer1.extend(serializer2)
		#     else:
		#         serializer1=serializer2
		# if user.is_superadmin:
		#     my_team = MyTeams.objects.filter()
		#     serializer1 = MyTeamsSerializer(my_team, many=True).data
		# return Response(serializer1)


class chanelApiView(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)
	
	def post(self, request, format=None):
		user = request.user
		data = request.data
		if request.data.get('edit')==False:			
			data["user"] = user.id
			data["chanel_by"] = user.id
			my_team_serializer = MychanelsSerializer(data=data)
		else:
			mychaneldata=Mychanels.objects.get(id=request.data.get('id'))
			my_team_serializer = MychanelsSerializer(mychaneldata,data=data)
		if my_team_serializer.is_valid():
			my_team_serializer.save()
			return Response(my_team_serializer.data, status=status.HTTP_201_CREATED)
		return Response(my_team_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, format=None):
		user = request.user
		my_team = []
		serializer1={}
		if user.is_superadmin:
			my_team = Mychanels.objects.filter()
			serializer1 = MychanelsSerializer(my_team, many=True).data
		else:   
			# if Mychanels.objects.filter(user_id=user.id).exists():
			# 	my_team = Mychanels.objects.filter(user_id=user.id)
			# 	serializer1 = MychanelsSerializer(my_team, many=True).data    
			print(user.id,'ppppp') 
			if chanelMembers.objects.filter(member_id=user.id).exists():                  
				print(user.id,'ppppp') 
				my_team_id = [my_team.chanel.id if my_team.chanel else -1   for my_team in chanelMembers.objects.filter(member_id=user.id)]
				my_team = Mychanels.objects.filter(id__in = my_team_id)
				serializer1 = MychanelsSerializer(my_team, many=True).data
				print(serializer1)
		return Response(serializer1)

	
class MyTeamDetailView(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get_object(self, pk):
		try:
			return MyTeams.objects.get(pk=pk)
		except MyTeams.DoesNotExist:
			raise Http404
	
	def put(self, request, pk, format=None):     
		# print ("Inside my MyTeamDetailView page")
		from decimal import Decimal
		# print ("pk is", pk)
		user = request.user
		data = request.data.get('myTeam')
		del data['my_team_logo']
		# print ("data is", data)
		snippet = self.get_object(pk)
		serializer = MyTeamsSerializer(snippet, data=data)
		dataroom_storage = Dataroom.objects.filter(my_team_id=snippet.id).aggregate(Sum('dataroom_storage_allocated')).get('dataroom_storage_allocated__sum')
		dataroom_storage = dataroom_storage if dataroom_storage != None else Decimal(0.00)
		# print ("serializer is valid", serializer.is_valid())
		# print ("serializer is errors", serializer.errors)
		# print("dataaaaaaaaaa", dataroom_storage, snippet.dataroom_storage_allowed)
		if dataroom_storage <= Decimal(data['dataroom_storage_allowed']):
			if serializer.is_valid():
				serializer.save()
				return Response({'msg':snippet.team_name+' Team updated successfully'})
		else:
			return Response({'msg':'Total dataroom storage should be less than team dataroom_storage_allowed'})
		return Response(status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, pk, format=None):
		user = request.user
		data = request.data
		snippet = self.get_object(pk)
		serializer = MyTeamsSerializer(snippet, many=False)
		if user.is_superadmin:
			return Response({'teamdata':serializer.data,'createdataroomaccess':'True'}) 
		else:
			memberdataa=TeamMembers.objects.filter(myteam_id=pk,member_id=user.id).last()
			if memberdataa:
				if memberdataa.allowtoaddnewdataroom==True:
					return Response({'teamdata':serializer.data,'createdataroomaccess':'True'}) 
				else:
					return Response({'teamdata':serializer.data,'createdataroomaccess':'False'}) 
			else:
				return Response('member data not found') 



	def delete(self, request, pk, format=None):
		user = request.user
		data = request.data
		snippet = self.get_object(pk)
		snippet.delete()
		data = {
		   'msg': "My team successfully deleted !"
		}
		return Response(data, status=status.HTTP_201_CREATED)

class MyTeamBrandingDetailView(APIView):
	
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get_object(self, pk):
		try:
			return MyTeamBranding.objects.get(my_team_branding=pk)
		except MyTeamBranding.DoesNotExist:
			return Response({'result':False}, status=status.HTTP_400_BAD_REQUEST)
	
	def put(self, request, pk, format=None):     
		user = request.user
		data = request.data.get('my_team_branding')
		del data["favicon_icon"]
		del data["branding_logo"]
		del data["email_header"]
		# print ("data is", data)
		pk = data.get('my_team_branding')
		# print ("priamry key is", pk)
		snippet = self.get_object(pk)
		serializer = MyTeamBrandingSerializer(snippet, data= data)
		# print ("serializer is valid", serializer.is_valid())
		# print ("serializer errors", serializer.errors)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, pk, format=None):
		user = request.user
		data = request.data
		snippet = self.get_object(pk)
		serializer = MyTeamBrandingSerializer(snippet, many=False)
		return Response(serializer.data) 

	def delete(self, request, pk, format=None):
		user = request.user
		data = request.data
		snippet = self.get_object(pk)
		snippet.delete()
		data = {
		   'msg': "My team successfully deleted !"
		}
		return Response(data, status=status.HTTP_201_CREATED)

class RevertDefaultMyTeamBrandingSetting(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get_object(self, pk):
		try:
			return MyTeamBranding.objects.get(pk=pk)
		except MyTeamBranding.DoesNotExist:
			raise Http404

	def post(self, request, pk, format=None):
		user = request.user
		data = request.data.get('my_team_branding')
		# print ("actutal data is ", data)
		# print ("team branding default primary key is", pk)
		my_team_branding = self.get_object(pk)
		default_data = self.set_default_team_branding_setting(data)
		# print ("default_data is", default_data)
		# print ("primary key is", pk)
		my_team_branding_serializer = MyTeamBrandingSerializer(my_team_branding, data=default_data)
		# print ("my team branding serializer is valid", my_team_branding_serializer.is_valid())
		# print ("my team errors", my_team_branding_serializer.errors)        
		if my_team_branding_serializer.is_valid():
			my_team_branding_serializer.save()
			# print ("my_team_branding_serializer data", my_team_branding_serializer.data)
			return Response(my_team_branding_serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)


	def set_default_team_branding_setting(self, new_data):
		data = {
			'border_top_color': '#f200bd', 
			'background_color': '#f200bd', 
			'email_background_color' :'#f200bd', 
			'custom_login_border_color' : '#f200bd', 
			'border_top_color' : '#f200bd', 
			'my_team_branding' : new_data.get('my_team_branding'), 
			'id' : new_data.get('id'), 
			'my_team_branding_done_by': new_data.get('my_team_branding_done_by') , 
		}

		return data

class UploadMyTeamLogo(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, pk, format=None):
		# print ("primary key is", pk)
		my_team_logo = request.FILES.getlist('my_team_pic')
		data = request.data
		# print ("Upload my team logo method called", my_team_logo)
		my_teams = MyTeams.objects.get(id=pk)
		if my_teams.my_team_logo.url != "/home/cdms_backend/cdms2/media/default_images/my_team/myteam-default.png":        
			my_teams.my_team_logo.delete(save=True)
		my_teams.my_team_logo = my_team_logo[0]
		my_teams.save()
		my_teams_serializer = MyTeamsSerializer(my_teams, many=False)
		data = {
			'data': my_teams_serializer.data, 
			'msg' : 'My Team Profile successfully updated !' 
		}
		return Response(data, status=status.HTTP_201_CREATED)

class UploadMyTeamBrandingLogo(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, pk, format=None):
		# print ("primary key is", pk)
		branding_logo = request.FILES.getlist('branding_logo')
		email_header = request.FILES.getlist('email_header')
		favicon_icon = request.FILES.getlist('favicon_icon')
		# print ("branding_logo is", branding_logo)
		# print ("email header", email_header)
		# print ("favicon_icon", favicon_icon)
		data = request.data
		my_team_branding = MyTeamBranding.objects.get(my_team_branding=pk)
		if branding_logo:
			if my_team_branding.branding_logo.url != "/home/cdms_backend/cdms2/media/default_images/my_team/branding_logo.png":
				my_team_branding.branding_logo.delete(save=True)
				my_team_branding.branding_logo = branding_logo[0]
				my_team_branding.save()
				# print ("branding_logo is successfully saved!")
			else :
				# print ("my team branding_logo url is same as default url")
				my_team_branding.branding_logo = branding_logo[0]
				my_team_branding.save()
				
		elif email_header:
			# print ("email header is present")
			if my_team_branding.email_header.url != "/home/cdms_backend/cdms2/media/default_images/my_team/email_header.png":
				my_team_branding.email_header.delete(save=True)
				my_team_branding.email_header = email_header[0]
				my_team_branding.save()
			else:
				my_team_branding.email_header = email_header[0]
				my_team_branding.save()
				
		elif favicon_icon:
			# print ("update favicon_icon")
			if my_team_branding.favicon_icon.url != "/home/cdms_backend/cdms2/media/default_images/my_team/favicon_icon.ico":
				my_team_branding.favicon_icon.delete(save=True)  
				my_team_branding.favicon_icon = favicon_icon[0]
				my_team_branding.save()
			else:
				my_team_branding.favicon_icon = favicon_icon[0]
				my_team_branding.save()
		else:
			print ("Dont update anything")
		#`my_team_branding.save()
		my_team_branding_serializer = MyTeamBrandingSerializer(my_team_branding, many=False)
		# print ("my_team_branding_serializer",my_team_branding_serializer.data)
		data = {
			'msg' : 'My Team Profile successfully updated !', 
			'data' : my_team_branding_serializer.data
		}
		return Response(data, status=status.HTTP_201_CREATED)


class AddNewMemberToTeam(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes =(IsAuthenticated, )

	def get(self, request, pk, format=None):
		# print ("pk is ", pk)
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote

		team_members = [ member.member.id for member  in TeamMembers.objects.filter(myteam = pk)]
		all_members = User.objects.filter(id__in=team_members)
		team_members_serializer = UserSerializer(all_members, many=True)
		
		datarooms = Dataroom.objects.filter(my_team=pk)
		dataroom_serializer = DataroomSerializer(datarooms, many=True)
		datarom_data=dataroom_serializer.data
		for i in datarom_data:
			if i['dataroom_users_permitted']==10000:
				i['dataroom_users_permitted']=''
			vote_consumed = round((Vote.objects.filter(dataroom_id=i['id'],is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if Vote.objects.filter(dataroom_id=i['id'],is_deleted=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
			disclaimer_consumed =round((DataroomDisclaimer.objects.filter(dataroom_id=i['id']).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomDisclaimer.objects.filter(dataroom_id=i['id']).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
			dataroom_consumed = round((DataroomFolder.objects.filter(dataroom_id=i['id'],is_deleted_permanent=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum')) if DataroomFolder.objects.filter(dataroom_id=i['id'], is_deleted=False, is_folder=False).aggregate(Sum('file_size_mb')).get('file_size_mb__sum') else 0,0)
			total_consumed=vote_consumed + disclaimer_consumed + dataroom_consumed
			i['dataroom_consumed']=total_consumed

			i['dataroom_features']=dataroomProLiteFeatures.objects.filter(dataroom_id=i['id']).values()
		data = {
			'team_member_data':team_members_serializer.data, 
			'datarooms': datarom_data
		}
		return Response(data, status=status.HTTP_201_CREATED)

	def post(self, request, pk, format=None):
		# print ("post method called")
		data = request.data
		all_data = data.get("memeber")
		all_data['is_end_user'] = False
		# print ("data is", data)
		# print ("all_data is", all_data)
		user = request.user
		#step1
		""" check if dataroom allowed admin limit condition is satisfied or not """
		my_teams = MyTeams.objects.get(pk=pk)
		all_members = TeamMembers.objects.filter(myteam=pk).count()
		# print ("is admin allowd", my_teams.dataroom_admin_allowed >= all_members)
		# print ("my teams admin allowd", my_teams.dataroom_admin_allowed)
		# print ("my teams", all_members)
		# if my_teams.dataroom_admin_allowed > all_members :
		# print ("all members count is", all_members)
		flagg=0
		if my_teams.dataroom_admin_allowed!=None or my_teams.dataroom_admin_allowed=='':
			flagg=1
		elif my_teams.dataroom_admin_allowed>=all_members+1:
			flagg=1
		else:
			flagg=0
		if flagg==1:		
			is_user = User.objects.filter(email__iexact=all_data.get("email")).exists()
			#step1
			""" create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
			if is_user == False:
				all_data['password'] = "Password1#"
				all_data['is_admin'] = True
				all_data['is_active'] = True
				all_data['username']  = all_data.get('email')
				all_data['is_end_user'] = False
				all_data['is_team_member'] = True
				serializer = UserSerializer(data=all_data)
				if serializer.is_valid():
					serializer.save()
					unique_id = get_random_string(length=400)
					link = constants.link+"invitation_link/"+unique_id
					new_data = {
						'invitiation_sender':user.id, 
						'invitiation_receiver':serializer.data.get("id"), 
						'invitation_status':3, 
						'is_invitation_expired':False, 
						'invitation_link':link, 
						'invitation_token':unique_id 
					}

					invite_user_serializer = InviteUserSerializer(data=new_data)     
					if invite_user_serializer.is_valid():
						invite_user_serializer.save()
						emailer_utils.send_invitation_account_email(serializer.data, new_data)
						# if invitation has been sent to user add it inside memeber list
						# update member list
						member_data = {
							'member':serializer.data.get("id"), 
							'myteam':pk, 
							'member_added_by': user.id,
							'accesstodataroomusers':all_data['accesstodataroomusers'],
							'allowtoaddnewmember':all_data['allowtoaddnewmember'],
							'allowtoaddnewdataroom':all_data['allowtoaddnewdataroom'],
						}

						team_members_serializer = TeamMembersSerializer(data=member_data)
						# print ("team_members_serializer is valid", team_members_serializer.is_valid())
						# print ("team members serializer errors", team_members_serializer.errors) 
						if team_members_serializer.is_valid():
							team_members_serializer.save()
							data = {
								'success' : True ,
								'message': 'Member successfully added in this team!', 
								'data': serializer.data
							}
							return Response(data, status=status.HTTP_201_CREATED)
						else:
							print(team_members_serializer.errors)
					else:
						print ("erorr in storing invite_user_serializer information")
			else:
				# print ("User is aleardy exist")
				# print("Usererrr", all_data.get('email'))
				# user is already exist so get the data user specific data 
				if 	data.get("edit")==True:
					memberdata=TeamMembers.objects.get(id=data.get("id"))
					member_data = {
						'accesstodataroomusers':all_data['accesstodataroomusers'],
						'allowtoaddnewmember':all_data['allowtoaddnewmember'],
						'allowtoaddnewdataroom':all_data['allowtoaddnewdataroom'],				
					}					
					team_members_serializer = TeamMembersSerializer(memberdata,data=member_data)
					if team_members_serializer.is_valid():
						team_members_serializer.save()
						data = {
							'success' : True ,
							'message': 'Member successfully Updated in this team!', 
							'data': team_members_serializer.data
						}
						return Response(data, status=status.HTTP_201_CREATED)
					else:
						print(team_members_serializer.errors)
				else:
					existing_user = User.objects.get(email=all_data.get("email"))
					existing_user.is_team_member = True
					existing_user.save()
					member_data = {
						'member':existing_user.id, 
						'myteam':pk, 
						'member_added_by': user.id,
						'accesstodataroomusers':all_data['accesstodataroomusers'],
						'allowtoaddnewmember':all_data['allowtoaddnewmember'],
						'allowtoaddnewdataroom':all_data['allowtoaddnewdataroom'],				
					}

					team_members_serializer = TeamMembersSerializer(data=member_data)
					# print ("team_members_serializer is valid", team_members_serializer.is_valid())
					# print ("team members serializer errors", team_members_serializer.errors) 
					if team_members_serializer.is_valid():
						team_members_serializer.save()
						data = {
							'success' : True ,
							'message': 'Member successfully added in this team!', 
							'data': team_members_serializer.data
						}
						return Response(data, status=status.HTTP_201_CREATED)
					else:
						print(team_members_serializer.errors)

		else:
			return Response('Member limit Exceed', status=status.HTTP_400_BAD_REQUEST)




class AddNewMemberTochanel(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes =(IsAuthenticated, )

	def get(self, request, pk, format=None):
		# print ("pk is ", pk)
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote

		team_members = [ member.member.id for member  in chanelMembers.objects.filter(chanel_id= pk)]
		all_members = User.objects.filter(id__in=team_members)
		team_members_serializer = UserSerializer(all_members, many=True)
		
		myteamdata=MyTeams.objects.filter(chanel_id=pk)
			
		myteamdata_serializer = MyTeamsSerializer(myteamdata, many=True)
		myteamdata_data=myteamdata_serializer.data
		for i in myteamdata_data:
			dataaconsumed =[ member.dataroom_storage_allocated for member  in Dataroom.objects.filter(my_team_id= i['id'])] 
			dataaconsumed=sum(dataaconsumed)
			i['team_current_storage']=dataaconsumed
		data = {
			'team_member_data':team_members_serializer.data, 
			'team_data': myteamdata_data
		}
		return Response(data, status=status.HTTP_201_CREATED)

	def post(self, request, pk, format=None):
		# print ("post method called")
		data = request.data
		all_data = data.get("memeber")
		all_data['is_end_user'] = False
		# print ("data is", data)
		# print ("all_data is", all_data)
		user = request.user
		#step1
		""" check if dataroom allowed admin limit condition is satisfied or not """
		my_teams = Mychanels.objects.get(pk=pk)
		all_members = chanelMembers.objects.filter(chanel_id=pk).count()
		# print ("is admin allowd", my_teams.dataroom_admin_allowed >= all_members)
		# print ("my teams admin allowd", my_teams.dataroom_admin_allowed)
		# print ("my teams", all_members)
		# if my_teams.dataroom_admin_allowed > all_members :
		# print ("all members count is", all_members)
		if my_teams.dataroom_admin_allowed!=None or my_teams.dataroom_admin_allowed=='':
			flagg=1
		elif my_teams.dataroom_admin_allowed>=all_members+1:
			flagg=1
		else:
			flagg=0
		if flagg==1:
			is_user = User.objects.filter(email__iexact=all_data.get("email")).exists()
			#step1
			""" create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
			if is_user == False:
				all_data['password'] = "Password1#"
				all_data['is_admin'] = True
				all_data['is_active'] = True
				all_data['username']  = all_data.get('email')
				all_data['is_end_user'] = False
				all_data['is_team_member'] = True
				serializer = UserSerializer(data=all_data)
				if serializer.is_valid():
					serializer.save()
					unique_id = get_random_string(length=400)
					link = constants.link+"invitation_link/"+unique_id
					new_data = {
						'invitiation_sender':user.id, 
						'invitiation_receiver':serializer.data.get("id"), 
						'invitation_status':3, 
						'is_invitation_expired':False, 
						'invitation_link':link, 
						'invitation_token':unique_id 
					}

					invite_user_serializer = InviteUserSerializer(data=new_data)     
					if invite_user_serializer.is_valid():
						invite_user_serializer.save()
						emailer_utils.send_invitation_account_email(serializer.data, new_data)
						# if invitation has been sent to user add it inside memeber list
						# update member list
						member_data = {
							'member':serializer.data.get("id"), 
							'chanel':pk, 
							'member_added_by': user.id,
							'accesstodataroomusers':all_data['accesstodataroomusers'],
							'allowtoaddnewmember':all_data['allowtoaddnewmember'],
							'allowtoaddnewteam':all_data['allowtoaddnewteam'],
						}

						team_members_serializer = chanelMembersSerializer(data=member_data)
						# print ("team_members_serializer is valid", team_members_serializer.is_valid())
						# print ("team members serializer errors", team_members_serializer.errors) 
						if team_members_serializer.is_valid():
							team_members_serializer.save()
							data = {
								'success' : True ,
								'message': 'Member successfully added in this Chanel!', 
								'data': serializer.data
							}
							return Response(data, status=status.HTTP_201_CREATED)
						else:
							return Response(team_members_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			else:
				# print ("User is aleardy exist")
				# print("Usererrr", all_data.get('email'))
				# user is already exist so get the data user specific data 
				if 	data.get("edit")==True:
					memberdata=chanelMembers.objects.get(id=data.get("id"))
					member_data = {
						'accesstodataroomusers':all_data['accesstodataroomusers'],
						'allowtoaddnewmember':all_data['allowtoaddnewmember'],
						'allowtoaddnewteam':all_data['allowtoaddnewteam'],				
					}					
					team_members_serializer = chanelMembersSerializer(memberdata,data=member_data)
					if team_members_serializer.is_valid():
						team_members_serializer.save()
						data = {
							'success' : True ,
							'message': 'Member successfully Updated in this Channel!', 
							'data': team_members_serializer.data
						}
						return Response(data, status=status.HTTP_201_CREATED)
					else:
						return Response(team_members_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


				else:

					existing_user = User.objects.get(email=all_data.get("email"))
					existing_user.is_team_member = True
					existing_user.save()
					member_data = {
						'member':existing_user.id, 
						'chanel':pk, 
						'member_added_by': user.id,
						'accesstodataroomusers':all_data['accesstodataroomusers'],
						'allowtoaddnewmember':all_data['allowtoaddnewmember'],
						'allowtoaddnewteam':all_data['allowtoaddnewteam'],
					}

					team_members_serializer = chanelMembersSerializer(data=member_data)
					# print ("team_members_serializer is valid", team_members_serializer.is_valid())
					# print ("team members serializer errors", team_members_serializer.errors) 
					if team_members_serializer.is_valid():
						team_members_serializer.save()
						data = {
							'success' : True ,
							'message': 'Member successfully added in this Channel!', 
							'data': team_members_serializer.data
						}
						return Response(data, status=status.HTTP_201_CREATED)
					else:
						return Response(team_members_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		
		else:
			return Response('Member limit Exceed', status=status.HTTP_400_BAD_REQUEST)



class chanel_dashboard(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, format=None):
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote
		chanelcount=0
		serializerdata1=[]
		if request.user.is_superadmin:
			print('111111111111')
			if request.GET.get('id')==None or request.GET.get('id')=='':
				chanel=Mychanels.objects.filter(is_deleted=False)
			else:
				chanel=Mychanels.objects.filter(id=request.GET.get('id'), is_deleted=False)
			if chanel:
				chanelcount=chanel.count()
				for i in chanel:
					chanel1=Mychanels.objects.filter(id=i.id,is_deleted=False).last()
					serializerdata=MychanelsSerializer(chanel1,many=False).data
					myteamdata1=[ member.dataroom_storage_allowed for member  in MyTeams.objects.filter(chanel_id = i.id,is_deleted=False,onlinesubscriber=False)]
					myteamdata=[ member.id for member  in MyTeams.objects.filter(chanel_id = i.id,is_deleted=False,onlinesubscriber=False)]
					dataroomdata=[ member.dataroom_storage_allocated for member  in Dataroom.objects.filter(my_team_id__in = myteamdata,is_deleted=False)]
					serializerdata['myteamscount']=len(myteamdata)
					serializerdata['dataroomcount']=len(dataroomdata)
					serializerdata['dataroomstorage']=sum(dataroomdata)
					serializerdata['dataroomstorage1']=sum(myteamdata1)	
					serializerdata1.append(serializerdata)

		else:
			if request.GET.get('id')==None or request.GET.get('id')=='':
				memberdata = chanelMembers.objects.filter(member_id = request.user.id)
			else:
				memberdata = chanelMembers.objects.filter(chanel_id=request.GET.get('id'),member_id = request.user.id)
			# chanelcount=Mychanels.objects.filter(id__in=chaneldata,is_deleted=False).count()
			if memberdata:
				chanelcount=memberdata.count()
				for i in memberdata:
					print('111111111111')
					chanel=Mychanels.objects.filter(id=i.chanel.id,is_deleted=False).last()
					if chanel:
						chanel1=Mychanels.objects.get(id=chanel.id,is_deleted=False)
						serializerdata=MychanelsSerializer(chanel1,many=False).data
						myteamdata=[ member.id for member  in MyTeams.objects.filter(chanel_id = i.id,is_deleted=False,onlinesubscriber=False)]
						myteamdata1=[ member.dataroom_storage_allowed for member  in MyTeams.objects.filter(chanel_id = i.chanel.id,is_deleted=False,onlinesubscriber=False)]
						dataroomdata=[ member.dataroom_storage_allocated for member  in Dataroom.objects.filter(my_team_id__in = myteamdata,is_deleted=False)]
						serializerdata['myteamscount']=len(myteamdata)
						serializerdata['dataroomcount']=len(dataroomdata)
						serializerdata['dataroomstorage']=sum(dataroomdata)
						serializerdata['dataroomstorage1']=sum(myteamdata1)
						# serializerdata['dataroomstorage']=sum(dataroomdata)
						serializerdata['accesstocreateteam']=i.allowtoaddnewteam
						serializerdata1.append(serializerdata)
		return Response({'chanelcount':chanelcount,'data':serializerdata1}, status=status.HTTP_201_CREATED)


class chanel_allmember(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, format=None):
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote
		from users_and_permission.models import DataroomMembers
		serializerdata=[]
		membercount=0

		if request.user.is_superadmin:
				if request.GET.get('channel')==None or request.GET.get('channel')=='':
					chanel=Mychanels.objects.filter(is_deleted=False)
				else:
					chanel=Mychanels.objects.filter(is_deleted=False,chanel_name__icontains=request.GET.get('channel'))
				if chanel:
					for i in chanel:
						if request.GET.get('team')==None or request.GET.get('team')=='':
							myteamdata=MyTeams.objects.filter(chanel_id = i.id)
						else:
							myteamdata=MyTeams.objects.filter(team_name__icontains=request.GET.get('team'),chanel_id = i.id)
						# print(myteamdata,'check this rrrrrrrrrrr')
						if myteamdata:
							for j in myteamdata:
								if request.GET.get('dataroom')==None or request.GET.get('dataroom')=='':
									dataroomdata=Dataroom.objects.filter(my_team_id = j.id,is_deleted=False)
								else:
									dataroomdata=Dataroom.objects.filter(dataroom_nameFront__icontains=request.GET.get('dataroom'), my_team_id = j.id,is_deleted=False)
								# print(dataroomdata,'vvvvvvvv')
								if dataroomdata:
									for k in dataroomdata:
										if request.GET.get('role')=='admin':
											dataroommembers=DataroomMembers.objects.filter(is_dataroom_admin=True,dataroom_id= k.id,is_deleted=False)
										elif request.GET.get('role')=='laadmin':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=True,dataroom_id = k.id,is_deleted=False)
										elif request.GET.get('role')=='enduser':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=False,is_dataroom_admin=False,dataroom_id = k.id,is_deleted=False)
										else:
											dataroommembers=DataroomMembers.objects.filter(dataroom_id = k.id,is_deleted=False)
										if request.GET.get('userFullName')==None or request.GET.get('userFullName')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(Q(member__first_name__icontains=request.GET.get('userFullName')) | Q(member__last_name__icontains=request.GET.get('userFullName')))
										if request.GET.get('emailId')==None or request.GET.get('emailId')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(member__email__icontains=request.GET.get('emailId'))

										if dataroommembers:
											membercount=dataroommembers.count()
											for l in dataroommembers:
												if l.is_la_user:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':i.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'LA Admin'})
												elif l.is_dataroom_admin:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':i.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'Admin'})
												else:

													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':i.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'End User'})
										else:
											pass
											# return Response('member not present', status=status.HTTP_400_BAD_REQUEST)
								else:
									pass
									# return Response('dataroom not present', status=status.HTTP_400_BAD_REQUEST)
						else:
							pass
							# return Response('team not present', status=status.HTTP_400_BAD_REQUEST)
				else:
					return Response('chanel not present', status=status.HTTP_400_BAD_REQUEST)

		else:
			memberdata = chanelMembers.objects.filter(member_id = request.user.id)
			# chanelcount=Mychanels.objects.filter(id__in=chaneldata,is_deleted=False).count()
			if memberdata:
				for i in memberdata:
					print('111111111111')
					if request.GET.get('channel')==None or request.GET.get('channel')=='':
						chanel=Mychanels.objects.filter(id=i.chanel.id,is_deleted=False).last()
					else:
						chanel=Mychanels.objects.filter(id=i.chanel.id,is_deleted=False,chanel_name__icontains=request.GET.get('channel')).last()
					if chanel:
						if request.GET.get('team')==None or request.GET.get('team')=='':
							myteamdata=MyTeams.objects.filter(chanel_id = i.chanel.id)
						else:
							myteamdata=MyTeams.objects.filter(team_name__icontains=request.GET.get('team'),chanel_id = i.chanel.id)

						if myteamdata:
							for j in myteamdata:
								if request.GET.get('dataroom')==None or request.GET.get('dataroom')=='':
									dataroomdata=Dataroom.objects.filter(my_team_id = j.id,is_deleted=False)
								else:
									dataroomdata=Dataroom.objects.filter(dataroom_nameFront__icontains=request.GET.get('dataroom'), my_team_id = j.id,is_deleted=False)

								if dataroomdata:
									for k in dataroomdata:
										if request.GET.get('role')=='admin':
												dataroommembers=DataroomMembers.objects.filter(is_dataroom_admin=True,dataroom_id = k.id,is_deleted=False)
										elif request.GET.get('role')=='laadmin':
												dataroommembers=DataroomMembers.objects.filter(is_la_user=True,dataroom_id = k.id,is_deleted=False)
										elif request.GET.get('role')=='enduser':
												dataroommembers=DataroomMembers.objects.filter(is_la_user=False,is_dataroom_admin=False,dataroom_id = k.id,is_deleted=False)
										else:
												dataroommembers=DataroomMembers.objects.filter(dataroom_id = k.id,is_deleted=False)
										if request.GET.get('userFullName')==None or request.GET.get('userFullName')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(Q(member__first_name__icontains=request.GET.get('userFullName')) | Q(member__last_name__icontains=request.GET.get('userFullName')))
										if request.GET.get('emailId')==None or request.GET.get('emailId')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(member__email__icontains=request.GET.get('emailId'))

										if dataroommembers:
											membercount=dataroommembers.count()

											for l in dataroommembers:
												if l.is_la_user:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'LA Admin'})
												elif l.is_dataroom_admin:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'Admin'})
												else:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'End User'})
										else:
											pass
											# return Response('member not present', status=status.HTTP_400_BAD_REQUEST)
								else:
									pass
									# return Response('dataroom not present', status=status.HTTP_400_BAD_REQUEST)
						else:
							pass
							# return Response('team not present', status=status.HTTP_400_BAD_REQUEST)
					else:
						pass
						# return Response('chanel not present', status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response('data not present', status=status.HTTP_400_BAD_REQUEST)
		return Response({'membercount':membercount,'data':serializerdata}, status=status.HTTP_201_CREATED)





class team_allmember(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request,pk, format=None):
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote
		from users_and_permission.models import DataroomMembers
		serializerdata=[]
		membercount=0
		myteamdata=MyTeams.objects.filter(id = pk).last()
		if myteamdata:
								if request.GET.get('dataroom')==None or request.GET.get('dataroom')=='':
									dataroomdata=Dataroom.objects.filter(my_team_id = myteamdata.id,is_deleted=False)
								else:
									dataroomdata=Dataroom.objects.filter(dataroom_nameFront__icontains=request.GET.get('dataroom'), my_team_id = myteamdata.id,is_deleted=False)
								# print(dataroomdata,'vvvvvvvv')
								if dataroomdata:
									for k in dataroomdata:
										if request.GET.get('role')=='admin':
											dataroommembers=DataroomMembers.objects.filter(is_dataroom_admin=True,dataroom_id= k.id,is_deleted=False)
										elif request.GET.get('role')=='laadmin':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=True,dataroom_id = k.id,is_deleted=False)
										elif request.GET.get('role')=='enduser':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=False,is_dataroom_admin=False,dataroom_id = k.id,is_deleted=False)
										else:
											dataroommembers=DataroomMembers.objects.filter(dataroom_id = k.id,is_deleted=False)
										if request.GET.get('userFullName')==None or request.GET.get('userFullName')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(Q(member__first_name__icontains=request.GET.get('userFullName')) | Q(member__last_name__icontains=request.GET.get('userFullName')))
										if request.GET.get('emailId')==None or request.GET.get('emailId')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(member__email__icontains=request.GET.get('emailId'))

										if dataroommembers:
											membercount=dataroommembers.count()
											for l in dataroommembers:
												if l.is_la_user:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'LA Admin'})
												elif l.is_dataroom_admin:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'Admin'})
												else:

													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'End User'})
										else:
											return Response({'data':[]}, status=status.HTTP_201_CREATED)

								else:
									return Response({'data':[]}, status=status.HTTP_201_CREATED)
		else:
			return Response({'data':[]}, status=status.HTTP_201_CREATED)


		# else:
		# 	if memberdata:
		# 		for i in memberdata:
		# 			print('111111111111')
		# 			if request.GET.get('channel')==None or request.GET.get('channel')=='':
		# 				chanel=Mychanels.objects.filter(id=i.chanel.id,is_deleted=False).last()
		# 			else:
		# 				chanel=Mychanels.objects.filter(id=i.chanel.id,is_deleted=False,chanel_name__icontains=request.GET.get('channel')).last()
		# 			if chanel:
		# 				if request.GET.get('team')==None or request.GET.get('team')=='':
		# 					myteamdata=MyTeams.objects.filter(chanel_id = i.chanel.id)
		# 				else:
		# 					myteamdata=MyTeams.objects.filter(team_name__icontains=request.GET.get('team'),chanel_id = i.chanel.id)

		# 				if myteamdata:
		# 					for j in myteamdata:
		# 						if request.GET.get('dataroom')==None or request.GET.get('dataroom')=='':
		# 							dataroomdata=Dataroom.objects.filter(my_team_id = j.id,is_deleted=False)
		# 						else:
		# 							dataroomdata=Dataroom.objects.filter(dataroom_nameFront__icontains=request.GET.get('dataroom'), my_team_id = j.id,is_deleted=False)

		# 						if dataroomdata:
		# 							for k in dataroomdata:
		# 								if request.GET.get('role')=='admin':
		# 										dataroommembers=DataroomMembers.objects.filter(is_dataroom_admin=True,dataroom_id = k.id,is_deleted=False)
		# 								elif request.GET.get('role')=='laadmin':
		# 										dataroommembers=DataroomMembers.objects.filter(is_la_user=True,dataroom_id = k.id,is_deleted=False)
		# 								elif request.GET.get('role')=='enduser':
		# 										dataroommembers=DataroomMembers.objects.filter(is_la_user=False,is_dataroom_admin=False,dataroom_id = k.id,is_deleted=False)
		# 								else:
		# 										dataroommembers=DataroomMembers.objects.filter(dataroom_id = k.id,is_deleted=False)
		# 								if request.GET.get('userFullName')==None or request.GET.get('userFullName')=='':
		# 									pass
		# 								else:
		# 									dataroommembers=dataroommembers.filter(Q(member__first_name__icontains=request.GET.get('userFullName')) | Q(member__last_name__icontains=request.GET.get('userFullName')))
		# 								if request.GET.get('emailId')==None or request.GET.get('emailId')=='':
		# 									pass
		# 								else:
		# 									dataroommembers=dataroommembers.filter(member__email__icontains=request.GET.get('emailId'))

		# 								if dataroommembers:
		# 									membercount=dataroommembers.count()

		# 									for l in dataroommembers:
		# 										if l.is_la_user:
		# 											serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'LA Admin'})
		# 										elif l.is_dataroom_admin:
		# 											serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'Admin'})
		# 										else:
		# 											serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'chanel':chanel.chanel_name,'team':j.team_name,'dataroomname':k.dataroom_nameFront,'role':'End User'})
		# 								else:
		# 									pass
		# 									# return Response('member not present', status=status.HTTP_400_BAD_REQUEST)
		# 						else:
		# 							pass
		# 							# return Response('dataroom not present', status=status.HTTP_400_BAD_REQUEST)
		# 				else:
		# 					pass
		# 					# return Response('team not present', status=status.HTTP_400_BAD_REQUEST)
		# 			else:
		# 				pass
		# 				# return Response('chanel not present', status=status.HTTP_400_BAD_REQUEST)
		# 	else:
		# 		return Response('data not present', status=status.HTTP_400_BAD_REQUEST)
		return Response({'membercount':membercount,'data':serializerdata}, status=status.HTTP_201_CREATED)




class DeleteMemberFromMyTeam(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, pk, format=None):
		# print ("delete method called")
		member_id = request.data.get('member_id')
		# print ("primary key is", pk)
		# print ("member_id", member_id)
		data = {}
		try:
			# print ("inside try method")
			team_member = TeamMembers.objects.get(myteam_id=pk, member_id=member_id)
			# print ("Team member exist")
			if team_member:
				# print ("team member is exist")
				team_member.delete()
				data["msg"] = "Member successfully deleted !"
				return Response(data, status=status.HTTP_201_CREATED)
		except:
			# print ("exception is occured")
			data["msg"] = "member does not exist"
			return Response(data, status=status.HTTP_201_CREATED)

class DeleteMemberFromchanel(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, pk, format=None):
		# print ("delete method called")
		member_id = request.data.get('member_id')
		# print ("primary key is", pk)
		# print ("member_id", member_id)
		data = {}
		try:
			# print ("inside try method")
			team_member = chanelMembers.objects.get(chanel_id=pk, member_id=member_id)
			# print ("Team member exist")
			if team_member:
				# print ("team member is exist")
				team_member.delete()
				data["msg"] = "Member successfully deleted !"
				return Response(data, status=status.HTTP_201_CREATED)
		except:
			# print ("exception is occured")
			data["msg"] = "member does not exist"
			return Response(data, status=status.HTTP_201_CREATED)
from azure.storage.blob import BlockBlobService,PublicAccess
from userauth.models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids,pendinginvitations
from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
from data_documents.models import DataroomFolder
from datetime import timedelta,datetime
from django.utils import timezone
from userauth.utils import send_mail_to_superadmin,send_dataroomdelete_email,send_markedfordeletion_email,send_accessrevoked_email,send_offlinedataroomdelete_email
from Vote.models import Vote
from notifications.models import AllNotifications,Notifications
from users_and_permission.models import DataroomGroups,DataroomMembers,DataroomGroupPermission
import os
from dms.settings import *

class Deleteteamm(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
				if Dataroom.objects.filter(my_team_id=pk).exists():
					plandata1=Dataroom.objects.filter(my_team_id=pk)
					for l in plandata1:
						Dataroom.objects.filter(id=l.id).update(is_deleted=True,delete_at=datetime.now(),is_expired=True)
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=l.id).update(is_deleted=True,deleted_by_date=datetime.now(),is_deleted_permanent=True)
						if 	DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							# block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=l.id).exists():
							data=Vote.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=l.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)							
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf")	
						DataroomFolder.objects.filter(dataroom_id=l.id).delete()
						AllNotifications.objects.filter(dataroom_id=l.id).delete()
						Notifications.objects.filter(dataroom_id=l.id).delete()	
						Watermarking.objects.filter(dataroom_id=l.id).delete()
						pendinginvitations.objects.filter(dataroom_id=l.id).delete()
						DataroomGroups.objects.filter(dataroom_id=l.id).delete()
						DataroomMembers.objects.filter(dataroom_id=l.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=l.id).delete()
						Vote.objects.filter(dataroom_id=l.id).delete()						
						send_offlinedataroomdelete_email(subject= 'Deletion Notice – Docully Project '+str(l.dataroom_nameFront)+' has been Deleted', to = str(l.user.email), first_name = l.user.first_name,projectname=l.dataroom_nameFront)		
					TeamMembers.objects.filter(myteam_id=pk).delete()
					MyTeams.objects.filter(id=pk).delete()	
					return Response('Team deleted successfully', status=status.HTTP_201_CREATED)
				else:
					TeamMembers.objects.filter(myteam_id=pk).delete()
					MyTeams.objects.filter(id=pk).delete()	
					return Response('Team deleted successfully', status=status.HTTP_201_CREATED)

class Deletechanel(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, pk, format=None):
		if	MyTeams.objects.filter(chanel_id=pk).exists():
			teamdataaa=MyTeams.objects.filter(chanel_id=pk)
			for j in teamdataaa:
				if Dataroom.objects.filter(my_team_id=j.id).exists():
					plandata1=Dataroom.objects.filter(my_team_id=j.id)
					for l in plandata1:
						Dataroom.objects.filter(id=l.id).update(is_deleted=True,delete_at=datetime.now(),is_expired=True)
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=l.id).update(is_deleted=True,deleted_by_date=datetime.now(),is_deleted_permanent=True)
						if 	DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							# block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=l.id).exists():
							data=Vote.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=l.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)							
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf")	
						DataroomFolder.objects.filter(dataroom_id=l.id).delete()
						AllNotifications.objects.filter(dataroom_id=l.id).delete()
						Notifications.objects.filter(dataroom_id=l.id).delete()	
						Watermarking.objects.filter(dataroom_id=l.id).delete()
						pendinginvitations.objects.filter(dataroom_id=l.id).delete()
						DataroomGroups.objects.filter(dataroom_id=l.id).delete()
						DataroomMembers.objects.filter(dataroom_id=l.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=l.id).delete()
						Vote.objects.filter(dataroom_id=l.id).delete()						
						send_offlinedataroomdelete_email(subject= 'Deletion Notice – Docully Project '+str(l.dataroom_nameFront)+' has been Deleted', to = str(l.user.email), first_name = l.user.first_name,projectname=l.dataroom_nameFront)		
					TeamMembers.objects.filter(myteam_id=j.id).delete()
					MyTeams.objects.filter(id=j.id).delete()	
				else:
					TeamMembers.objects.filter(myteam_id=j.id).delete()
					MyTeams.objects.filter(id=j.id).delete()
		chanelMembers.objects.filter(chanel_id=pk).delete()
		Mychanels.objects.filter(id=pk).delete()		
		return Response('Channel deleted successfully', status=status.HTTP_201_CREATED)

class chanelteamView(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)
	

	def get(self, request, format=None):
		user = request.user
		my_team = []
		serializer1=[]
		if user.is_superadmin:
			my_team = Mychanels.objects.filter()
			serializer1 = MychanelsSerializer(my_team, many=True).data
			for i in serializer1:
				my_team = MyTeams.objects.filter(chanel_id = i['id'])
				i['teamdata'] = MyTeamsSerializer(my_team, many=True).data 

		else:   
			# if Mychanels.objects.filter(user_id=user.id).exists():
			# 	my_team = Mychanels.objects.filter(user_id=user.id)
			# 	serializer1 = MychanelsSerializer(my_team, many=True).data    
			print(user.id,'ppppp') 
			if chanelMembers.objects.filter(member_id=user.id).exists():                  
				print(user.id,'ppppp') 
				my_team_id = [my_team.chanel.id if my_team.chanel else -1   for my_team in chanelMembers.objects.filter(member_id=user.id)]
				my_team = Mychanels.objects.filter(id__in = my_team_id)
				serializer1 = MychanelsSerializer(my_team, many=True).data
				for i in serializer1:
					my_team = MyTeams.objects.filter(chanel_id = i['id'])
					i['teamdata'] = MyTeamsSerializer(my_team, many=True).data
		return Response(serializer1)

from userauth.models import *
from userauth.serializers import *
from .utils import storage_used
class silveronline(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user=request.user
		if user.is_superadmin:
			dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,dataroom__offlinedataroom=False,is_latest_invoice=True,plan__name__icontains='silver')
			serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
			serializerdata=storage_used(serializerdata)
			return Response(serializerdata,status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

class goldonline(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user=request.user

		if user.is_superadmin:
			dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,dataroom__offlinedataroom=False,is_latest_invoice=True,plan__name__icontains='gold')
			serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
			serializerdata=storage_used(serializerdata)

			return Response(serializerdata,status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

class platinumonline(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user=request.user

		if user.is_superadmin:
			dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,dataroom__offlinedataroom=False,is_latest_invoice=True,plan__name__icontains='platinum')
			serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
			serializerdata=storage_used(serializerdata)

			return Response(serializerdata,status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

class trialonline(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user=request.user

		if user.is_superadmin:
			dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,dataroom__offlinedataroom=False,is_latest_invoice=True,plan__name__icontains='trial')
			serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
			serializerdata=storage_used(serializerdata)

			return Response(serializerdata,status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

class directdeletedataroom(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, pk,format=None):
						import datetime
						Dataroom.objects.filter(id=pk).update(is_deleted=True,delete_at=datetime.datetime.now(),is_expired=True)
						l=Dataroom.objects.filter(id=pk).last()
						container_name ='docullycontainer'
						DataroomFolder.objects.filter(dataroom_id=l.id).update(is_deleted=True,deleted_by_date=datetime.datetime.now(),is_deleted_permanent=True)
						if 	DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).exists():
							filedata=DataroomFolder.objects.filter(dataroom_id=l.id,is_folder=False).last()
							file_name = str(filedata.path).split("/")[-2].replace("%20", " ")+"/"
							# block_blob_service = BlockBlobService(account_name='docullystorage', account_key='ddIGey4fa6zz/FnWjMgPm5zN35BgIEDsaY6K18dpTFpkqUAJRD6efPBpXZGdBG8ICnyWWE8Y/PPGZQ0ajUeZTw==',sas_token = sas_url)
							block_blob_service = BlockBlobService(account_name='newdocullystorage', account_key='qOUUYXZxll+/cVmanzs+riupuL5c19VdDD0egQD/KUA5VUssLYF/hM0TEPcHEKgaFAIEzyglVXY7+AStQZEEig==',sas_token = sas_url)
							blobs_list = block_blob_service.list_blobs(container_name,file_name)
							for blob in blobs_list:
								block_blob_service.delete_blob(container_name, blob.name, snapshot=None)
						if Vote.objects.filter(dataroom_id=l.id).exists():
							data=Vote.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.path.delete(save=True)						
						if DataroomDisclaimer.objects.filter(dataroom_id=l.id).exists():
							data=DataroomDisclaimer.objects.filter(dataroom_id=l.id)
							for i in data: 
								i.dataroom_disclaimer.delete(save=True)							
						if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf"):
							os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(l.id)+".pdf")					
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(l.id)+".pdf")	
							if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf"):
								os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(l.id)+".pdf")	
						DataroomFolder.objects.filter(dataroom_id=l.id).delete()
						AllNotifications.objects.filter(dataroom_id=l.id).delete()
						Notifications.objects.filter(dataroom_id=l.id).delete()	
						Watermarking.objects.filter(dataroom_id=l.id).delete()
						pendinginvitations.objects.filter(dataroom_id=l.id).delete()
						DataroomGroups.objects.filter(dataroom_id=l.id).delete()
						DataroomMembers.objects.filter(dataroom_id=l.id).delete()
						DataroomGroupPermission.objects.filter(dataroom_id=l.id).delete()
						Vote.objects.filter(dataroom_id=l.id).delete()						
						send_offlinedataroomdelete_email(subject= 'Deletion Notice – Docully Project '+str(l.dataroom_nameFront)+' has been Deleted', to = str(l.user.email), first_name = l.user.first_name,projectname=l.dataroom_nameFront)		
						return Response('Done',status=status.HTTP_201_CREATED)


class teamdeletiononline(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request,pk, format=None):
		user=request.user

		if user.is_superadmin:
			ddd=Dataroom.objects.filter(my_team_id=pk).last()
			print('----------------------hehehehehehe',ddd.is_deleted)
			if Dataroom.objects.filter(my_team_id=pk,is_deleted=False).exists():
				return Response('please delete dataroom inside team',status=status.HTTP_201_CREATED)
			else:
				MyTeams.objects.filter(id=pk).update(is_deleted=True)
				return Response('deleted',status=status.HTTP_201_CREATED)

		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)


class team_alluseronline(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, format=None):
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote
		from users_and_permission.models import DataroomMembers
		serializerdata=[]
		membercount=0
		print('00000',request.user.is_superadmin,request.GET.get('userFullName'))

		if request.user.is_superadmin:
				if request.GET.get('team')==None or request.GET.get('team')=='':
					team=MyTeams.objects.filter(onlinesubscriber=True)
				else:
					team=MyTeams.objects.filter(is_deleted=False,team_name__icontains=request.GET.get('team'),onlinesubscriber=True)
				print('00000',team.exists(),request.GET.get('userFullName'))

				if team.exists():
					print('222222')

					for myteamdata in team:
								if request.GET.get('dataroom')==None or request.GET.get('dataroom')=='':
									dataroomdata=Dataroom.objects.filter(my_team_id = myteamdata.id,is_deleted=False)
								else:
									dataroomdata=Dataroom.objects.filter(dataroom_nameFront__icontains=request.GET.get('dataroom'), my_team_id = myteamdata.id,is_deleted=False)
								# print(dataroomdata,'vvvvvvvv')
								print('1111',myteamdata.id,dataroomdata.exists())
								if dataroomdata:
									for k in dataroomdata:
										if request.GET.get('role')=='admin':
											dataroommembers=DataroomMembers.objects.filter(is_dataroom_admin=True,dataroom_id= k.id,is_deleted=False)
										elif request.GET.get('role')=='laadmin':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=True,dataroom_id = k.id,is_deleted=False)
										elif request.GET.get('role')=='enduser':
											dataroommembers=DataroomMembers.objects.filter(is_la_user=False,is_dataroom_admin=False,dataroom_id = k.id,is_deleted=False)
										else:
											dataroommembers=DataroomMembers.objects.filter(dataroom_id = k.id,is_deleted=False)
										if request.GET.get('userFullName')==None or request.GET.get('userFullName')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(Q(member__first_name__icontains=request.GET.get('userFullName')) | Q(member__last_name__icontains=request.GET.get('userFullName')))
										if request.GET.get('emailId')==None or request.GET.get('emailId')=='':
											pass
										else:
											dataroommembers=dataroommembers.filter(member__email__icontains=request.GET.get('emailId'))

										if dataroommembers:
											membercount=dataroommembers.count()
											dataroommembers = paginator.paginate_queryset(dataroommembers, request)

											for l in dataroommembers:
												if l.is_la_user:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'LA Admin'})
												elif l.is_dataroom_admin:
													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'Admin'})
												else:

													serializerdata.append({'id':l.id,'userfullname':str(l.member.first_name)+' '+str(l.member.last_name),'email':l.member.email,'team':myteamdata.team_name,'dataroomname':k.dataroom_nameFront,'role':'End User'})
										# else:
											# return Response({'data':['hi3']}, status=status.HTTP_201_CREATED)

								# else:
									# return Response({'data':['hi2']}, status=status.HTTP_201_CREATED)
					return Response({'data':serializerdata},status=status.HTTP_201_CREATED)

		else:
			return Response({'data':['hi1']}, status=status.HTTP_201_CREATED)

class myteamonline_dashboard(APIView):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get(self, request, format=None):
		from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
		from data_documents.models import DataroomFolder
		from Vote.models import Vote
		chanelcount=0
		serializerdata1=[]
		serializerdata={}

		if request.user.is_superadmin:
					data=planinvoiceuserwise.objects.filter(is_latest_invoice=True)
					dataroomdata=[ member.dataroom.dataroom_storage_allocated for member  in data]
					serializerdata['myteamscount']=data.count()
					serializerdata['dataroomcount']=data.count()
					serializerdata['dataroomstorage']=sum(dataroomdata)	
					serializerdata1.append(serializerdata)
					return Response({'data':serializerdata1}, status=status.HTTP_201_CREATED)

from .utils import *
class globalsearchteamdataroom(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request,pk, format=None):
		user=request.user
		if user.is_superadmin:
			dataroomdata=Dataroom.objects.filter(Q(my_team_id=pk,offlinedataroom=False,dataroom_nameFront__icontains=request.GET.get('key'),is_deleted=False) | Q(my_team_id=pk,offlinedataroom=False,id__icontains=request.GET.get('key')))
			dataroomserializerdataa=DataroomSerializer(dataroomdata,many=True).data
			if dataroomserializerdataa:
				dataroomserializerdataa=storage_usedfordataroom(dataroomserializerdataa)
			return Response({'dataroomdata':dataroomserializerdataa},status=status.HTTP_201_CREATED)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)


class globalsearchteamdataroomid(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user=request.user
		if user.is_superadmin:
			if request.GET.get('plan')=='':
				dataa=Dataroom.objects.filter(offlinedataroom=False).values('id')
				# serializerdata=MyTeamsSerializer(dataa,many=True).data
				dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,is_latest_invoice=True,dataroom_id__in=dataa,company_name__icontains=request.GET.get('key'))
				serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
				serializerdata=storage_used(serializerdata)
				serializerdata=calculatedeletedate(serializerdata)

				dataroomdata=Dataroom.objects.filter(Q(offlinedataroom=False,dataroom_nameFront__icontains=request.GET.get('key')) | Q(offlinedataroom=False,id__icontains=request.GET.get('key'))).values('id')
				dataroomdataa=planinvoiceuserwise.objects.filter(is_latest_invoice=True,dataroom_id__in=dataroomdata)
				dataroomserializerdata=planinvoiceuserwiseSerializer(dataroomdataa,many=True).data
				dataroomserializerdata=storage_used(dataroomserializerdata)
				dataroomserializerdata=calculatedeletedate(dataroomserializerdata)

				# dataroomserializerdataa=DataroomSerializer(dataroomdata,many=True).data
				# if dataroomserializerdataa:
				# 	dataroomserializerdataa=storage_usedfordataroom(dataroomserializerdataa)
				# 	serializerdata=storage_usedforteams(serializerdata)
				# 	print(dataroomserializerdataa,'llllllllllllllll')
				return Response({'myteamdata':serializerdata,'dataroomdata':dataroomserializerdata},status=status.HTTP_201_CREATED)
			else:
				dataa=Dataroom.objects.filter(offlinedataroom=False).values('id')
				# serializerdata=MyTeamsSerializer(dataa,many=True).data
				dataa=planinvoiceuserwise.objects.filter(dataroom__my_team__is_deleted=False,is_latest_invoice=True,dataroom_id__in=dataa,company_name__icontains=request.GET.get('key'))
				serializerdata=planinvoiceuserwiseSerializer(dataa,many=True).data
				serializerdata=storage_used(serializerdata)
				serializerdata=calculatedeletedate(serializerdata)


				dataroomdata=Dataroom.objects.filter(Q(offlinedataroom=False,dataroom_nameFront__icontains=request.GET.get('key')) | Q(offlinedataroom=False,id__icontains=request.GET.get('key'))).values('id')
				dataroomdataa=planinvoiceuserwise.objects.filter(is_latest_invoice=True,dataroom_id__in=dataroomdata,plan__name__icontains=request.GET.get('plan'))
				dataroomserializerdata=planinvoiceuserwiseSerializer(dataroomdataa,many=True).data
				dataroomserializerdata=storage_used(dataroomserializerdata)
				dataroomserializerdata=calculatedeletedate(dataroomserializerdata)

				# dataroomserializerdataa=DataroomSerializer(dataroomdata,many=True).data
				# if dataroomserializerdataa:
				# 	dataroomserializerdataa=storage_usedfordataroom(dataroomserializerdataa)
				# 	serializerdata=storage_usedforteams(serializerdata)
				# 	print(dataroomserializerdataa,'llllllllllllllll')
				return Response({'myteamdata':serializerdata,'dataroomdata':dataroomserializerdata},status=status.HTTP_201_CREATED)















				# plandata=planinvoiceuserwise.objects.filter(plan__name__icontains=request.GET.get('plan'),is_latest_invoice=True).values('dataroom_id')
				# dataroomids=Dataroom.objects.filter(id__in=plandata).values('my_team_id')
				# dataa=MyTeams.objects.filter(id__in=dataroomids, onlinesubscriber=True,team_name__icontains=request.GET.get('key'),is_deleted=False)
				# serializerdata=MyTeamsSerializer(dataa,many=True).data
				# dataroomdata=Dataroom.objects.filter(Q(id__in=plandata, offlinedataroom=False,dataroom_nameFront__icontains=request.GET.get('key'),is_deleted=False) | Q(id__in=plandata, offlinedataroom=False,id__icontains=request.GET.get('key'),is_deleted=False))
				# dataroomserializerdataa=DataroomSerializer(dataroomdata,many=True).data
				# if dataroomserializerdataa:
				# 	dataroomserializerdataa=storage_usedfordataroom(dataroomserializerdataa)
				# 	serializerdata=storage_usedforteams(serializerdata)
				# 	print(dataroomserializerdataa,'llllllllllllllll')
				# return Response({'myteamdata':serializerdata,'dataroomdata':dataroomserializerdataa},status=status.HTTP_201_CREATED)

		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
