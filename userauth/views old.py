from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import *
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework import status
# from oauth2_provider.models import *
from django.core.mail import EmailMessage, EmailMultiAlternatives
# from oauth2_provider.views.generic import ProtectedResourceView
from rest_framework import permissions, routers, serializers, viewsets
from rest_framework.parsers import JSONParser
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import requests
from rest_framework.response import Response
# from oauthlib.common import generate_token
from rest_framework import status
from datetime import datetime
from django.utils import timezone 
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.crypto import get_random_string
import datetime
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    ListCreateAPIView)
from django.template.loader import render_to_string
from dms.settings import *

from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FileUploadParser
from django.core.mail import send_mail
from random import randint
from myteams.models import MyTeams
from .serializers import UserSerializer, AccessHistorySerializer, InviteUserSerializer,subscriptionplanSerializer,plansfeatureSerializer,dvd_addon_plansSerializer,addon_plan_invoiceuserwiseSerializer
from . import constants, utils
from .models import Profile, AccessHistory, User, InviteUser,planinvoiceuserwise,subscriptionplan,plansfeature,telr_payment_cartids
from emailer import utils as emailer_utils
from emailer.models import SiteSettings
from users_and_permission.models import DataroomMembers
from dataroom.models import Dataroom, DataroomModules, DataroomOverview
from users_and_permission.serializers import DataroomMembersSerializer
import json

def ValidToken():
    import datetime
    from django.utils.timezone import utc
    user = User.objects.get(email__iexact='support@confiexdataroom.com')
    serializer = UserSerializer(user, many=False)
    if serializer.is_valid():
        token, created = Token.objects.get_or_create(user=user)

        utc_now = datetime.datetime.utcnow()    
        if not created and token.created < utc_now - datetime.timedelta(minutes=10):
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow()
            token.save()
        response_data = {'token': token.key}

        return response_data

    return False

class Register(APIView):
    serializers = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        data = JSONParser().parse(request)
        print("Dat----",data)
        data['username'] = data.get('email').lower()
        # print("Dat----",data)
        # {'first_name': 'yghk', 'last_name': 'gfhfk', 'email': 'd@gmail.com', 'phone': 'fdhgfj', 'company_name': 'cvnvm', 'country': 'vbmv,', 'project_name': 'cmbm', 'is_trial': False, 'dataroom_name': 'cmbm'}
        data["is_superadmin"] = False
        data["is_staff"] = False
        data["is_team"] = True
        data["is_subscriber"] = True


    
        serializer = UserSerializer(data=data)
        print("Is Valid",serializer.is_valid())
        print("Is Error",serializer.errors)
        if serializer.is_valid():
            serializer.save()
            token = get_random_string(length=100)
            user = User.objects.get(id = serializer.data.get('id'))
            user.is_subscriber = True 
            user.is_active = True 
            user.set_password(data.get('password'))
            user.save()

            profile = Profile.objects.get(user_id=serializer.data.get('id'))

            profile.user_id = user.id

            profile.reset_key = token

            profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")

            profile.save()

            constants.link="https://services.docully.com/projectName/"

            link = constants.link+"password_set/?token="+profile.reset_key


            utils.send_activation_email(subject= 'Activate & setup password for your Docully account', to =data.get('email').lower(), first_name = data.get('first_name'), link =link)

            if data.get('is_trial')==True:
                teams = MyTeams()
                teams.team_name = data.get('dataroom_name')+' Team'
                teams.dataroom_allowed = 1
                teams.dataroom_admin_allowed = 25
                teams.dataroom_storage_allowed = 1
                teams.team_created_by_id = user.id
                teams.user_id = user.id
                teams.start_date = datetime.date.today()
                teams.end_date = datetime.date.today() + datetime.timedelta(days=15)
                teams.save()

                dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
                dataroom = Dataroom()
                dataroom.dataroom_name = data.get('dataroom_name')
                dataroom.is_dataroom_on_live = True
                dataroom.dataroom_storage_allocated = 1
                dataroom.user = user
                dataroom.my_team_id = teams.id
                dataroom.dataroom_modules = dataroom_modules
                dataroom.save()
                User.objects.filter(id=user.id).update(is_trial=True)
                plansdata1=subscriptionplan.objects.filter(name__icontains='trial').last()
                obj1=planinvoiceuserwise()
                obj1.user_id=user.id
                obj1.plan_id=plansdata1.id
                obj1.dataroom_id=dataroom.id
                obj1.select_billing_term='15 days'
                obj1.customer_name=str(user.first_name)+str(user.last_name)
                obj1.company_name=user.company_name
                obj1.effective_price='0.00'
                obj1.total_fee='0.00'
                obj1.grand_total='0.00'
                obj1.payment_complete=True
                obj1.start_date=datetime.datetime.now()
                obj1.end_date=datetime.datetime.now()+timedelta(days=15)
                obj1.is_plan_active=True
                obj1.save()
                dataroom_member_data = {
                        'dataroom':dataroom.id, 
                        'member' :user.id, 
                        'member_type':1, 
                        'member_added_by':user.id,
                        'is_dataroom_admin':True
                    }
                DataroomMembers.objects.create(dataroom_id=dataroom.id, member_id=user.id, member_added_by_id=user.id, is_dataroom_admin=True)
                overview = DataroomOverview.objects.create(dataroom_id=dataroom.id, user_id=user.id)
                serializer.data['team_id'] = teams.id
                utils.send_trialperiod_email(subject= '15 Days free trial is successfully activated on Docully for '+str(data.get('dataroom_name')), to =data.get('email').lower(), first_name = data.get('first_name'), data =obj1,projectname=data.get('dataroom_name'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def activate(request, key):
    if request.method == 'GET':  
        # print ("api for activation called")
        # print ("priamry key is:",key)
        activation_expired = False
        already_active = False
        # print ("key is:", key)
        profile = get_object_or_404(Profile, activation_key=key)
        context = {}
        if profile.user.is_active == False:
            # print ("profile is not active")
            context["message"] = "Account is verified successfully"
            if timezone.now() > profile.key_expires:
                activation_expired = True
                id_user = profile.user.id
                # print ("profile is active")
                return render(request, 'account/account_activation_succcessfull.html', context)
            else:
                # print ("profile is already active")
                profile.user.is_active = True
                profile.user.save()
                # print ("profile state is successfully stored")
                return render(request, 'account/account_activation_succcessfull.html', context)
        else:
            context["message"] ="Account is already verified"
            return render(request, 'account/account_activation_succcessfull.html', context)

class CreatePasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        data = JSONParser().parse(request)
        username = data.get('user').lower()
        password = data.get('password')
        user = User.objects.filter(email=username).first()
        # print('user---',user)
        if user :
            user.set_password(password)
            user.save()
            user.is_reset_key_status = True
            user.save()
            msg = "Password reset successfully"
            return Response({'msg':msg}, status=status.HTTP_201_CREATED)
        return Response({'msg':'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        data = JSONParser().parse(request)
        # print("data----",data)
        username = data.get('user').lower()
        user = User.objects.filter(email=username).first()
        # print('user---',user)
        if user :
            token = get_random_string(length=100)
            profile = Profile()
            profile.user_id = user.id
            profile.reset_key = token
            profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
            profile.save()
            # print(constants.link,"constants.link")
            constants.link="https://services.docully.com/projectName/"
            link = constants.link+"password_reset/?token="+profile.reset_key
            # print(link,"link")
            # send_mail('[DMS] Please reset your password', 
            #     'Please go to the following page and choose a user email:\n'+link,
            #     'badgujarr007@gmail.com', [user.email], fail_silently=False)
            subject = "Reset your Docully password"
            subject = subject
            from_email = settings.EMAIL_HOST_USER
            # ctx = {
            #     'user': [user.first_name],
            #     'sender': 'badgujarr007@gmail.com', 
            #     'link':link
            # }
            # print(from_email)
            message = render_to_string('emailer/forgetpassword.html', {
                'user': user.first_name,
                # 'sender': 'badgujarr007@gmail.com', 
                'link':link
            })
            # message = get_template('emailer/forgetpassword.html').render(ctx)
            msg = EmailMessage(subject, message, to=[user.email], from_email=from_email)
            msg.content_subtype = 'html'
            msg.send(fail_silently=False)
            return Response({"error": False, 'result': "Congrats ! Email Successfully send. Please check your email."}, status=status.HTTP_201_CREATED)
        return Response({"error": True, 'result': "Please check your username. This username doesnt exist!!"}, status=status.HTTP_400_BAD_REQUEST)

def password_reset(request):
    # print("GET--",request.GET)
    token = request.GET.get('token')
    try:
        # print ("inside try block")
        # print ("TOken is", token)
        usr = Profile.objects.get(reset_key=token, is_reset_key_status=False)
        # print ("first name is", usr.user.first_name)
        # print ("last name is", usr.user.last_name)
        # print ("first name is", usr.user.email)
        
        return render(request, 'userauth/forgot_password.html', {'user': usr.user,'token':token})
    except:
        usr = None
    if usr != None:
        return render(request, 'userauth/forgot_password.html', {'user': usr.user,'token':token})
    else:
        msg = "Reset Password Link is Expired"
        return render(request, 'userauth/forgot_password.html', {'msg': msg, 'user': None})
    return render(request, 'userauth/forgot_password.html', {'user': usr.user,'token':token})

def password_reset_submit(request):
    token = request.POST.get('token')
    try:
        usr = Profile.objects.get(reset_key=token, is_reset_key_status=False)
        if usr :
            print ("user is exist")
    except:
        usr = None
    if request.method == 'POST':
        if usr != None:
            user = request.POST.get('username').lower()            
            password = request.POST.get('password')        
            confirm_password = request.POST.get('confirm_password')
            # print ("user1:-", user, "\n")
            if password == confirm_password:
                user =  User.objects.filter(email=user).first()
                user.set_password(password)
                user.save()
                usr.is_reset_key_status = True
                usr.save()
                msg = "Password reset successfully"
                return render(request, 'userauth/forgot_password_submit.html', {'msg': msg,'user': usr.user,'token':token})
            else:
                msg = "Password doesn't match the confirmation"
                return render(request, 'userauth/forgot_password.html', {'msg': msg,'user': usr.user,'token':token})
        else:
            msg = "Reset Password Link is Expired"
            return render(request, 'userauth/forgot_password.html', {'msg': msg})
    return render(request, 'userauth/forgot_password.html', {'user': usr.user,'token':token})

def password_set(request):
    # print("GET--",request.GET)
    token = request.GET.get('token')
    try:
        # print ("inside try block")
        # print ("TOken is", token)
        usr = Profile.objects.get(reset_key=token, is_reset_key_status=False)
        # print ("first name is", usr.user.first_name)
        # print ("last name is", usr.user.last_name)
        # print ("first name is", usr.user.email)
        
        return render(request, 'userauth/set_password.html', {'user': usr.user,'token':token})
    except:
        usr = None
    if usr != None:
        return render(request, 'userauth/set_password.html', {'user': usr.user,'token':token})
    else:
        msg = "Set Password Link is Expired"
        return render(request, 'userauth/set_password.html', {'msg': msg, 'user': None})
    return render(request, 'userauth/set_password.html', {'user': usr.user,'token':token})

def password_set_submit(request):
    token = request.POST.get('token')
    try:
        usr = Profile.objects.get(reset_key=token, is_reset_key_status=False)
        if usr :
            print ("user is exist")
    except:
        usr = None
    if request.method == 'POST':
        if usr != None:
            user = request.POST.get('username').lower()            
            password = request.POST.get('password')        
            confirm_password = request.POST.get('confirm_password')
            # print ("user1:-", user, "\n")
            if password == confirm_password:
                user =  User.objects.filter(email=user).first()
                user.set_password(password)
                user.save()
                usr.is_reset_key_status = True
                usr.save()
                msg = "Password set successfully"
                return render(request, 'userauth/set_password_submit.html', {'msg': msg,'user': usr.user,'token':token})
            else:
                msg = "Password doesn't match the confirmation"
                return render(request, 'userauth/set_password.html', {'msg': msg,'user': usr.user,'token':token})
        else:
            msg = "Set Password Link is Expired"
            return render(request, 'userauth/set_password.html', {'msg': msg})
    return render(request, 'userauth/set_password.html', {'user': usr.user,'token':token})


class AccountVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        username = request.data['username']
        otp = request.data['otp']
        user = User.objects.filter(username=username,).first()
        try:
            se = request.session['otp']
            if se == otp:
                user.is_active = True
                user.save()
                request.session.clear_expired()
            else:
                return Response({'error': False, 'result': 'Incorrect otp / expired otp.'})
        except:
            return Response({'error': False, 'result': 'Incorrect username / expired otp.'})

        return Response({"error": True, 'result': "Account verify successfully."})


class LoginView(APIView):
    # serializer_class = TokenSerializer
    # authentication_classes = [OAuth2Authentication]    
    permission_classes = [permissions.AllowAny]


    def createEntryInAccessHistory(self, user, request):
        # import datetime
        # request.session['email'] = user.email
        request.session['id'] = user.id
        ip = utils.get_client_ip(request)
        data = {'user': user.id,'logged_in_ip':ip, 
                'logged_in_time':timezone.now(), 'logged_out_time':timezone.now(), 
                'is_logged_in': True
                }

        return data

    # def get(self, request, format=None):
    #     """
    #     Return a Valid token if username and password
    #     is valid for a given client
    #     """
    #     # print("Data----",request.POST) 
    #     #print (request) 
    #     data = JSONParser().parse(request)
    #     print("Data----",data)
    #     username = data.get('username').lower()
    #     password = data.get('password')
    #     print ("Before authentication")
    #     user_count = User.objects.filter(email__iexact=username)
    #     print ("user count is ", user_count.count())
    #     if user_count.count() > 0:
    #         user = User.objects.get(email__iexact=username)
    #         print ("user is exist")
    #         if user is not None:
    #             is_user = user.check_password(password)
    #             print ("is_user status", is_user)
    #             print ("is_user active", user.is_active)
    #             if is_user:
    #                 if user.is_active:
    #                     # Correct password, and the user is marked "activaee"
    #                     print ("user is active")
    #                     login(request, user)
    #                     serializer = UserSerializer(user, many=False)
    #                     token, created = Token.objects.get_or_create(user=user)
    #                     token_data = {"token": token.key,"user":serializer.data}
    #                     data = self.createEntryInAccessHistory(user, request)
    #                     serializer = AccessHistorySerializer(data = data)                        
    #                     if serializer.is_valid():
    #                         serializer.save()
    #                         print(token_data)
    #                         return Response(token_data)
    #                 else:
    #                     return Response({'msg':'User is not active'}, status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                  print ("user is not activate")
    #                  return Response({'msg':'Incorrect username/password'}, status=status.HTTP_400_BAD_REQUEST)
    #         else :
    #             return Response({'msg':'User does not exist in the system'}, status=status.HTTP_400_BAD_REQUEST)
    #     else :
    #         print ("user does not exist")
    #         return Response({'msg':'User does not exist in the system'}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request, format=None):
        """
        Return a Valid token if username and password
        is valid for a given client
        """
        # print("Data----",request.POST) 
        #print (request) 
        data = JSONParser().parse(request)
        # print("Data----",data)
        username = data.get('username').lower()
        password = data.get('password')
        # print ("Before authentication")
        user_count = User.objects.filter(email__iexact=username)
        # print ("user count is ", user_count.count())
        if user_count.count() > 0:
            user = User.objects.get(email__iexact=username)
            user.is_active = True
            # print ("user is exist")
            if user is not None:
                is_user = user.check_password(password)
                # User.objects.filter(id=user.id).update(is_active=True)
                # print ("is_user status", is_user)
                # print ("is_user active", user.is_active)
                if is_user:
                    user.save()
                    if user.is_active:
                        # Correct password, and the user is marked "activaee"
                        print ("user is active")
                        request.session['email'] = user.email
                        request.session['id'] = user.id
                        login(request, user)
                        authenticate(email=username, password=password)
                        serializer = UserSerializer(user, many=False)
                        token, created = Token.objects.get_or_create(user=user)
                        token_data = {"token": token.key,"user":serializer.data}
                        data = self.createEntryInAccessHistory(user, request)
                        serializer = AccessHistorySerializer(data = data)                        
                        if serializer.is_valid():
                            serializer.save()
                            # print(token_data)
                            return Response(token_data)
                    else:
                        return Response({'msg':'User is not active'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                     # print ("user is not activate")
                     return Response({'msg':'Incorrect username/password'}, status=status.HTTP_400_BAD_REQUEST)
            else :
                return Response({'msg':'User does not exist in the system'}, status=status.HTTP_400_BAD_REQUEST)
        else :
            # print ("user does not exist")
            return Response({'msg':'User does not exist in the system'}, status=status.HTTP_400_BAD_REQUEST)
            

class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )    
    def get(self, request):
        # print(request.session)
        # print("logout user",request.user)
        username = request.user
        user = User.objects.filter(id=username.id)
        # print("logout id",username.id)
        # print("LogoutView",User.objects.filter(id=username.id).values())
        if user.exists():
            user.update(is_active=False)
        try:
            print(request.session['id'],"<=== check session values ===>",request.session['email'])
        except Exception as e:
            print("logout error",e)
        # username = request.user
        # user = User.objects.filter(email__iexact=username)
        # if user.exists():
        #     print("enter logout")
        #     user.update(is_active=False)

        # if 'email' in request.session:        
        #     del request.session['email']
        # if 'id' in request.session:
        #     del request.session['id']
        logout(request)


        # request.user.auth_token.delete()
        return Response({"error": False, 'result': "logged out successfully"})


class UserView(ListAPIView):
    serializer_class = UserSerializer

    def get(self, request, format=None):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


class CategoryUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, pk, format=None):
        user = request.user
        data = []
        ip = utils.get_client_ip(request)
        if user is not None:
            serializer = UserSerializer(user, many=False)
            cat = None
            d_mem = DataroomMembers.objects.filter(dataroom_id=pk, member_id=user.id).first()
            d_mem_serializer = DataroomMembersSerializer(d_mem, many=False)
            data.append({'cat': d_mem_serializer.data})
            # print("dataaaaaaaaaaaaa",data)
            # import pdb;pdb.set_trace();
            return Response(d_mem_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileDataroom(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, pk, format=None):
        user = request.user
        ip = utils.get_client_ip(request)
        if user is not None:
            serializer = UserSerializer(user, many=False)
            data = serializer.data
            try:
                member = DataroomMembers.objects.filter(member_id = user.id, dataroom_id=pk, is_deleted=False).first()
                data['member'] = DataroomMembersSerializer(member, many=False).data
            except:
                data['member'] = {}
                data['member']['is_la_user'] = False
                data['member']['is_end_user'] = False
                data['member']['is_dataroom_admin'] = False
                # status1=InviteUser.objects.filter(invitiation_sender=user.id,invitiation_receiver=member.member).values('is_invitation_accepted')
                # print('status---------------------------------',status1)
                # if status1 == True:
                #     data['member']['is_active'] = 'Active'
                # else:
                #     data['member']['is_active'] = 'InActive'


            return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        ip = utils.get_client_ip(request)
        tokenn=str(request.META.get('HTTP_AUTHORIZATION').replace('token ',''))
        # print(tokenn,'token dataaaaaaaaaaaaa')
        tokenn= Token.objects.get(key=tokenn)
        # print('Tokkkkkkkkkkkkkkkkkkkkkkkken',tokenn.user)
        user = User.objects.get(email=tokenn.user)


        if user is not None:
            serializer = UserSerializer(user, many=False)
            data = serializer.data
            data['avatar']=str(data['avatar'])+sas_url
            # print(data,'get api dattttttttttttttttaaaaaaaaaaaaaaaaaaaaa')

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        user = request.user
        ip = utils.get_client_ip(request)
        # print("dataaaaa", data)
        data['avatar'] = None
        serializer = UserSerializer(user, data=data)
        # print("serializer is valid", serializer.is_valid())
        # print("serializer is valid", serializer.errors)
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data,'post api dattttttttttttttttaaaaaaaaaaaaaaaaaaaaa')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Receive_email(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        data = request.data
        user = request.user
        receive_email = data["receive_email"]
        start_email_notification = data["receive_notification"]
        user_check = User.objects.filter(id=user.id)

        if user_check.exists():
            user_check.update(receive_email=receive_email,start_email_notification=start_email_notification)
            return Response({"success":"data saved"},status=status.HTTP_201_CREATED)
        else:
            return Response({"error":"User does not exists"},status=status.HTTP_400_BAD_REQUEST)
            # if receive_email and start_email_notification:
            #     print("both true")
            #     user_check.update(receive_email=True,start_email_notification=True)
            #     return Response({"success":"You will recieve daily mail and email notification"},status=status.HTTP_201_CREATED)
            # elif receive_email and start_email_notification is False:
            #     print("both false")
            #     user_check.update(receive_email=False,start_email_notification=False)
            #     return Response({"success":"You will not recieve daily mail and email notification"},status=status.HTTP_201_CREATED)
            # elif start_email_notification is False:
            #     print("third")
            #     user_check.update(start_email_notification=False)
            #     return Response({"success":"You will not recieve email notification"},status=status.HTTP_201_CREATED)
            # else:
            #     user_check.update(receive_email=False)
            #     return Response({"success":"You will not recieve daily mail"},status=status.HTTP_201_CREATED)


class ChangePassword(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        data = request.data
        user = request.user
        new_user = user.check_password(data["current_password"])
        if new_user:
            if((data["confirm_new_password"] == data["new_password"])):
                ip = utils.get_client_ip(request)
                user.set_password(data["new_password"])
                user.save()
                return Response({"success": "password successfully changed !!"} , status=status.HTTP_201_CREATED)
            return Response({"error":"New password and Confirm password didn't mached !"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"Incorrect current password!"}, status=status.HTTP_400_BAD_REQUEST)
 

class AccessHistoryApi(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        access_histories = AccessHistory.objects.filter(user_id=user.id).order_by('-logged_in_time')[:10]
        serializers = AccessHistorySerializer(access_histories, many=True)
        # print("serializers",serializers.data) 
        return Response(serializers.data)

class inactivesessiondelete(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def get(self, request, format=None):
        from django.contrib.sessions.models import Session

        for s in Session.objects.all():
            data = s.get_decoded()
            if data.get('_auth_user_id', None) == request.user.id:
                s.delete()
        return Response('Done')

class UploadProfilePic(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        user = request.user
        profile_pics = request.FILES.getlist('file')
        user.avatar.delete(save=True)
        user.avatar = profile_pics[0]
        user.save() 
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class CreateUserFromSuperAdmin(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        #access_histories = AccessHistory.objects.filter(user_id=user.id).order_by('-logged_in_time')[:10]
        users = User.objects.filter(is_admin=True)
        serializers = UserSerializer(users, many=True) 
        # print ("serializersd data", serializers.data)
        return Response(serializers.data)


    def post(self, request, format=None):
        data = request.data
        all_data = data.get("user")
        user = request.user
        # print ("new data is", data)
        already_exist_email = []
        invitation_send_email = []
        for data in all_data :
            # print ("data", data)
            is_user = User.objects.filter(email__iexact=data.get("email").lower()).exists()
            #step1
            """ create new user if user is exist then throw the error and infom admin with that email already exist and send invitation email"""
            if is_user == False:
                data['password'] = "Password1#"
                data['is_admin'] = True
                data['is_active'] = True
                serializer = UserSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    # If user is saved then make the entry inside InviteUser page
                    
                    unique_id = get_random_string(length=400)
                    link = constants.link+"invitation_link/"+unique_id
                    new_data = {
                        'invitiation_sender':user.id, 
                        'invitiation_receiver':serializer.data.get("id"), 
                        'invitation_status':3, 
                        'is_invitation_expired':False, 
                        'invitation_link':link, 
                        'invitation_token':unique_id , 
                        'dataroom_invitation': 0
                    }

                    invite_user_serializer = InviteUserSerializer(data=new_data)     
                    if invite_user_serializer.is_valid():
                        invite_user_serializer.save()
                        emailer_utils.send_invitation_account_email(serializer.data, new_data)
                        invitation_send_email.append(data);
                    else:
                        print ("erorr in storing invite_user_serializer information")
            else:
                already_exist_email.append(data.get('email'))
                # print ("User is aleardy exist")
        # send invitation email at once
        # print ("already exist user", already_exist_email)
        # print ("invitation_send_email", invitation_send_email)
        
        return Response({"message":"Invitation is successfully send" , 'already_exist_user':already_exist_email, 'invitation_send_email':invitation_send_email}, status=status.HTTP_201_CREATED)



def invitation_link(request, key):
    if request.method == 'GET':  
        # print ("api for activation called")
        # print ("priamry key is:",key)
        invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=False).exists()
        # print ("invite user",invite_user)
        context = {}
        msg = "User with this Invitation link does not exist"
        if invite_user != False:
            # print ("User is exist ")
            invite_user = InviteUser.objects.get(invitation_token=key, is_invitation_expired=False, is_invitation_accepted=False)
            # print ("invite_user.invitiation_receiver", invite_user.invitiation_receiver)
            try :
                invitee_member = User.objects.get(id=invite_user.invitiation_receiver.id)
                invitation_sender = User.objects.get(id=invite_user.invitiation_sender.id)
                site_setting = SiteSettings.objects.get(id=1)
                context["invitee_member"] = invitee_member
                context["invitation_sender"] = invitation_sender
                context["site_setting"] = site_setting
                return render(request, 'userauth/invitation_welcome.html', context)
            except UserDoesNotExist:
                # print ("User Does Not exit")
                return False
        else:
            invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=True, is_invitation_accepted=False).exists()
            if invite_user !=False:
                msg = "Inviatation is already expired"
                context["message"] = msg
                return render(request, 'userauth/invitation_error.html', context)
            else:
                invite_user = InviteUser.objects.filter(invitation_token__iexact=key).exists()
                if invite_user != False:                    
                    invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=True).exists()
                    if invite_user != False:
                        msg = "Invitation is already accepted"
                        # print ("Invitation is already accepted")
                        context["message"] = msg 
                        return render(request, 'userauth/invitation_error.html', context)

                    else:
                        msg = "Inviatation with this link does not exist"
                        # print ("Inviatation with this link does not exist")
                        return False
                else :
                    msg = "Inviatation with this link does not exist"
                    return False
        context["message"] = msg
        return render(request, 'userauth/invitation_error.html', context)


def invitation_link_admin(request, key):
    if request.method == 'GET':
        # print("request",dir(request))
        # try:
        #     print("==== user",request.user)
        #     print(" try this invitation id",dir(request.session))
        #     print("values",request.session.values())
        #     print("---",request.session.session_key())

        # except Exception as e:
        #     print("this invitation id error",e)

        # return HttpResponse("ok")
        # print ("api for activation called")
        # print ("priamry key is:",key)

        user_exist = request.GET.get("user_exist")
        invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=False).exists()
        # print ("invite user",invite_user)
        context = {}
        msg = "User with this Invitation link does not exist"
        if invite_user != False:
            # print ("User is exist ")
            invite_user = InviteUser.objects.get(invitation_token=key, is_invitation_expired=False, is_invitation_accepted=False)
            # print ("invite_user.invitiation_receiver", invite_user.invitiation_receiver)
            try :
                invitee_member = User.objects.get(id=invite_user.invitiation_receiver.id)
                invitation_sender = User.objects.get(id=invite_user.invitiation_sender.id)
                site_setting = SiteSettings.objects.get(id=1)
                context["invitee_member"] = invitee_member
                context["invitation_sender"] = invitation_sender
                context["site_setting"] = site_setting
                context["user_exist"] = user_exist
                # print('coming here 34343434')
                invite_user.is_invitation_accepted=True
                invite_user.invitatation_acceptance_date=datetime.datetime.now()
                invite_user.save()
                # InviteUser.objects.(invitation_token=key).update(is_invitation_accepted=True,invitatation_acceptance_date =datetime.datetime.now())
                user = User.objects.filter(id=invite_user.invitiation_receiver.id,is_active=True)
                if user.exists():
                    return redirect("https://services.docully.com/#/dashboard")
                else:
                    return render(request, 'userauth/admin_invitation_welcome.html', context)
            except UserDoesNotExist:
                # print ("User Does Not exit")
                return False
        else:
            invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=True, is_invitation_accepted=False).exists()
            if invite_user !=False:
                msg = "Invitation is already expired"
                context["message"] = msg
                return render(request, 'userauth/admin_invitation_error.html', context)
            else:
                invite_user = InviteUser.objects.filter(invitation_token__iexact=key).exists()
                if invite_user != False:                    
                    invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=True).exists()
                    if invite_user != False:
                        msg = "Invitation is already accepted"
                        # print ("Invitation is already accepted")
                        context["message"] = msg 
                        return render(request, 'userauth/admin_invitation_error.html', context)

                    else:
                        msg = "Inviatation with this link does not exist"
                        # print ("Inviatation with this link does not exist")
                        return False
                else :
                    msg = "Inviatation with this link does not exist"
                    return False
        context["message"] = msg
        return render(request, 'userauth/admin_invitation_error.html', context)


def invitation_welcome_login(request):
    if request.method == 'POST':
        invitee_member = request.POST["invitee_member"]
        invitation_sender = request.POST["invitation_sender"]
        invitee_member = User.objects.get(id=invitee_member)
        invitation_sender = User.objects.get(id=invitation_sender)
        context = {
        'invitee_member':invitee_member,
        'invitation_sender':invitation_sender
        }
        request.session["invitee_member"] = invitee_member.id
        return render(request, 'userauth/invitation_welcome_login.html', context)

def invitation_welcome_login_success(request):
    if request.method == 'POST':
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"].lower()
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        context = {}
        if password == confirm_password:
            invitee_member = request.session.get("invitee_member")
            data = {
                'first_name':first_name,
                'last_name': last_name, 
                'email' : email, 
                'password':password, 
                'username': email 
            }
            #step 1 : 
            #update the user information as well as password 
            user = User.objects.get(id=invitee_member)
            invitee_member_serializer = UserSerializer(user, data)
            # print ("invitee_member_serializer is valid", invitee_member_serializer.is_valid())
            # print ("invitee_member_serializer errors", invitee_member_serializer.errors)
            
            if invitee_member_serializer.is_valid():
                invitee_member_serializer.save()
                # set user password here and activate the user and set the user as admin
                user.is_active = True
                user.is_end_user = True
                user.set_password(password)
                user.save()
                # print ("invite member serializer data", invitee_member_serializer.data)                
                #step2:
                #change the membership status to pending to verified  
                #as well as change the status
                # print ("invitee_member", invitee_member)
                invite_user = InviteUser.objects.filter(invitiation_receiver_id=invitee_member).update(invitation_status=3, is_invitation_accepted=True, is_invitation_expired=False)
                # print ("password and confirm password matched")
                # print ('invite_user count', invite_user)
                context["msg"] = "Account is successfully created"
                return render(request, 'userauth/invitation_welcome_message.html', context)
        else :
            invitee_member = request.session.get("invitee_member")
            # print ("invitee_member", invitee_member)
            context["msg"] = "password and confirm password wrong !"
            context["invitee_member"] = User.objects.get(id=invitee_member)
            return render(request, 'userauth/invitation_welcome_login.html', context)



def admin_invitation_welcome_login(request):
    if request.method == 'POST':
        invitee_member = request.POST["invitee_member"]
        invitation_sender = request.POST["invitation_sender"]
        invitee_member = User.objects.get(id=invitee_member)
        invitation_sender = User.objects.get(id=invitation_sender)
        context = {
        'invitee_member':invitee_member,
        'invitation_sender':invitation_sender
        }
        request.session["invitee_member"] = invitee_member.id
        return render(request, 'userauth/invitation_welcome_login.html', context)

def admin_invitation_welcome_login_success(request):
    if request.method == 'POST':
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"].lower()
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        context = {}
        if password == confirm_password:
            invitee_member = request.session.get("invitee_member")
            data = {
                'first_name':first_name,
                'last_name': last_name, 
                'email' : email, 
                'password':password, 
                'username': email 
            }
            #step 1 : 
            #update the user information as well as password 
            user = User.objects.get(id=invitee_member)
            invitee_member_serializer = UserSerializer(user, data)
            # print ("invitee_member_serializer is valid", invitee_member_serializer.is_valid())
            # print ("invitee_member_serializer errors", invitee_member_serializer.errors)
            
            if invitee_member_serializer.is_valid():
                invitee_member_serializer.save()
                # set user password here and activate the user and set the user as admin
                user.is_active = True
                user.is_admin = True
                user.set_password(password)
                user.save()
                # print ("invite member serializer data", invitee_member_serializer.data)                
                #step2:
                #change the membership status to pending to verified  
                #as well as change the status
                # print ("invitee_member", invitee_member)
                invite_user = InviteUser.objects.filter(invitiation_receiver_id=invitee_member).update(invitation_status=3, is_invitation_accepted=True, is_invitation_expired=False)
                # print ("password and confirm password matched")
                # print ('invite_user count', invite_user)
                context["msg"] = "Account is successfully created"
                return render(request, 'userauth/invitation_welcome_message.html', context)
        else :
            invitee_member = request.session.get("invitee_member")
            # print ("invitee_member", invitee_member)
            context["msg"] = "password and confirm password wrong !"
            context["invitee_member"] = User.objects.get(id=invitee_member)
            return render(request, 'userauth/invitation_welcome_login.html', context)


class registeremailcheck(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        useremail=request.GET.get('email').lower()
        if User.objects.filter(email=useremail).exists():
            return Response(False)
        else:
            return Response(True)    

class plan_subscription(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request,format=None):
                    user=request.user
                    data=request.data 
                    print(data,user.id,'this data')
                    plandataa=subscriptionplan.objects.get(id=data.get('pid'))
                    cart_id_obj=telr_payment_cartids()
                    cart_id_obj.user_id=user.id
                    cart_id_obj.is_new_plan=True
                    cart_id_obj.save()
                    if data.get('billing_country')=='UAE':
                            tottalfee=int(plandataa.cost)
                            discountedprice= int(plandataa.cost)*5/100
                            gtotal=int(plandataa.cost)+ discountedprice
                            countryt=data.get('billing_country')
                    else:
                            countryt=data.get('others')
                            gtotal=int(plandataa.cost)
                    if gtotal==data.get('grand_total'):
                            obj=planinvoiceuserwise()
                            obj.user_id=user.id  
                            obj.is_latest_invoice=False
                            obj.save()   
                            tempidd=int(obj.id)+2111-7
                            url = 'https://secure.telr.com/gateway/order.json/'
                            if data.get('upgradeplanflag')=='True':
                                payload = {'ivp_method':'create','ivp_store':'22607','ivp_authkey':'TpxX@5MgLV#ZzWJL','ivp_amount':data.get('grand_total'),'ivp_currency':'USD','ivp_test':'1','ivp_cart':cart_id_obj.id,'ivp_desc':'New Plan Purchased, Plan name:'+str(plandataa.name),'return_auth':'https://services.docully.com/projectName/newplan_process/'+str(tempidd)+'/','return_decl':'https://services.docully.com/#/paycancel','return_can':'https://services.docully.com/#/paycancel'}
                            else:
                                payload = {'ivp_method':'create','ivp_store':'22607','ivp_authkey':'TpxX@5MgLV#ZzWJL','ivp_amount':data.get('grand_total'),'ivp_currency':'USD','ivp_test':'1','ivp_cart':cart_id_obj.id,'ivp_desc':'New Plan Purchased, Plan name:'+str(plandataa.name),'return_auth':'https://services.docully.com/projectName/newplan_process/'+str(tempidd)+'/','return_decl':'https://docully.com/#/paycancel','return_can':'https://docully.com/#/paycancel'}
                            response = requests.post(url, data = payload)
                            
                            if response.status_code == 200:
                                telrdata=response.json()
                                obj=planinvoiceuserwise.objects.get(id=obj.id)
                                obj.user_id=user.id
                                obj.vat=data.get('vat_detail')
                                obj.grand_total=data.get('grand_total')
                                obj.billing_address=data.get('billing_address')
                                obj.billing_city=data.get('billing_city')
                                obj.billing_state=data.get('billing_state')
                                obj.billing_country=countryt
                                obj.company_name=data.get('company_name')
                                obj.po_box=data.get('po_box')
                                obj.total_fee=data.get('Total_fee')
                                obj.select_billing_term=data.get('Billing_freq')
                                obj.plan_id=data.get('pid')
                                obj.project_name=data.get('dataroom_name')
                                # obj.is_plan_active=True
                                obj.is_latest_invoice=False
                                if data.get('upgradeplanflag')=='True':
                                    oldplandata=planinvoiceuserwise.objects.filter(user_id=user.id,id=data.get('oldplanid')).first()
                                    obj.dataroom_id=oldplandata.dataroom.id
                                    planinvoiceuserwise.objects.filter(user_id=user.id,id=data.get('oldplanid')).update(is_plan_upgraded=True)
                                if 'trial' in plandataa.name.lower():
                                    if user.is_trial==False:
                                        teams = MyTeams()
                                        teams.team_name = 'My Team'
                                        teams.dataroom_allowed = 1
                                        teams.dataroom_admin_allowed = 25
                                        teams.dataroom_storage_allowed = int(plandataa.storage)
                                        teams.team_created_by_id = user.id
                                        teams.user_id = user.id
                                        teams.start_date = datetime.date.today()
                                        obj.start_date=datetime.datetime.now()
                                        teams.end_date = datetime.date.today() + datetime.timedelta(days=15)
                                        obj.end_date=datetime.datetime.now() + datetime.timedelta(days=15)
                                        teams.save()
                                        dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
                                        dataroom = Dataroom()
                                        dataroom.dataroom_name = data.get('dataroom_name')
                                        dataroom.is_dataroom_on_live = False
                                        dataroom.dataroom_storage_allocated = int(plandataa.storage)
                                        dataroom.user = user
                                        dataroom.my_team_id = teams.id
                                        dataroom.dataroom_modules = dataroom_modules
                                        dataroom.is_paid=False
                                        dataroom.trial_expiry_date=datetime.datetime.now() + datetime.timedelta(days=15)
                                        dataroom.save()
                                        obj.dataroom_id=dataroom.id
                                        dataroom_member_data = {
                                                        'dataroom':dataroom.id, 
                                                        'member' :user.id, 
                                                        'member_type':1, 
                                                        'member_added_by':user.id,
                                                        'is_dataroom_admin':True
                                                    }
                                        DataroomMembers.objects.create(dataroom_id=dataroom.id, member_id=user.id, member_added_by_id=user.id, is_dataroom_admin=True,memberactivestatus=True)
                                        overview = DataroomOverview.objects.create(dataroom_id=dataroom.id, user_id=user.id)
                                        obj.save()
                                        telr_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                        utils.send_trialperiod_email(subject= '15 Days free trial is successfully activated on Docully for '+str(data.get('dataroom_name')), to =user.email.lower(), first_name = user.first_name, data =obj,projectname=data.get('dataroom_name'))
                                        utils.send_mail_to_superadmin(subject= 'User Activity- Free Trial #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,projectname=data.get('dataroom_name'))
                                        User.objects.filter(id=user.id).update(is_trial=True)
                                        if data.get('company_name') is not None or False:
                                            User.objects.filter(id=user.id).update(company_name=data.get('company_name'))
                                        return Response('https://docully.com/#/payment-successful', status=status.HTTP_201_CREATED)                                    
                                    else:
                                        return Response('Already Used Trial', status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    obj.save()
                                    telr_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                    return Response(telrdata['order']['url'], status=status.HTTP_201_CREATED)                                    
                            else:
                                return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)


                             
                    else:
                        return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        user=request.user       
        data=planinvoiceuserwise.objects.filter(user_id=user.id,is_latest_invoice=True)
        dataa=planinvoiceuserwiseSerializer(data,many=True)

        return Response(dataa.data,status=status.HTTP_201_CREATED)


class payment_api(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request,pk,format=None):
        pk=int(pk)+7-2111
        userinvoicedata=planinvoiceuserwise.objects.get(id=pk)
        plandataa=subscriptionplan.objects.filter(id=userinvoicedata.plan.id).first()
        user=User.objects.get(id=userinvoicedata.user.id)

        teams = MyTeams()
        teams.team_name = 'My Team'
        teams.dataroom_allowed = 1
        teams.dataroom_admin_allowed = 25
        teams.dataroom_storage_allowed = int(plandataa.storage)
        teams.team_created_by_id = user.id
        teams.user_id = user.id
        teams.start_date = datetime.date.today()
        userinvoicedata.start_date=datetime.datetime.now()
        userinvoicedata.is_latest_invoice=True
        userinvoicedata.is_plan_active=True
        userinvoicedata.auto_renewal=True
        userinvoicedata.payment_complete=True
        userinvoicedata.payment_option='online'
        if plandataa.term.lower()=='monthly':
            teams.end_date = datetime.date.today() + datetime.timedelta(days=30)
            userinvoicedata.end_date=datetime.datetime.now() + datetime.timedelta(days=30)
        elif plandataa.term.lower()=='quarterly':
            teams.end_date = datetime.date.today() + datetime.timedelta(days=90)
            userinvoicedata.end_date=datetime.datetime.now() + datetime.timedelta(days=90)
        elif plandataa.term.lower()=='annually' or plandataa.term.lower()=='yearly':
            teams.end_date = datetime.date.today() + datetime.timedelta(days=365)
            userinvoicedata.end_date=datetime.datetime.now() + datetime.timedelta(days=365)
        rflag=0
        if userinvoicedata.dataroom is not None or userinvoicedata.dataroom=='null':
            if Dataroom.objects.filter(id=userinvoicedata.dataroom.id).exists():
                planinvoiceuserwise.objects.filter(user_id=user.id,dataroom_id=userinvoicedata.dataroom.id).exclude(id=userinvoicedata.id).update(is_plan_upgraded=True,is_plan_active=False,auto_renewal=False,is_latest_invoice=False)
                Dataroom.objects.filter(id=userinvoicedata.dataroom.id).update(dataroom_storage_allocated=int(plandataa.storage),dataroom_nameFront=userinvoicedata.project_name,is_paid=True)
                dataroom=Dataroom.objects.filter(id=userinvoicedata.dataroom.id).first()       
                rflag=1 
        else:
            teams.save()
            dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
            dataroom = Dataroom()
            dataroom.dataroom_name = userinvoicedata.project_name
            dataroom.is_dataroom_on_live = False
            dataroom.dataroom_storage_allocated = int(plandataa.storage)
            dataroom.user = user
            dataroom.my_team_id = teams.id
            dataroom.dataroom_modules = dataroom_modules
            dataroom.is_paid=True
            dataroom.save()
            userinvoicedata.dataroom_id=dataroom.id
            dataroom_member_data = {
                        'dataroom':dataroom.id, 
                        'member' :user.id, 
                        'member_type':1, 
                        'member_added_by':user.id,
                        'is_dataroom_admin':True
                                    }
            DataroomMembers.objects.create(dataroom_id=dataroom.id, member_id=user.id, member_added_by_id=user.id, is_dataroom_admin=True,memberactivestatus=True)
            overview = DataroomOverview.objects.create(dataroom_id=dataroom.id, user_id=user.id)
        userinvoicedata.save()
        utils.send_subscription_email(subject= 'Your Docully Subscription - Activated', to =user.email.lower(), first_name = user.first_name, data =userinvoicedata,projectname=userinvoicedata.project_name)
        utils.send_mail_to_superadmin(subject= 'User Activity- Paid subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =userinvoicedata,projectname=userinvoicedata.project_name)                    
        User.objects.filter(id=user.id).update(paid_subscription=True)
        if userinvoicedata.company_name is not None or False:
                User.objects.filter(id=user.id).update(company_name=userinvoicedata.company_name)
        telr_payment_cartids.objects.filter(new_plan_id=userinvoicedata.id).update(is_new_plan=True,new_plan_id=userinvoicedata.id,is_payment_done=True) 
        if rflag==1:
            return redirect('https://services.docully.com/#/paysuccess', status=status.HTTP_201_CREATED)
        else:
            return redirect('https://docully.com/#/payment-successful', status=status.HTTP_201_CREATED)

class GetSinglePlan(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request, pk,format=None):
        print(request.data,"the value of pk",pk)
        data = list(subscriptionplan.objects.filter(id=pk,planstatus=True).values())
        # serializer_data = subscriptionplanSerializer(data,many=False).data
        return Response(data)

class Singleusersubsubscription(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request, pk,format=None):
        user=request.user       
        data=planinvoiceuserwise.objects.get(id=pk)
        if data.user.id==user.id:
            dataa=planinvoiceuserwiseSerializer(data,many=False)
            return Response(dataa.data,status=status.HTTP_201_CREATED)
        else:
            return Response('Something went wrong',status=status.HTTP_400_BAD_REQUEST)


def checksessionvaluehere(request):
    print("plan session",request.session['plan_selected'])
    return True





class MaintainPlanSession(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self,request,format=None):
        user = request.user
        data = {
        "user":user.id,
        "selected_plan":request.data
        }
        request.session["user"] = user.id
        request.session['plan_selected'] = data
        checksessionvaluehere(request)
        return Response({"data":"success"})


class GetPlanForBilling(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk,format=None):
        try:
            print(request.session.get('plan_selected'),"user id for checking",pk)
            print(request.session["user"])
            print(request.session.values())
            # data = request.session['plan_selected']
            # print("see",data)
            # plan = data["selected_plan"]
            # plandata = list(subscriptionplan.objects.filter(id=plan,planstatus=True).values())
            return Response({"data":"Your plan has been selected"},status=status.HTTP_201_CREATED)
        except Exception as e:
            print("value of e",e)
            return Response({"data":"Your plan has not been selected"},status=status.HTTP_400_BAD_REQUEST)




class plandetails(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        data=subscriptionplan.objects.filter(planstatus=True)
        dataa=subscriptionplanSerializer(data,many=True)
        return Response(dataa.data)

class featuredetails(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        data=plansfeature.objects.filter()
        dataa=plansfeatureSerializer(data,many=True)
        return Response(dataa.data)

class userplandetails(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).exists():
            data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).first()
            dataa=planinvoiceuserwiseSerializer(data,many=False)
            data11=dataa.data
            if 'trial' in data.plan.name.lower() or data.cancel_at_monthend==True:
                data11['auto_renewal_date']=''
            else:
                data11['auto_renewal_date']=data.end_date + datetime.timedelta(days=1)
                dateobject=datetime.datetime.strptime(str(data11['auto_renewal_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                data11['auto_renewal_date']=dateobject.strftime("%d/%m/%Y")
            data11['s_addoncount']=len(data.addon_plans.all())
            data11['d_addoncount']=len(data.dvd_addon_plans.all())
            dateobject=datetime.datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['created_date']=dateobject.strftime("%d/%m/%Y")
            dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['start_date']=dateobject.strftime("%d/%m/%Y")
            dateobject=datetime.datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['end_date']=dateobject.strftime("%d/%m/%Y")

            return Response(data11,status=status.HTTP_201_CREATED)
        else:
            return Response('false',status=status.HTTP_400_BAD_REQUEST)


class userplandetails_new(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,is_latest_invoice=True).exists():
            data=planinvoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,is_latest_invoice=True).first()            
            dataa=planinvoiceuserwiseSerializer(data,many=False)
            data11=dataa.data
            if 'trial' in data.plan.name.lower() or data.cancel_at_monthend==True:
                data11['auto_renewal_date']=''
            else:
                data11['auto_renewal_date']=data.end_date + datetime.timedelta(days=1)
                dateobject=datetime.datetime.strptime(str(data11['auto_renewal_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                data11['auto_renewal_date']=dateobject.strftime("%d/%m/%Y")            
            data11['s_addoncount']=len(data.addon_plans.all())
            data11['d_addoncount']=len(data.dvd_addon_plans.all())
            dateobject=datetime.datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['created_date']=dateobject.strftime("%d/%m/%Y")
            dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['start_date']=dateobject.strftime("%d/%m/%Y")
            dateobject=datetime.datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['end_date']=dateobject.strftime("%d/%m/%Y")
            
            return Response(data11,status=status.HTTP_201_CREATED)

        else:

            return Response('false',status=status.HTTP_400_BAD_REQUEST)

class addon_dvd_post(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def post(self, request,pk, format=None):
        user=request.user
        data=request.data 
        # pk=data.get('pid')
        cart_id_obj=telr_payment_cartids()
        cart_id_obj.user_id=user.id
        cart_id_obj.is_DVD_addon=True
        cart_id_obj.save()

        tempidd=pk
        url = 'https://secure.telr.com/gateway/order.json/'
        payload = {'ivp_method':'create','ivp_store':'22607','ivp_authkey':'TpxX@5MgLV#ZzWJL','ivp_amount':data.get('total_cost'),'ivp_currency':'USD','ivp_test':'1','ivp_cart':cart_id_obj.id,'ivp_desc':'DVD Request, Quantity-'+str(data.get('dvd_quantity')),'return_auth':'https://services.docully.com/projectName/dvd_addon_pay/?planid='+str(pk)+'&cartid='+str(cart_id_obj.id)+'&quant='+str(data.get('dvd_quantity'))+'&amount='+str(data.get('total_cost')),'return_decl':'https://services.docully.com/#/paycancel','return_can':'https://services.docully.com/#/paycancel'}
        response = requests.post(url, data = payload)
        if response.status_code == 200:
            telrdata=response.json()
            telr_payment_cartids.objects.filter(id=cart_id_obj.id).update(telr_ref_id=telrdata['order']['ref'])
            return Response(telrdata['order']['url'], status=status.HTTP_201_CREATED)                                    



        obj=dvd_addon_invoiceuserwise()
        obj.user_id=user.id
        obj.dvd_addon_plan_id=dvd_addon_plans.objects.filter().first().id
        obj.dataroom_id=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first().dataroom.id
        obj.quantity=int(data.get('dvd_quantity'))
        obj.total_cost=int(data.get('total_cost'))
        obj.save()

        plandata1=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        plandata1.dvd_addon_plans.add(obj)
        plandata1.save()

        data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        dataa=planinvoiceuserwiseSerializer(data,many=False)
        utils.dvd_addon_request(subject= 'Data DVD request', to =user.email.lower(), first_name = user.first_name, data =obj)
 
        return Response(dataa.data)


class userplanredirectionflag(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user=request.user
        current_time=datetime.now()
        planinvoiceuserwise.objects.filter(user_id=user.id,end_date__lt=current_time).update(is_plan_active=False)
        if planinvoiceuserwise.objects.filter(user_id=user.id,is_plan_active=True).exist():
            flagtoredirect=False
        else:
            flagtoredirect=True
        return Response(flagtoredirect,status=status.HTTP_201_CREATED)

class getusercurrentplan(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    # permission_classes = [permissions.AllowAny]

    def get(self,request,pk):
        user = request.user
        # bought_plan = planinvoiceuserwise.objects.filter(user_id=user.id,payment_complete=True).first()
        bought_plan = planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        if bought_plan:
            upgrade_plan_data = subscriptionplan.objects.filter(cost__gt=bought_plan.plan.cost)
            result_data = subscriptionplanSerializer(upgrade_plan_data,many=True).data
            return Response(result_data,status=status.HTTP_200_OK)
        else:
            return Response({'data':'No plans for upgrade'},status=status.HTTP_204_NO_CONTENT)

class currentplandetail(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk):
        user = request.user
        current_plan = planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        if current_plan:
            result = planinvoiceuserwiseSerializer(current_plan,many=False).data
            return Response(result,status=status.HTTP_200_OK)
        else:
            return Response({'data':'No plans'},status=status.HTTP_204_NO_CONTENT)



class cancel_user_plan(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        data89=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        Dataroom.objects.filter(id=data89.dataroom.id).update(is_expired=True)
        planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).update(is_plan_active=False)
        return Response('success',status=status.HTTP_201_CREATED)

class reactivate_user_plan(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        data89=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        Dataroom.objects.filter(id=data89.dataroom.id).update(is_expired=False)
        planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).update(is_plan_active=True,cancel_at_monthend=False)
        return Response('success',status=status.HTTP_201_CREATED)


class userplan_stopat_monthend(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).update(cancel_at_monthend=True,auto_renewal=False)
        return Response('success',status=status.HTTP_201_CREATED)

class addon_get(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).exists():
            plan_data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
            addon_data=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,dataroom_id=plan_data.dataroom.id)
            addon_dataa=addon_plan_invoiceuserwiseSerializer(addon_data,many=True).data
        return Response(addon_dataa,status=status.HTTP_201_CREATED)