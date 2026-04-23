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
import re
# from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    ListCreateAPIView)
from django.template.loader import render_to_string
from dms.settings import *
from data_documents.models import DataroomFolder

from rest_framework import permissions
# from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import TokenAuthentication,Token
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
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
from .models import Profile, AccessHistory, User, InviteUser,planinvoiceuserwise,subscriptionplan,plansfeature,ccavenue_payment_cartids,addon_plan_tempforsameday,Captcha_model
from emailer import utils as emailer_utils
from emailer.models import SiteSettings
from users_and_permission.models import DataroomMembers
from dataroom.models import Dataroom, DataroomModules, DataroomOverview,otp_model
# from dataroom.models import Dataroom, DataroomModules, DataroomOverview
from users_and_permission.serializers import DataroomMembersSerializer
import json
from .utils import send_mail_to_superadmin
# from .ccavutil import encrypt,decrypt
# from .ccavResponseHandler import res
from string import Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import send_mail_to_superadmin,send_twodaysalert_email,send_trialtwodaysalert_email,send_trialexpiry_email,send_planrenewal_email
from django.db.models import F
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode













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

    def get(self, request, format=None):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        import datetime
        data = JSONParser().parse(request)
        print("Dat----",data)
        data['username'] = data.get('email').lower()
        # print("Dat----",data)
        # {'first_name': 'yghk', 'last_name': 'gfhfk', 'email': 'd@gmail.com', 'phone': 'fdhgfj', 'company_name': 'cvnvm', 'country': 'vbmv,', 'project_name': 'cmbm', 'is_trial': False, 'dataroom_name': 'cmbm'}
        data["is_superadmin"] = False
        data["is_staff"] = False
        data["is_team"] = False
        data["is_subscriber"] = True
        data["email"]=data.get('email').lower()
        captcha = data.get('captcha')
        if Captcha_model.objects.filter(code=captcha,is_used=False).exists():
            Captcha_model.objects.filter(code=captcha,is_used=False).update(is_used=True)
            pass
        else:
            return Response({'msg':'Invalid Captcha'}, status=status.HTTP_400_BAD_REQUEST)


        pattern = r'[#$%^!&*><]'
        if re.search(pattern, data.get('email')) or re.search(pattern,data.get('first_name'))  or  re.search(pattern, data.get('last_name')):

            return Response({"data":"special char no accepted"}, status=status.HTTP_400_BAD_REQUEST)



        serializer = UserSerializer(data=data)
        print("Is Valid",serializer.is_valid())
        print("Is Error",serializer.errors)
        if serializer.is_valid():
            serializer.save()
            token = get_random_string(length=100)
            user = User.objects.get(id = serializer.data.get('id'))
            user.is_subscriber = True 
            user.is_active = True 
            user.set_password('Password1#')
            user.save()

            profile = Profile.objects.get(user_id=serializer.data.get('id'))

            profile.user_id = user.id

            profile.reset_key = token

            profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")

            profile.save()

            constants.link="https://stage.docullyvdr.com/projectName/"

            link = constants.link+"password_set/?token="+profile.reset_key


            utils.send_activation_email(subject= 'Activate & setup password for your Docully account', to =data.get('email').lower(), first_name = data.get('first_name'), link =link)
            request.session['email'] = user.email
            request.session['id'] = user.id
            login(request, user)
            authenticate(email=user.email, password=data.get('password'))
            userserializer = UserSerializer(user, many=False)
            token1, created = Token.objects.get_or_create(user=user)
            token_data = {"token": token1.key,"user":userserializer.data}
            data = self.createEntryInAccessHistory(user, request)
            serializer = AccessHistorySerializer(data = data)                        
            if serializer.is_valid():
                serializer.save()



            if data.get('is_trial')==True:
                teams = MyTeams()
                teams.team_name = str(user.email)+' - '+str(data.get('dataroom_name'))
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
                dataroom.is_paid=False
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
                obj1.end_date=datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59))+datetime.timedelta(days=15)
                obj1.is_plan_active=True
                obj1.payment_complete=True
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
                utils.send_mail_to_superadmin(subject= 'User Activity- Free trial subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=data.get('dataroom_name'),payment_reference='',upgradef=0,quantityflag=0)
            Captcha_model.objects.filter(code=captcha,is_used=False).update(is_used=True)                    
            return Response({'tokendata':token_data,'userdata':serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"msg":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)



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





class Is_Active(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


    def get(self, request, format=None):
        # data = request.data
        # # all_data = data.get("user")
        # print('------',data)
        user = request.user
        user = User.objects.filter(id=user.id).update(is_active=True)

        return Response({'msg':'Done'}, status=status.HTTP_201_CREATED)





class User_Active(APIView):
    # authentication_classes = (TokenAuthentication, )
    # permission_classes = (IsAuthenticated, )
    permission_classes = [permissions.AllowAny]


    def post(self, request, format=None):
        """
        Return a Valid token if username and password
        is valid for a given client
        """
        # print("Data----",request.POST) 
        #print (request) 
        data = JSONParser().parse(request)
        # print("Data----",data)
        email = data.get('email').lower()
        # user = request.user
        # user = User.objects.filter(email=email).last()
        user = AccessHistory.objects.filter(user__email=email,is_logged_in=True)
        # for i in user:
        #     print('-----------',i.is_logged_in,'===========-----------',i.user.email)
        if user:
            atc=True
        else:
            atc=False
        
        

        return Response({'msg':atc}, status=status.HTTP_201_CREATED)





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
        import datetime
        if user :
            print('-------------------forget_trails',user.forget_trails)
            print('-------------------user.forget_trails_time',user.forget_trails_time)
            if user.forget_trails==3:
                blocked_time=user.forget_trails_time+datetime.timedelta(minutes=5)
                print('--------------tinmenow',datetime.datetime.now())
                print('--------------blocked + 5 mins',blocked_time)
                print('--------------blocked',user.is_blocked_time)
                if datetime.datetime.now()<=blocked_time:
                                    
                    return Response({'msg':'To many attempts  try after sometime'}, status=status.HTTP_400_BAD_REQUEST)
            print('--------------count------------',user.forget_trails)
            if user.forget_trails>3:
                print('--------------count------------inside')
                User.objects.filter(email=username).update(forget_trails=0,forget_trails_time=None)


            if user.check_password('Password1#'):
                profile = Profile.objects.get(user_id=user.id)
                token = get_random_string(length=100)
                profile.user_id = user.id

                profile.reset_key = token

                profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")

                profile.save()

                constants.link="https://stage.docullyvdr.com/projectName/"

                link = constants.link+"password_set/?token="+profile.reset_key


                utils.send_activation_email(subject= 'Activate & setup password for your Docully account', to =user.email, first_name = user.first_name, link =link)
                user=User.objects.get(id=user.id)
                user.forget_trails=user.forget_trails+1
                user.save()
                print('-----------count before111,',user.forget_trails)

                user=User.objects.get(id=user.id)
                if user.forget_trails>=3:
                    print('-----------count after1111,',user.forget_trails)
                    user.forget_trails_time=datetime.datetime.now()
                    user.save()

                return Response({"error": False, 'result': "Congrats ! Email Successfully send. Please check your email."}, status=status.HTTP_201_CREATED)


            else:
                token = get_random_string(length=100)
                profile = Profile()
                profile.user_id = user.id
                profile.reset_key = token
                profile.key_expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
                profile.save()
                # print(constants.link,"constants.link")
                constants.link="https://stage.docullyvdr.com/projectName/"
                link = constants.link+"password_reset/?token="+profile.reset_key
                # print(link,"link")
                # send_mail('[DMS] Please reset your password', 
                #     'Please go to the following page and choose a user email:\n'+link,
                #     'badgujarr007@gmail.com', [user.email], fail_silently=False)
                subject = "Reset your Docully password"
                subject = subject
                from_email = settings.DEFAULT_FROM_EMAIL
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

                user=User.objects.get(id=user.id)
                user.forget_trails=user.forget_trails+1
                user.save()


                print('-----------count before222,',user.forget_trails)
                user=User.objects.get(id=user.id)
                if user.forget_trails>=3:
                    print('-----------count after222,',user.forget_trails)
                    user.forget_trails_time=datetime.datetime.now()
                    user.save()

                return Response({"error": False, 'result': "Congrats ! Email Successfully send. Please check your email."}, status=status.HTTP_201_CREATED)
        return Response({"error": True}, status=status.HTTP_400_BAD_REQUEST)

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


@csrf_exempt
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
            # ciphertext1=data["current_password"]
            ciphertext2=password
            ciphertext3=confirm_password
            print ("paswwrdddn=======",ciphertext2)
            print ("paswwrdddn=======",ciphertext3)
            key='1203199320052023'
            key = key.encode('utf-8')
            # ciphertext_bytes = b64decode(ciphertext1)
            ciphertext_bytes2 = b64decode(ciphertext2)
            ciphertext_bytes3 = b64decode(ciphertext3)
            # print('------------1',ciphertext_bytes)
            iv = '1203199320052023'
            iv=iv.encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cipher2 = AES.new(key, AES.MODE_CBC, iv)
            # decrypted_data = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
            decrypted_data2 = unpad(cipher.decrypt(ciphertext_bytes2), AES.block_size)
            decrypted_data3 = unpad(cipher2.decrypt(ciphertext_bytes3), AES.block_size)
            # current_password= decrypted_data.decode('utf-8')
            password= decrypted_data2.decode('utf-8')
            confirm_password= decrypted_data3.decode('utf-8')

            if password == confirm_password:
                userpass = user_password_history.objects.filter(user__email=user).order_by('-id')[:3]
                if userpass:
                    for i in userpass:
                        if i.password==password:
                            
                            msg = "Already Used Password !"
                            return render(request, 'userauth/forgot_password.html', {'msg': msg,'user': usr.user,'token':token})
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
    print ("TOken is1111111111111", token)
    try:
        # print ("inside try block")
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


@csrf_exempt
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
            print ("user1:-======================", password)
            print ("user1:-===================ppp", confirm_password)
            ciphertext2=password
            ciphertext3=confirm_password
            print ("paswwrdddn=======",ciphertext2)
            print ("paswwrdddn=======",ciphertext3)
            key='1203199320052023'
            key = key.encode('utf-8')
            # ciphertext_bytes = b64decode(ciphertext1)
            ciphertext_bytes2 = b64decode(ciphertext2)
            ciphertext_bytes3 = b64decode(ciphertext3)
            # print('------------1',ciphertext_bytes)
            iv = '1203199320052023'
            iv=iv.encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cipher2 = AES.new(key, AES.MODE_CBC, iv)
            # decrypted_data = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
            decrypted_data2 = unpad(cipher.decrypt(ciphertext_bytes2), AES.block_size)
            decrypted_data3 = unpad(cipher2.decrypt(ciphertext_bytes3), AES.block_size)
            # current_password= decrypted_data.decode('utf-8')
            password= decrypted_data2.decode('utf-8')
            confirm_password= decrypted_data3.decode('utf-8')

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






class Captcha(APIView):
    # serializer_class = TokenSerializer
    # authentication_classes = [OAuth2Authentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        try:
            # Clean up old unused captcha records (older than 1 day)
            from datetime import timedelta
            from django.utils import timezone
            Captcha_model.objects.filter(is_used=True).delete()

            unique_id = get_random_string(length=6)
            Captcha_model.objects.create(code=unique_id)
            return Response({'code':unique_id})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Captcha generation failed: %s", e, exc_info=True)
            return Response({'msg': 'Captcha generation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










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
                'logged_in_time':timezone.now(), 
                # 'logged_out_time':timezone.now(), 
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
        import datetime
        # print("Data----",request.POST) 
        #print (request) 
        data = JSONParser().parse(request)
        # print("Data----",data)
        username = data.get('username').lower()
        password = data.get('password')
        captcha = data.get('captcha')
        print('----------------------------ecceccececcaptcha',captcha)
        print ("Before authentication")
        pattern = r'[#$%^!&*><]'
        # pattern1 = r'[\#$%^!&*><]'

        if Captcha_model.objects.filter(code=captcha,is_used=False).exists():
            Captcha_model.objects.filter(code=captcha,is_used=False).update(is_used=True)
            pass
        else:
            return Response({'msg':'Invalid Captcha'}, status=status.HTTP_400_BAD_REQUEST)
        if re.search(pattern, password):

            return Response({"data":"special char no accepted"}, status=status.HTTP_400_BAD_REQUEST)

        # print('------00',oo)
        user_count = User.objects.filter(email__iexact=username)
        
        user_not_blocked=False
        # print ("user count is ", user_count.count())
        # if username=='rushikesh.g@axat-tech.com' or username=='harvinndera@gmail.com' or username=='abhishek.m@axat-tech.com' or username=='sneha@confiexdataroom.com':
        #   pass
        # else:
        #   return Response({'msg':'On Maintenance'}, status=status.HTTP_400_BAD_REQUEST)


        



        if user_count.count() > 0:
            user = User.objects.get(email__iexact=username)
            user.is_active = True
            # print ("user is exist")
            if user is not None:
                

                
                if user.is_blocked==True :
                    blocked_time=user.is_blocked_time+datetime.timedelta(minutes=5)
                    print('--------------tinmenow',datetime.datetime.now())
                    print('--------------blocked + 5 mins',blocked_time)
                    print('--------------blocked',user.is_blocked_time)
                    if datetime.datetime.now()<=blocked_time:
                                        
                        return Response({'msg':'User is locked for sometime try again later'}, status=status.HTTP_400_BAD_REQUEST)
                print('--------------count------------',user_count.last().login_trails)
                if user_count.last().login_trails>3:
                    print('--------------count------------inside')
                    user_count.update(login_trails=0, is_blocked=False,is_blocked_time=None)
                
                # if username=='' and password=='':
                #       user.save()
                #       # Dataroom.objects.filter(id=583).update(is_expired=False,is_request_for_archive=False)
                #       request.session['email'] = user.email
                #       request.session['id'] = user.id
                #       login(request, user)
                #       serializer = UserSerializer(user, many=False)
                #       token, created = Token.objects.get_or_create(user=user)
                #       token_data = {"token": token.key,"user":serializer.data}
                #       return Response(token_data)
                # else:
                #   pass

                try:
                    ciphertext1=password
                    print ("paswwrdddn=======",ciphertext1)
                    key='1203199320052023'
                    key = key.encode('utf-8')
                    ciphertext_bytes = b64decode(ciphertext1)
                    print('------------1',ciphertext_bytes)
                    iv = '1203199320052023'
                    iv=iv.encode('utf-8')
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted_data = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
                    password_decrypted= decrypted_data.decode('utf-8')
                    password = decrypted_data.decode('utf-8')[:-6]
                except:
                    print('---------------',user.login_trails)
                    print('---------------',user.is_blocked)
                    print('---------------',user.is_blocked_time)
                    user=User.objects.get(id=user.id)
                    user_count.update(login_trails=user.login_trails+1)
                    print('---------------user_count.last().login_trails',user_count.last().login_trails)

                    if user_count.last().login_trails>=3:
                        user_count.update(is_blocked=True,is_blocked_time=datetime.datetime.now())

                    return Response({'msg':'Incorrect username/password'}, status=status.HTTP_400_BAD_REQUEST)





                is_user = user.check_password(password)
                # User.objects.filter(id=user.id).update(is_active=True)
                # print ("is_user status", is_user)
                # print ("is_user active", user.is_active)
                if is_user:
                    user.save()

                    if user.is_active:
                        
                        # Correct password, and the user is marked "activaee"
                        # print ("user is active")
                        request.session['email'] = user.email
                        request.session['id'] = user.id
                        if salt_key.objects.filter(salt_code=password_decrypted).exists():
                            user=User.objects.get(id=user.id)
                            user_count.update(login_trails=user.login_trails+1)

                            if user_count.last().login_trails>=3:
                                user_count.update(is_blocked=True,is_blocked_time=datetime.datetime.now())
                            return Response({'msg':'Incorrect username/password'}, status=status.HTTP_400_BAD_REQUEST)
                        salt_key.objects.create(salt_code=password_decrypted)
                        login(request, user)
                        authenticate(email=username, password=password)
                        serializer = UserSerializer(user, many=False)
                        user_ser=serializer.data
                        # if Token.objects.filter(user=user).exists():
                            # AccessHistory.objects.filter(user=user,is_logged_in=True).update(logged_out_time=datetime.datetime.now(),is_logged_in=False)
                            # Token.objects.filter(user=user).delete()
                        token = Token.objects.create(user=user)
                        if not User_time_zone.objects.filter(user_id=user.id).exists():
                            User_time_zone.objects.create(user_id=user.id,time_zone_id=377)

                        user_ser['user_time_zone']=User_time_zone.objects.filter(user_id=user.id).values('time_zone__country_code','time_zone__country','time_zone__tz','time_zone_id','time_zone__offset','time_zone__abbreviation')
                        token_data = {"token": token.key,"user":user_ser}
                        data = self.createEntryInAccessHistory(user, request)
                        serializer = AccessHistorySerializer(data = data)                        
                        if serializer.is_valid():
                            serializer.save()
                            print('token_data',serializer.data)
                            print('token_data',serializer.data['id'])
                            sess=request.session['login_id']=serializer.data['id']
                            request.session.modified = True
                            print('---------',sess)
                            token_data['login_id']=serializer.data['id']
                            token_data['login_id1']=ciphertext1[14:22]
                            
                                                                                    
                            
                            return Response(token_data)
                    else:
                        return Response({'msg':'User is not active'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                     # print ("user is not activate")
                     user=User.objects.get(id=user.id)
                     user_count.update(login_trails=user.login_trails+1)

                     if user_count.last().login_trails>=3:
                         user_count.update(is_blocked=True,is_blocked_time=datetime.datetime.now())
                     return Response({'msg':'Incorrect username/password'}, status=status.HTTP_400_BAD_REQUEST)
            else :
                return Response({'msg':'Invalid Details'}, status=status.HTTP_400_BAD_REQUEST)
        else :
            # print ("user does not exist")
            return Response({'msg':'Invalid Details'}, status=status.HTTP_400_BAD_REQUEST)
            

class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )    
    def get(self, request):
        print('================',request.session)
        # sess=request.session['login_id']
        
        # print("logout user",request.user)
        # request.
        login_id = request.GET.get('login_id')
        username = request.user
        print('================login_id',login_id)
        user = User.objects.filter(id=username.id)
        ip = utils.get_client_ip(request)
        access_history = AccessHistory.objects.filter(id=login_id).update(logged_out_time=timezone.now(),is_logged_in=False)
        # print("logout id",username.id)
        # print("LogoutView",User.objects.filter(id=username.id).values())
        # if user.exists():
        #     user.update(is_active=False)
        try:
            print(request.session['id'],"<=== check session values ===>",request.session['email'])
            del request.session['id']
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
        # token=request.META.get('HTTP_AUTHORIZATION')
        token=request.GET.get('token')
        print('----token',token)
        # if Token.objects.filter(user=username).exists():
        Token.objects.filter(key=token).update(expired=True)
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
            data['user_time_zone']=User_time_zone.objects.filter(user_id=user.id).values('time_zone__country_code','time_zone__country','time_zone__tz','time_zone_id','time_zone__offset','time_zone__abbreviation')
            # print(data,'get api dattttttttttttttttaaaaaaaaaaaaaaaaaaaaa')

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        user = request.user
        ip = utils.get_client_ip(request)
        # print("dataaaaa", data)
        # data['avatar'] = None
        print('------------------dataaaaaaa=====',data)
        print('--------firstnameeee',data['first_name'])
        pattern = r'[\#$%^!&*><]'

        spec_char=False

        if re.search(pattern, data['first_name']):
            spec_char=True
        if re.search(pattern, data['last_name']):
            spec_char=True
        if spec_char==True:
            return Response({"data":"special char no accepted"}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            User.objects.filter(id=user.id).update(first_name=data['first_name'],last_name= data['last_name'])
            if User_time_zone.objects.filter(user_id=user.id).exists():
                User_time_zone.objects.filter(user_id=user.id).update(time_zone_id=int(data['tz_id']))
            else:
                User_time_zone.objects.create(user_id=user.id,time_zone_id=int(data['tz_id']))
            # for i in User_time_zone.objects.filter(user_id=user.id):
                
            serializer = UserSerializer(user, many=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        


        # serializer = UserSerializer(user, data=data)
        # print("serializer is valid", serializer.is_valid())
        # print("serializer is valid", serializer.errors)
        # if serializer.is_valid():
        #     serializer.save()
            # print(serializer.data,'post api dattttttttttttttttaaaaaaaaaaaaaaaaaaaaa')


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
        print ("Before authentication")
        ciphertext1=data["current_password"]
        ciphertext2=data["new_password"]
        ciphertext3=data["confirm_new_password"]
        # captcha = data['captcha']
        # if Captcha_model.objects.filter(code=captcha,is_used=False).exists():
            
            # pass
        # else:
            # return Response({'msg':'Invalid Captcha'}, status=status.HTTP_400_BAD_REQUEST)

        print ("paswwrdddn=======",ciphertext1)
        key='1203199320052023'
        key = key.encode('utf-8')
        ciphertext_bytes = b64decode(ciphertext1)
        ciphertext_bytes2 = b64decode(ciphertext2)
        ciphertext_bytes3 = b64decode(ciphertext3)
        print('------------1',ciphertext_bytes)
        print('------------1',ciphertext_bytes2)
        print('------------1',ciphertext_bytes3)
        iv = '1203199320052023'
        iv=iv.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        cipher2 = AES.new(key, AES.MODE_CBC, iv)
        cipher3 = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
        decrypted_data2 = unpad(cipher2.decrypt(ciphertext_bytes2), AES.block_size)
        decrypted_data3 = unpad(cipher3.decrypt(ciphertext_bytes3), AES.block_size)
        current_password= decrypted_data.decode('utf-8')[:-6]
        new_password= decrypted_data2.decode('utf-8')[:-6]
        confirm_new_password= decrypted_data3.decode('utf-8')[:-6]

        new_user = user.check_password(current_password)
        if new_user:

             
            if((confirm_new_password == new_password)):
                userpass = user_password_history.objects.filter(user=user).order_by('-id')[:3]
                if userpass:
                    for i in userpass:
                        if i.password==new_password:
                            return Response({"error":"Already Used Password !"}, status=status.HTTP_400_BAD_REQUEST)
                ip = utils.get_client_ip(request)
                user.set_password(new_password)
                user.save()
                user_password_history.objects.create(user=user,password=new_password)
                # Captcha_model.objects.filter(code=captcha,is_used=False).update(is_used=True)
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
        profile_pics = request.FILES.get('file')
        import magic
        file12=profile_pics
        print('--------------imaggggggggprofile_pics',profile_pics)
        mime = magic.from_buffer(file12.read(), mime=True)
        if profile_pics.content_type==mime:
            user=User.objects.get(id=user.id)
            user.avatar.delete(save=True)
            user.avatar = profile_pics
            user.save() 
            print('--------------imaggggggggprofile_pics222222222222222222222',profile_pics)
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            return Response({'msg':'Cannot upload this type of file'},status=status.HTTP_400_BAD_REQUEST)



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
            # try :
            invitee_member = User.objects.get(id=invite_user.invitiation_receiver.id)
            invitation_sender = User.objects.get(id=invite_user.invitiation_sender.id)
            site_setting = SiteSettings.objects.get(id=1)
            context["invitee_member"] = invitee_member
            context["invitation_sender"] = invitation_sender
            context["site_setting"] = site_setting
            member_check = DataroomMembers.objects.filter(dataroom_id=invite_user.dataroom_invitation)
            print(member_check)
            from notifications.models import AllNotifications
            for i in member_check:
                print(i.member)
                AllNotifications.objects.create(user=i.member,dataroom_id=invite_user.dataroom_invitation,dataroom_member_invitation_accept=invite_user)
            # invite_user.save()
            # except UserDoesNotExist:
                # print ("User Does Not exit")
                # return False
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
        context = {}
        user_exist = request.GET.get("user_exist")
        # print('---------------',user_exist)
        
        invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=False).exists()
        # print ("invite user",invite_user)
        import datetime
        msg = "User with this Invitation link does not exist"
        if invite_user != False:
            # print ("User is exist ")
            invite_user = InviteUser.objects.get(invitation_token=key, is_invitation_expired=False, is_invitation_accepted=False)
            # print ("invite_user.invitiation_receiver", invite_user.invitiation_receiver)
            # try :
            invitee_member = User.objects.get(id=invite_user.invitiation_receiver.id)
            if invitee_member.check_password('Password1#'):
                    msg = "To accept invitation, first you need to create your unique password and set up your account. Please contact support@docullyvdr.com for any questions."
                    context["message"] = msg
                    print ("-----------------------------3")
                    return render(request, 'userauth/admin_invitation_error.html', context)

            invitation_sender = User.objects.get(id=invite_user.invitiation_sender.id)
            site_setting = SiteSettings.objects.get(id=1)
            context["invitee_member"] = invitee_member
            context["invitation_sender"] = invitation_sender
            context["site_setting"] = site_setting
            context["user_exist"] = user_exist
            # print('coming here 34343434')
            invite_user.is_invitation_accepted=True
            invite_user.invitatation_acceptance_date=datetime.datetime.now()
            # invite_user.save()
            member_check = DataroomMembers.objects.filter(dataroom_id=invite_user.dataroom_invitation,is_deleted=False)
            print(member_check)
            from notifications.models import AllNotifications
            for i in member_check:
                print(i.member.id,invitee_member.id,'iiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                if i.is_la_user==True or i.is_dataroom_admin==True or i.member.id==invitee_member.id:
                    AllNotifications.objects.create(user=i.member,dataroom_id=invite_user.dataroom_invitation,dataroom_member_invitation_accept=invite_user)
                
            invite_user.save()

            # InviteUser.objects.(invitation_token=key).update(is_invitation_accepted=True,invitatation_acceptance_date =datetime.datetime.now())
            user = User.objects.filter(id=invite_user.invitiation_receiver.id,is_active=True)
            if user.exists():
                print ("-----------------------------1")
                return redirect("https://stage.docullyvdr.com/#/dashboard")

            else:
                print ("-----------------------------2")
                return render(request, 'userauth/admin_invitation_welcome.html', context)
            # except UserDoesNotExist:
                # print ("User Does Not exit")
                # return False
        else:
            invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=True, is_invitation_accepted=False).exists()
            if invite_user !=False:
                msg = "Invitation is already expired"
                context["message"] = msg
                print ("-----------------------------3")
                return render(request, 'userauth/admin_invitation_error.html', context)
            else:
                invite_user = InviteUser.objects.filter(invitation_token__iexact=key).exists()
                if invite_user != False:                    
                    invite_user = InviteUser.objects.filter(invitation_token__iexact=key, is_invitation_expired=False, is_invitation_accepted=True).exists()
                    if invite_user != False:
                        msg = "Invitation is already accepted"
                        # print ("Invitation is already accepted")
                        context["message"] = msg 
                        print ("-----------------------------4")
                        return render(request, 'userauth/admin_invitation_error.html', context)

                    else:
                        msg = "Inviatation with this link does not exist"
                        # print ("Inviatation with this link does not exist")
                        # return False
                        return render(request, 'userauth/admin_invitation_error.html', context)
                else :
                    msg = "Inviatation with this link does not exist"
                    # return False
                    return render(request, 'userauth/admin_invitation_error.html', context)
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
    
    def post(self, request, format=None):
        data = JSONParser().parse(request)
        # print("Data----",data)
        # username = data.get('username').lower()
        # password = data.get('password')
        captcha = data.get('captcha')
        useremail=data.get('email').lower()
        if Captcha_model.objects.filter(code=captcha,is_used=False).exists():
            Captcha_model.objects.filter(code=captcha,is_used=False).update(is_used=True)
            pass
        else:
            return Response({'msg':'Invalid Captcha'}, status=status.HTTP_400_BAD_REQUEST)

        pattern = r'[#$%^!&*><]'

        if re.search(pattern, data.get('email')) :

            return Response({"data":"special char no accepted"}, status=status.HTTP_400_BAD_REQUEST)



        subject = 'Sign Up lead'
        to = ['bekcixdud_6ue47hx@parser.zohocrm.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        message = '<!doctype html><html lang="en">Hello Team,</br> Following user tried to sign up on the portal <br>Email ID:'+str(request.GET.get('email'))+'<br> Thanks,<br> Web Team </html>'
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        if User.objects.filter(email=useremail).exists():
            return Response(False)
        else:
            return Response(True)      

class contactusform(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        data=request.data
        subject = 'new web lead'
        to = ['phhazsbkp_v8sheah@parser.zohocrm.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        message = '<!doctype html><html lang="en">Hello Team,</br>first name: '+str(data['first_name'])+'</br>last name: '+str(data['last_name'])+'</br>email: '+str(data['email'])+'</br>contact number: '+str(data['contact_number'])+'</br>company: '+str(data['company'])+'</br>country: '+str(data['country'])+'</br>message: '+str(data['message'])+'<br> Thanks,<br> Web Team </html>'
        msg = EmailMessage(subject, message, to=to,cc=['vdrsales@docullyvdr.com'],from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        return Response('done',status=status.HTTP_201_CREATED)

# class plan_subscription(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )

#   def post(self, request,format=None):
#       user=request.user
#       data=request.data 
#       print(data,user.id,'this data')
#       # if data.get('step')== 'step1':
#       #     # obj.edition=data.get('edition')


#       #     obj.save()
#       #     # print(obj.id,'get till here')
#       #     return Response(obj.id, status=status.HTTP_201_CREATED)
#       # elif data.get('step')== 'step2':
#       #     # obj=planinvoiceuserwise.objects.get(id=data.get('planid'))
#       #     # obj.selected_plan=data.get('selected_plan')
#       #     obj.select_billing_term=data.get('Billing_freq')
#       #     obj.total_fee=data.get('Total_fee')
#       #     obj.save()
#       #     # print(obj.id,'get till here')
#       #     return Response(obj.id, status=status.HTTP_201_CREATED)
#       if data.get('step')== 'step3':
#               obj=planinvoiceuserwise()
#               obj.user_id=user.id
#               rflag=0

#               obj.vat=data.get('vat_detail')
#               obj.grand_total=data.get('grand_total')
#               obj.billing_address=data.get('billing_address')
#               obj.billing_city=data.get('billing_city')
#               obj.billing_state=data.get('billing_state')
#               obj.billing_country=data.get('billing_country')
#               obj.company_name=data.get('company_name')
#               obj.po_box=data.get('po_box')
#               obj.total_fee=data.get('Total_fee')
#               obj.select_billing_term=data.get('Billing_freq')
#               obj.plan_id=data.get('pid')
#               obj.is_plan_active=True
#               obj.project_name=data.get('dataroom_name')
#               plandataa=subscriptionplan.objects.get(id=obj.plan.id)
#               if 'trial' in plandataa.name.lower():
#                   if user.is_trial==False:
#                       User.objects.filter(id=user.id).update(is_trial=True)
#                   else:
#                       return Response('Already Used Trial', status=status.HTTP_400_BAD_REQUEST)

#               teams = MyTeams()
#               teams.team_name = 'My Team'
#               teams.dataroom_allowed = 1
#               teams.dataroom_admin_allowed = 25
#               teams.dataroom_storage_allowed = int(plandataa.storage)
#               teams.team_created_by_id = user.id
#               teams.user_id = user.id
#               teams.start_date = datetime.date.today()
#               obj.start_date=datetime.datetime.now()
#               if 'trial' in plandataa.name.lower():
#                   teams.end_date = datetime.date.today() + datetime.timedelta(days=15)
#                   obj.end_date=datetime.datetime.now() + datetime.timedelta(days=15)

#               elif plandataa.term.lower()=='monthly':
#                   teams.end_date = datetime.date.today() + datetime.timedelta(days=30)
#                   obj.end_date=datetime.datetime.now() + datetime.timedelta(days=30)
#               elif plandataa.term.lower()=='quarterly':
#                   teams.end_date = datetime.date.today() + datetime.timedelta(days=90)
#                   obj.end_date=datetime.datetime.now() + datetime.timedelta(days=90)
#               elif plandataa.term.lower()=='annually' or plandataa.term.lower()=='yearly':
#                   teams.end_date = datetime.date.today() + datetime.timedelta(days=365)
#                   obj.end_date=datetime.datetime.now() + datetime.timedelta(days=365)



#               if data.get('upgradeplanflag')=='True':
#                       oldplandata=planinvoiceuserwise.objects.filter(user_id=user.id,id=data.get('oldplanid')).first()
#                       obj.dataroom_id=oldplandata.dataroom.id
#                       planinvoiceuserwise.objects.filter(user_id=user.id,id=data.get('oldplanid')).update(is_plan_upgraded=True,is_plan_active=False,auto_renewal=False,is_latest_invoice=False)
#                       Dataroom.objects.filter(id=oldplandata.dataroom.id).update(dataroom_storage_allocated=int(plandataa.storage),dataroom_nameFront=data.get('dataroom_name'),is_paid=True)
#                       dataroom=Dataroom.objects.filter(id=oldplandata.dataroom.id).first()
#                       rflag=1

#               else:
#                       teams.save()

#                       dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
#                       dataroom = Dataroom()
#                       dataroom.dataroom_name = data.get('dataroom_name')
#                       # dataroom.dataroom_name = 'Dataroom'

#                       # need to show  dataroom on hold
#                       # dataroom.is_dataroom_on_live = True
#                       dataroom.is_dataroom_on_live = False
#                       dataroom.dataroom_storage_allocated = int(plandataa.storage)
#                       dataroom.user = user
#                       dataroom.my_team_id = teams.id
#                       dataroom.dataroom_modules = dataroom_modules
#                       if 'trial' in plandataa.name.lower():
#                           dataroom.is_paid=False
#                           dataroom.trial_expiry_date=datetime.datetime.now() + datetime.timedelta(days=15)
#                       else:
#                           dataroom.is_paid=True
#                       dataroom.save()
#                       obj.dataroom_id=dataroom.id

#                       dataroom_member_data = {
#                               'dataroom':dataroom.id, 
#                               'member' :user.id, 
#                               'member_type':1, 
#                               'member_added_by':user.id,
#                               'is_dataroom_admin':True
#                           }
#                       DataroomMembers.objects.create(dataroom_id=dataroom.id, member_id=user.id, member_added_by_id=user.id, is_dataroom_admin=True,memberactivestatus=True,is_q_a_user=True)
#                       overview = DataroomOverview.objects.create(dataroom_id=dataroom.id, user_id=user.id)
#               obj.save()
#               if 'trial' in plandataa.name.lower():
#                   utils.send_trialperiod_email(subject= '15 Days free trial is successfully activated on Docully for '+str(data.get('dataroom_name')), to =user.email.lower(), first_name = user.first_name, data =obj,projectname=data.get('dataroom_name'))
#                   utils.send_mail_to_superadmin(subject= 'User Activity- Free trial subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=data.get('dataroom_name'),payment_reference='',upgradef=0,quantityflag=0)
#               else:
#                   utils.send_subscription_email(subject= 'Your Docully Subscription - Activated', to =user.email.lower(), first_name = user.first_name, data =obj,projectname=obj.project_name)
#                   utils.send_mail_to_superadmin(subject= 'User Activity- Paid subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=obj.project_name,payment_reference='',upgradef=rflag,quantityflag=0)                    
                
#               User.objects.filter(id=user.id).update(paid_subscription=True)
#               if data.get('company_name') is not None or False:
#                   User.objects.filter(id=user.id).update(company_name=data.get('company_name'))

#               return Response('Done', status=status.HTTP_201_CREATED)
#       return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)


#   def get(self, request, format=None):
#       user=request.user       
#       data=planinvoiceuserwise.objects.filter(user_id=user.id,is_latest_invoice=True)
#       dataa=planinvoiceuserwiseSerializer(data,many=True)
#       count=data.count()
#       return Response({'data':dataa.data,'size':count},status=status.HTTP_201_CREATED)


# url(r'^projectName/newplan_process/(?P<pk>[0-9]+)/$', payment_api.as_view(), name="newplan_process"),
# url(r'^projectName/dvd_addon_pay/$', dvd_addon_pay.as_view(), name="dvd_addon_pay"),
class plan_subscriptionold(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def post(self, request,format=None):
                    user=request.user
                    data=request.data 
                    print(data,user.id,'this data')
                    import datetime
                    plandataa=subscriptionplan.objects.get(id=data.get('pid'))
                    cart_id_obj=ccavenue_payment_cartids()
                    user_id=user.id
                    is_new_plan=True
                    cart_id_obj.save()
                    # if data.get('billing_country')=='UAE':
                    #       tottalfee=int(plandataa.cost)
                    #       # discountedprice= int(plandataa.cost)
                    #       gtotal=int(plandataa.cost)
                    #       countryt=data.get('billing_country')
                    # else:
                    countryt=data.get('others')
                    gtotal=int(plandataa.cost)
                    print(gtotal,data.get('grand_total'))
                    if gtotal==data.get('grand_total'):
                            obj=planinvoiceuserwise()
                            obj.user_id=user.id  
                            obj.is_latest_invoice=False
                            obj.save()   
                            tempidd=int(obj.id)+2111-7
                            p_merchant_id = '48133'
                            p_order_id = str(cart_id_obj.id)
                            p_currency = 'AED'
                            p_amount = str(float(gtotal)*3.67)
                            # p_redirect_url = 'https://services.docullyvdr.com/projectName/newplan_process/'+str(tempidd)+'/'


                            p_language = 'EN'
                            access_code='AVIH04JJ41CN55HINC'
                            workingKey='BE768C208260B6EE9FC6223E5392D727'

                            if data.get('upgradeplanflag')=='True':
                                p_cancel_url = 'https://stage.docullyvdr.com/#/manage-subscription/'+str(data.get('oldplanid'))+'/end'
                                p_redirect_url = 'https://stage.docullyvdr.com/projectName/newplan_payment/'+str(tempidd)+'/846633/'


                            else:
                                p_cancel_url = 'https://stage.docullyvdr.com/#/billing-term/end'
                                p_redirect_url = 'https://stage.docullyvdr.com/projectName/newplan_payment/'+str(tempidd)+'/674653/'

                            
                            todaysdate=datetime.datetime.now()
                            todaysdate2=datetime.datetime.strptime(str(todaysdate),'%Y-%m-%d %H:%M:%S.%f')
                            todaysdate3=todaysdate2.strftime("%d-%m-%Y")
                            if user.email=='harvinndera@gmail.com':
                                p_amount='1.00'
                            merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency="+p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&response_type=JSON&si_type=ONDEMAND&si_mer_ref_no='+p_order_id+'&si_is_setup_amt=Y&si_start_date='+str(todaysdate3)
                            encryption = encrypt(merchant_data,workingKey)
                            newurl="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction&merchant_id="+p_merchant_id+"&encRequest="+encryption+"&access_code="+access_code

                            obj=planinvoiceuserwise.objects.get(id=obj.id)
                            obj.user_id=user.id
                            obj.vat=data.get('vat_detail')
                            obj.grand_total=data.get('grand_total')
                            # obj.billing_address=data.get('billing_address')
                            # obj.billing_city=data.get('billing_city')
                            # obj.billing_state=data.get('billing_state')
                            obj.billing_country=countryt
                            # if data.get('company_name')!=None or data.get('company_name')!='':
                            #   obj.company_name=data.get('company_name')
                            # else:
                            #   obj.company_name=user.company_name
                            obj.customer_name=str(user.first_name)+str(user.last_name)
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
                                    addonplandata=addon_plans.objects.filter(planstatus=True).first()
                                    addondata1=addon_plan_tempforsameday()
                                    addondata1.user_id=user.id
                                    addondata1.dataroom_id=oldplandata.dataroom.id
                                    addondata1.addon_plan_id=addonplandata.id
                                    addondata1.start_date=datetime.datetime.now()
                                    addondata1.is_plan_active=True   
                                    addondata1.save()

                            if 'trial' in plandataa.name.lower():
                                    if user.is_trial==False:
                                        teams = MyTeams()
                                        teams.team_name = str(user.email)+' - '+str(data.get('dataroom_name'))
                                        teams.dataroom_allowed = 1
                                        teams.dataroom_admin_allowed = 25
                                        teams.dataroom_storage_allowed = int(plandataa.storage)
                                        teams.team_created_by_id = user.id
                                        teams.user_id = user.id
                                        teams.onlinesubscriber=True

                                        teams.start_date = datetime.date.today()
                                        obj.start_date=datetime.datetime.now()
                                        teams.end_date = datetime.date.today() + datetime.timedelta(days=15)
                                        obj.end_date=datetime.datetime.now() + datetime.timedelta(days=15)
                                        obj.is_latest_invoice=True
                                        obj.payment_complete=True
                                        obj.is_plan_active=True
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
                                        dataroom.trial_expiry_date=datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59))+datetime.timedelta(days=15)
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
                                        ccavenue_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                        # if data.get('company_name') is not None or False:
                                        #   User.objects.filter(id=user.id).update(company_name=data.get('company_name'))                                        
                                        utils.send_trialperiod_email(subject= '15 Days free trial is successfully activated on Docully for '+str(data.get('dataroom_name')), to =user.email.lower(), first_name = user.first_name, data =obj,projectname=data.get('dataroom_name'))
                                        utils.send_mail_to_superadmin(subject= 'User Activity- Free trial subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=data.get('dataroom_name'),payment_reference='',upgradef=0,quantityflag=0)
                                        User.objects.filter(id=user.id).update(is_trial=True)

                                        return Response('https://stage.docullyvdr.com/#/payment-successful', status=status.HTTP_201_CREATED)                                    
                                    else:
                                        return Response('Already Used Trial', status=status.HTTP_400_BAD_REQUEST)
                            else:
                                    obj.save()
                                    ccavenue_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                    return Response(p_redirect_url, status=status.HTTP_201_CREATED)                                    
                            
                             
                    else:
                        return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)


import stripe
stripe.api_key = 'sk_test_51NL2YpSDKmPlLj2iibexoWwPr01eypoqPSenOPqVjDruALmbAuZ2T8HcAsJx89Lz5J3ipBjJqaVu2YRhBleZXdJs00701jrPoi'
# stripe.api_key = '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'

class plan_subscription(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def post(self, request,format=None):
                    user=request.user
                    data=request.data
                    import datetime 
                    print(data,user.id,'this data')
                    plandataa=subscriptionplan.objects.get(id=data.get('pid'))
                    cart_id_obj=ccavenue_payment_cartids()
                    user_id=user.id
                    is_new_plan=True
                    cart_id_obj.save()
                    # if data.get('billing_country')=='UAE':
                    #       tottalfee=int(plandataa.cost)
                    #       # discountedprice= int(plandataa.cost)
                    #       gtotal=int(plandataa.cost)
                    #       countryt=data.get('billing_country')
                    # else:
                    countryt=data.get('others')
                    gtotal=int(plandataa.cost)
                    print(gtotal,data.get('grand_total'))
                    if gtotal==data.get('grand_total'):
                            obj=planinvoiceuserwise()
                            obj.user_id=user.id  
                            obj.is_latest_invoice=False
                            obj.save()   
                            tempidd=int(obj.id)+2111-7
                            p_merchant_id = '48133'
                            p_order_id = str(cart_id_obj.id)
                            p_currency = 'AED'
                            p_amount = str(float(gtotal)*3.67)
                            # p_redirect_url = 'https://services.docullyvdr.com/projectName/newplan_process/'+str(tempidd)+'/'


                            p_language = 'EN'
                            access_code='AVIH04JJ41CN55HINC'
                            workingKey='BE768C208260B6EE9FC6223E5392D727'

                            if data.get('upgradeplanflag')=='True':
                                p_cancel_url = 'https://stage.docullyvdr.com/#/manage-subscription/'+str(data.get('oldplanid'))+'/end'
                                p_redirect_url = 'https://stage.docullyvdr.com/projectName/newplan_payment/'+str(tempidd)+'/846633/'
                                flag12=True

                            else:
                                p_cancel_url = 'https://stage.docullyvdr.com/#/billing-term/end'
                                p_redirect_url = 'https://stage.docullyvdr.com/projectName/newplan_payment/'+str(tempidd)+'/674653/'
                                flag12=False
                            
                            todaysdate=datetime.datetime.now()
                            todaysdate2=datetime.datetime.strptime(str(todaysdate),'%Y-%m-%d %H:%M:%S.%f')
                            todaysdate3=todaysdate2.strftime("%d-%m-%Y")
                            if user.email=='harvinndera@gmail.com':
                                p_amount='1.00'
                            # merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency="+p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&response_type=JSON&si_type=ONDEMAND&si_mer_ref_no='+p_order_id+'&si_is_setup_amt=Y&si_start_date='+str(todaysdate3)
                            # encryption = encrypt(merchant_data,workingKey)
                            # newurl="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction&merchant_id="+p_merchant_id+"&encRequest="+encryption+"&access_code="+access_code

                            obj=planinvoiceuserwise.objects.get(id=obj.id)
                            obj.user_id=user.id
                            obj.vat=data.get('vat_detail')
                            obj.grand_total=data.get('grand_total')
                            # obj.billing_address=data.get('billing_address')
                            # obj.billing_city=data.get('billing_city')
                            # obj.billing_state=data.get('billing_state')
                            obj.billing_country=countryt
                            # if data.get('company_name')!=None or data.get('company_name')!='':
                            #   obj.company_name=data.get('company_name')
                            # else:
                            #   obj.company_name=user.company_name
                            obj.customer_name=str(user.first_name)+str(user.last_name)
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
                                    addonplandata=addon_plans.objects.filter(planstatus=True).first()
                                    addondata1=addon_plan_tempforsameday()
                                    addondata1.user_id=user.id
                                    addondata1.dataroom_id=oldplandata.dataroom.id
                                    addondata1.addon_plan_id=addonplandata.id
                                    addondata1.start_date=datetime.datetime.now()
                                    addondata1.is_plan_active=True   
                                    addondata1.save()

                            if 'trial' in plandataa.name.lower():
                                    if user.is_trial==False:
                                        teams = MyTeams()
                                        teams.team_name = str(user.email)+' - '+str(data.get('dataroom_name'))
                                        teams.dataroom_allowed = 1
                                        teams.dataroom_admin_allowed = 25
                                        teams.dataroom_storage_allowed = int(plandataa.storage)
                                        teams.team_created_by_id = user.id
                                        teams.user_id = user.id
                                        teams.onlinesubscriber=True

                                        teams.start_date = datetime.date.today()
                                        obj.start_date=datetime.datetime.now()
                                        teams.end_date = datetime.date.today() + datetime.timedelta(days=15)
                                        obj.end_date=datetime.datetime.now() + datetime.timedelta(days=15)
                                        obj.is_latest_invoice=True
                                        obj.payment_complete=True
                                        obj.is_plan_active=True
                                        teams.save()
                                        dataroom_modules = DataroomModules.objects.create(is_watermarking=False, is_drm=False,is_question_and_answers=False,is_collabration=False, is_ocr=False, is_editor=False)
                                        dataroom = Dataroom()
                                        dataroom.dataroom_name = data.get('dataroom_name')
                                        phone=data.get('contact_no')
                                        company_name=data.get('company_name')
                                        country=data.get('country')
                                        dataroom.is_dataroom_on_live = False
                                        dataroom.dataroom_storage_allocated = int(plandataa.storage)
                                        dataroom.user = user
                                        dataroom.my_team_id = teams.id
                                        dataroom.dataroom_modules = dataroom_modules
                                        dataroom.is_paid=False
                                        dataroom.trial_expiry_date=datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59))+datetime.timedelta(days=15)
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
                                        ccavenue_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                        # if data.get('company_name') is not None or False:
                                        #   User.objects.filter(id=user.id).update(company_name=data.get('company_name'))                                        
                                        utils.send_trialperiod_email(subject= '15 Days free trial is successfully activated on Docully for '+str(data.get('dataroom_name')), to =user.email.lower(), first_name = user.first_name, data =obj,projectname=data.get('dataroom_name'))
                                        utils.send_mail_to_superadmin(subject= 'User Activity- Free trial subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =obj,addondata=0,projectname=data.get('dataroom_name'),payment_reference='',upgradef=0,quantityflag=0,phone=phone,company_name=company_name,country=country)

                                        User.objects.filter(id=user.id).update(is_trial=True,is_admin=True,phone=phone,company_name=company_name,country=country)

                                        return Response('https://stage.docullyvdr.com/#/payment-successful', status=status.HTTP_201_CREATED)                                    
                                        
                                    else:
                                        return Response('Already Used Trial', status=status.HTTP_400_BAD_REQUEST)
                            else:
                                    obj.save()
                                    ccavenue_payment_cartids.objects.filter(id=cart_id_obj.id).update(is_new_plan=True,new_plan_id=obj.id) 
                                    # nurl='https://stage.docullyvdr.com/projectName/teststripe/'+str(data.get('oldplanid'))+'/'+str(cart_id_obj.id)+'/'+str(flag12)+'/'+str(tempidd)+'/'+p_amount+'/'+'none'+'/'+str(user.email)+'/'
                                    price_id = data.get("price_id")  # Pass Pro/Lite Price ID from Angular

                                    checkout_session = stripe.checkout.Session.create(
                                        payment_method_types=["card"],
                                        line_items=[
                                            {
                                                "price": price_id,
                                                "quantity": 1,
                                            }
                                        ],
                                        mode="subscription",
                                        success_url="http://stage.docullyvdr.com/success_stripe?session_id={CHECKOUT_SESSION_ID}",
                                        cancel_url="http://stage.docullyvdr.com/cancel_stripe",
                                    )
                                    print('-------------------urllllll',checkout_session.url)
                                    return JsonResponse({"url": checkout_session.url})
                                    # return Response(nurl, status=status.HTTP_201_CREATED)                                    
                                    # try:
                                    #     checkout_session = stripe.checkout.Session.create(
                                    #         line_items=[
                                    #             {
                                    #                 # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                                    #                 'price': 'price_1NXNe9SDKmPlLj2ihiGBkdRB',
                                    #                 'quantity': 1,
                                    #             },
                                    #         ],
                                    #         mode='payment',
                                    #         success_url=p_redirect_url,
                                    #         cancel_url=p_cancel_url,
                                    #     )
                                    # except Exception as e:
                                    #     print('----------------eeeeeeeeeeeeee',e)
                                    #     return str(e)
                                    # print('=================',checkout_session)
                                    # print('=================urllllll',checkout_session.url)
                                    # aaa=str(checkout_session.url)
                                    # print('------------------4343',type(aaa))
                                    # print('------------------4222222',checkout_session['url'])
                                    # return Response(aaa,status=status.HTTP_201_CREATED)
                                    
                                    




                            
                             
                    else:
                        return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)




    # def get(self, request, format=None):
    #   user=request.user       
    #   data=planinvoiceuserwise.objects.filter(user_id=user.id,is_latest_invoice=True)
    #   dataa=planinvoiceuserwiseSerializer(data,many=True)

    #   return Response(dataa.data,status=status.HTTP_201_CREATED)

    def get(self, request, format=None):
        user=request.user       
        data=planinvoiceuserwise.objects.filter(user_id=user.id,is_latest_invoice=True)
        dataa=planinvoiceuserwiseSerializer(data,many=True)
        count=data.count()
        return Response({'data':dataa.data,'size':count},status=status.HTTP_201_CREATED)






from rest_framework.decorators import api_view,permission_classes

# @api_view(['POST'])
@permission_classes((AllowAny, ))
def TestStripepage(request,pk,cart_id,flag,temp,price,quantity,email):
    context={}
    customer_data = stripe.Customer.list(email=email).data   
    print('---------------================33',email)
    print('---------------================',customer_data)
    amountt=int(float(price))
    # if the array is empty it means the email has not been used yet  
    if len(customer_data) != 0:
    # creating customer
        customer = customer_data[0]
        extra_msg = "Customer already existed." 
        ss=stripe.PaymentMethod.list(
          customer=customer.id,
          # type="card",
        ).data
        print('-----------pay ',ss[0])
        try:
            pay=stripe.PaymentIntent.create(
            amount=amountt,
            currency='inr',
            automatic_payment_methods={"enabled": True},
            customer=customer.id,
            payment_method=ss[0].id,
            off_session=True,
            confirm=True,
            )
            print('--------------uiuiuuiupayy',pay)
            
            print('-----flag-',flag)
            cust_id=customer.id
            pay_id=pay.id
            if flag=='dvd':
                p_redirect_url='https://stage.docullyvdr.com/projectName/newplandvd_payment/'+str(temp)+'/'+str(quantity)+'/'

            elif flag=='manual':

                p_redirect_url=f'https://stage.docullyvdr.com/projectName/manualrenewal/{str(temp)}/?cust_id={cust_id}&pay_id={pay_id}&cart_id={cart_id}'

            else:
                if flag=='True':
                    # p_cancel_url = 'http://20.198.98.31/#/manage-subscription/'+str(data.get('oldplanid'))+'/end'
                    p_redirect_url = f"https://stage.docullyvdr.com/projectName/newplan_payment/{str(temp)}/846633/?cust_id={cust_id}&pay_id={pay_id}&cart_id={cart_id}"


                else:
                    # p_cancel_url = 'http://20.198.98.31/#/billing-term/end'
                    p_redirect_url = f'https://stage.docullyvdr.com/projectName/newplan_payment/{str(temp)}/674653/?cust_id={cust_id}&pay_id={pay_id}&cart_id={cart_id}'
        # except:
        except stripe   .error.CardError as e:
            err = e.error
            # Error code will be authentication_required if authentication is needed
            print("Code is:00000000000000 %s" % err.code)
            payment_intent_id = err.payment_intent['id']
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if flag=='dvd':
                p_redirect_url = 'https://stage.docullyvdr.com/#/manage-subscription/'+str(pk)+'/dvdFail'
            elif flag=='manual':
                temp=1234-int(pk)
                p_redirect_url = 'https://stage.docullyvdr.com/#/manage-subscription/'+str(pk)+'/overdueFail'

            else:
                if flag=='True':
                    p_redirect_url='https://stage.docullyvdr.com/#/manage-subscription/'+str(pk)+'/end'
                else:
                    p_redirect_url='https://stage.docullyvdr.com/#/billing-term/end'
                
    return redirect(p_redirect_url,status=status.HTTP_201_CREATED)
    # email='varun.k@axat-tech.com'
    # customer_data = stripe.Customer.list(email=email).data   
    # # print('---------------================',customer_data)
    # # if the array is empty it means the email has not been used yet  
    # if len(customer_data) == 0:
    # # creating customer
    #     customer = stripe.Customer.create(
    #     # email=email, payment_method=payment_method_id)  
    #     email=email)  
    # else:
    #     customer = customer_data[0]
    #     extra_msg = "Customer already existed."  

    # pri=int(float(price))
    # # print('customer------c',customer)
    # # Create a PaymentIntent with the order amount and currency
    # intent = stripe.PaymentIntent.create(
    #     customer=customer['id'],
    #     # description="Software development services",
    #     # shipping={
    #     # "name": "var",
    #     # "address": {
    #     # "line1": "sss",
    #     # "postal_code": "421305",
    #     # "city": "bwd",
    #     # "state": "Maharashtra",
    #     # "country": "India",
    #     # },
    #     # },
    #     amount=pri,
    #     currency='inr',
    #     automatic_payment_methods={
    #         'enabled': True,
    #     },
    # )
    # return Response({
    #     'clientSecret': intent['client_secret']
    # })
    
    



# @permission_classes((AllowAny, ))
# def TestStripepage11(request):
#     print('-----',request.url)
#     return Response(status=status.HTTP_200_OK)

def stripetest(request,pk,cart_id,flag,temp,price,quantity,email):
    print('---------------================22',email)
    context={}
    context['pk']=pk
    context['flag']=flag
    context['temp']=temp
    context['price']=price
    context['quantity']=quantity
    context['email']=email
    context['cart_id']=cart_id
    return render(request,'sss1.html',context)





@permission_classes((AllowAny, ))
def TestStripe(request,pk,cart_id,flag,temp,price,quantity,email):
    context={}
    # email=request.user.email
    print('---------------================11',email)
    customer_data = stripe.Customer.list(email=email).data   
    print('---------------================',customer_data)
    # if the array is empty it means the email has not been used yet  
    if len(customer_data) == 0:
    # creating customer
        customer = stripe.Customer.create(
        # email=email, payment_method=payment_method_id)  
        email=email)  
    else:
        customer = customer_data[0]
        extra_msg = "Customer already existed."  

    print('-------------csutomer id',customer.id)


    intent=stripe.SetupIntent.create(
      customer=customer.id,
      automatic_payment_methods={"enabled": True},
    )
    context['client_secret']=intent['client_secret']
    context['pk']=pk
    context['flag']=flag
    context['temp']=temp
    context['price']=price
    context['quantity']=quantity
    context['email']=email
    context['cart_id']=cart_id

    return render(request,'sss.html', context)

# # class TestStripe(APIView):
# #     # permission_classes = [permissions.AllowAny]
#     # # def post(self,request,format=None):
#     # test_payment_intent = stripe.PaymentIntent.create(
#     # amount=1000, currency='aed', 
#     # payment_method_types=['card'],
#     # receipt_email='test@example.com')
#     # return Response(status=status.HTTP_200_OK, data=test_payment_intent)
#     data = request.data
#     prints('----------',data)
#     email = data['email']
#     # email = 'test333@gmail.com'
#     payment_method_id = data['payment_method_id']
# #     extra_msg = '' # add new variable to response message  # checking if customer with provided email already exists
#     customer_data = stripe.Customer.list(email=email).data   
#     print('---------------================',customer_data)
#     # if the array is empty it means the email has not been used yet  
#     if len(customer_data) == 0:
#     # creating customer
#         customer = stripe.Customer.create(
#         email=email, payment_method=payment_method_id)  
        
#     else:
#         customer = customer_data[0]
#         extra_msg = "Customer already existed."  
    
# #     print('-----custt1111',customer)
#     # print('-----custt',stripe.Customer.list(limit=3).data)
#     ss=stripe.PaymentIntent.create(
#     customer=customer, 
#     payment_method=payment_method_id,  
#     currency='aed', # you can provide any currency you want
#     amount=1100,confirm=True)  
#     # return Response(status=status.HTTP_200_OK, data={'message': 'Success', 'data': {
#     #   'customer_id': customer.id, 'extra_msg': extra_msg}
#     # })
#     print('----------------',ss)
#     return Response(status=status.HTTP_200_OK)

    # data = request.data
    # # data = json.loads(request.data)
    # print('----------',data)
    # email="testtest12334300@gmail.com"
    # customer_data = stripe.Customer.list(email=email).data   
    # print('---------------================',customer_data)
    # # if the array is empty it means the email has not been used yet  
    # if len(customer_data) == 0:
    # # creating customer
    #     customer = stripe.Customer.create(
    #     # email=email, payment_method=payment_method_id)  
    #     email=email)  
    # else:
    #     customer = customer_data[0]
    #     extra_msg = "Customer already existed."  


    # # print('customer------c',customer)
    # # Create a PaymentIntent with the order amount and currency
    # intent = stripe.PaymentIntent.create(
    #     customer=customer['id'],
    #     # description="Software development services",
    #     # shipping={
    #     # "name": "var",
    #     # "address": {
    #     # "line1": "sss",
    #     # "postal_code": "421305",
    #     # "city": "bwd",
    #     # "state": "Maharashtra",
    #     # "country": "India",
    #     # },
    #     # },
    #     amount=1100,
    #     currency='inr',
    #     automatic_payment_methods={
    #         'enabled': True,
    #     },
    # )
    # return Response({
    #     'clientSecret': intent['client_secret']
    # })
    # email=request.user.email
    # customer_data = stripe.Customer.list(email=email).data   
    # print('---------------================',customer_data)
    # # if the array is empty it means the email has not been used yet  
    # if len(customer_data) == 0:
    # # creating customer
    #     customer = stripe.Customer.create(
    #     # email=email, payment_method=payment_method_id)  
    #     email=email)  
    # else:
    #     customer = customer_data[0]
    #     extra_msg = "Customer already existed."  


    # # print('customer------c',customer)
    # # Create a PaymentIntent with the order amount and currency
    # intent = stripe.PaymentIntent.create(
    #     customer=customer['id'],
    #     # description="Software development services",
    #     # shipping={
    #     # "name": "var",
    #     # "address": {
    #     # "line1": "sss",
    #     # "postal_code": "421305",
    #     # "city": "bwd",
    #     # "state": "Maharashtra",
    #     # "country": "India",
    #     # },
    #     # },
    #     amount=1100,
    #     currency='inr',
    #     automatic_payment_methods={
    #         'enabled': True,
    #     },
    # )
    # path='http://20.198.98.31/projectName/newplan_payment/'














    # context={}
    # print('-----flag-',flag)
    # if flag=='dvd':
    #     p_redirect_url='http://20.198.98.31/projectName/newplandvd_payment/'+str(temp)+'/'+str(quantity)+'/'

    # elif flag=='manual':

    #     p_redirect_url='http://20.198.98.31/projectName/manualrenewal/'+str(temp)+'/'

    # else:
    #     if flag=='True':
    #         # p_cancel_url = 'http://20.198.98.31/#/manage-subscription/'+str(data.get('oldplanid'))+'/end'
    #         p_redirect_url = 'http://20.198.98.31/projectName/newplan_payment/'+str(temp)+'/846633/'


    #     else:
    #         # p_cancel_url = 'http://20.198.98.31/#/billing-term/end'
    #         p_redirect_url = 'http://20.198.98.31/projectName/newplan_payment/'+str(temp)+'/674653/'

    #     # return Response({
    #     #     'clientSecret': intent['client_secret'],'rdurl':p_redirect_url
    #     # })
        
    # context['rdurl']=p_redirect_url
    # context['price']=price
    # return render(request,"stripe_test_page.html",context)






class payment_api(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request,pk,format=None):
        pk=int(pk)+7-2111
        from datetime import date
        userinvoicedata=planinvoiceuserwise.objects.get(id=pk)
        plandataa=subscriptionplan.objects.filter(id=userinvoicedata.plan.id).first()
        ccavenuedataa=ccavenue_payment_cartids.objects.filter(new_plan_id=pk).last()
        user=User.objects.get(id=userinvoicedata.user.id)
        teams = MyTeams()
        teams.team_name = str(userinvoicedata.user.email)+' - '+str(userinvoicedata.project_name)
        teams.dataroom_allowed = 1
        teams.dataroom_admin_allowed = 25
        teams.dataroom_storage_allowed = int(plandataa.storage)
        teams.team_created_by_id = user.id
        teams.user_id = user.id
        teams.onlinesubscriber=True
        # teams.start_date = date.today()
        import datetime
        userinvoicedata.start_date=datetime.datetime.now()
        userinvoicedata.is_latest_invoice=True
        userinvoicedata.is_plan_active=True
        userinvoicedata.auto_renewal=True
        userinvoicedata.payment_complete=True
        userinvoicedata.ccavenue_cartid=ccavenuedataa.id
        userinvoicedata.payment_option='online'
        userinvoicedata.paid_at=datetime.datetime.now()
        if plandataa.term.lower()=='monthly':
            teams.end_date = date.today() + datetime.timedelta(days=30)
            userinvoicedata.end_date=datetime.datetime.combine(date.today(), datetime.time(23, 59))+datetime.timedelta(days=30)
        elif plandataa.term.lower()=='quarterly':
            teams.end_date = date.today() + datetime.timedelta(days=90)
            userinvoicedata.end_date=datetime.datetime.now() + datetime.timedelta(days=90)
        elif plandataa.term.lower()=='annually' or plandataa.term.lower()=='yearly':
            teams.end_date = date.today() + datetime.timedelta(days=365)
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
        userinvoicedata=planinvoiceuserwise.objects.get(id=pk)
        if userinvoicedata.company_name is not None or False:
                User.objects.filter(id=user.id).update(company_name=userinvoicedata.company_name)
        utils.send_subscription_email(subject= 'Your Docully Subscription - Activated', to =user.email.lower(), first_name = user.first_name, data =userinvoicedata,projectname=userinvoicedata.project_name)
        utils.send_mail_to_superadmin(subject= 'User Activity- Paid subscription #'+str(dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =userinvoicedata,addondata=0,projectname=userinvoicedata.project_name,payment_reference=ccavenuedataa.ref_id,upgradef=rflag,quantityflag=0)                    
        User.objects.filter(id=user.id).update(paid_subscription=True)
        ccavenue_payment_cartids.objects.filter(new_plan_id=userinvoicedata.id).update(is_new_plan=True,new_plan_id=userinvoicedata.id,is_payment_done=True) 
        ccavenuedataa=ccavenue_payment_cartids.objects.get(new_plan_id=userinvoicedata.id)
        # url = "https://accounts.zoho.com/oauth/v2/token"

        # payload = 'refresh_token=1000.6ff64f5c33f604d0969683ed84701772.28ac1ba0255435b0f3c3faadf928362a&client_id=1000.ST9XGX4LSA0JI9WDZN9BMA3QY4WS1M&client_secret=313a88810dd3ab38bbd42088ee24d43a7c86313d3e&redirect_uri=https%3A%2F%2Fservices.docullyvdr.com&grant_type=refresh_token'
        # headers = {
        #   'Content-Type': 'application/x-www-form-urlencoded',
        #   'Cookie': 'JSESSIONID=2AE2AA1795AB74B4B281E49ED15AC764; _zcsr_tmp=8eb94bb9-8a2a-4c31-8529-7557497f81b6; b266a5bf57=dcb92d0f99dd7421201f8dc746d54606; iamcsr=8eb94bb9-8a2a-4c31-8529-7557497f81b6'
        # }

        # response = requests.request("POST", url, headers=headers, data=payload)
        # result = json.loads(response.text)
        # print('0000000000000000',result)
        # # for i in result:

        # ss=result['access_token']
        # acc_token=f"Zoho-oauthtoken {ss}"
        # print('-------',acc_token)
        import datetime
        #1111111111111111111111        

        url = "https://accounts.zoho.com/oauth/v2/token"

        payload = 'refresh_token=1000.6ff64f5c33f604d0969683ed84701772.28ac1ba0255435b0f3c3faadf928362a&client_id=1000.ST9XGX4LSA0JI9WDZN9BMA3QY4WS1M&client_secret=313a88810dd3ab38bbd42088ee24d43a7c86313d3e&redirect_uri=https%3A%2F%2Fservices.docullyvdr.com&grant_type=refresh_token'
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Cookie': 'JSESSIONID=2AE2AA1795AB74B4B281E49ED15AC764; _zcsr_tmp=8eb94bb9-8a2a-4c31-8529-7557497f81b6; b266a5bf57=dcb92d0f99dd7421201f8dc746d54606; iamcsr=8eb94bb9-8a2a-4c31-8529-7557497f81b6'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(response.text)
        print('0000000000000000',result)
        # for i in result:

        ss=result['access_token']
        acc_token=f"Zoho-oauthtoken {ss}"
        print('-------',acc_token)

        url2 = "https://www.zohoapis.com/subscriptions/v1/customers"

        payload2 = {}
        headers2 = {
          'Authorization': acc_token,
          'X-com-zoho-subscriptions-organizationid': '775478479',
          'Cookie': 'JSESSIONID=AA5DFCB8E0E9E978463A4BC45B384238; _zcsr_tmp=9b0a216a-47f8-455f-87c8-0c6de1c41c12; a8c51ae498=74c37202fabd2a0575d7d0ff3f946a89; zsmcscook=9b0a216a-47f8-455f-87c8-0c6de1c41c12'
        }

        response2 = requests.request("GET", url2, headers=headers2, data=payload2)
        rr2= json.loads(response2.text)
        print('-------33',rr2)
        flag=False
        for ij in rr2['customers']:
            print('------------',ij['email'])
            if ij['email'] == user.email:
                print('--------------------------------------------------------------------------------------------')
                flag = True
                display_name=ij['display_name']
                first_name=ij['first_name']
                last_name=ij['last_name']
                email=ij['email']
                customer_id=ij['customer_id']

        date1=datetime.date.today()
        if flag==False:
            


            url3 = "https://www.zohoapis.com/subscriptions/v1/customers"

            payload3 = json.dumps({
              "display_name": user.email,
              "first_name": user.first_name,
              "last_name": user.last_name,
              "email": user.email,
              # "phone": 9090909990,
              # "mobile": 9090909090
            })
            headers3 = {
              'Authorization': acc_token,
              'X-com-zoho-subscriptions-organizationid': '775478479',
              'content-type': 'application/json',
              
            }

            response3 = requests.request("POST", url3, headers=headers3, data=payload3)
            rr3= json.loads(response3.text)
            print('-------33',rr3)
            print('3333333355555555555555------',response3.text)

#subscription===========================
            
            url1 = "https://www.zohoapis.com/subscriptions/v1/subscriptions"
            dd=rr3['customer']['display_name']
            ff=rr3['customer']['first_name']
            ll=rr3['customer']['last_name']
            ee=rr3['customer']['email']
            cc=rr3['customer']['customer_id']
            
            print('------------dareeee',date1)
            payload1=json.dumps({"add_to_unbilled_charges": True,
                    "customer": {"display_name": f"{dd}",
                    "first_name": f"{ff}",        
                    "last_name": f"{ll}",       
                    "email": f"{ee}",        
                    },
                    "customer_id": cc,
                    "starts_at": f"{date1}",
                    "plan": {"plan_code": "Mini",
                    "plan_description": "Includes 01 GB Storage & Unlimited Users",
                    "price": 1110.00,
                    "setup_fee": 0,
                    "quantity": 1 },
                    "auto_collect":False})



       
            headers1 = {
              'Authorization': acc_token,
              'X-com-zoho-subscriptions-organizationid': '775478479',
              'content-type': 'application/json'
              
            }

            response1 = requests.request("POST", url1, headers=headers1, data=payload1)

            print('last responseee------------',response1.text)
        else:
            #subscription11===========================

            url1 = "https://www.zohoapis.com/subscriptions/v1/subscriptions"

            payload1 = json.dumps({
              "add_to_unbilled_charges": True,
              "customer": {
                "display_name":display_name ,
                # "salutation": salutation,
                "first_name": first_name,
                "last_name":last_name,
                "email": email,
               
              },
              "customer_id": customer_id,
              "starts_at": f"{date1}",
              "plan": {
                "plan_code": "Mini",
                "plan_description": "Includes 01 GB Storage & Unlimited Users",
                "price": 1110,
                "setup_fee": 0,
                "quantity": 1
              },
              "auto_collect": False
            })
            headers1 = {
              'Authorization': acc_token,
              'X-com-zoho-subscriptions-organizationid': '775478479',
              'content-type': 'application/json'
              
            }

            response1 = requests.request("POST", url1, headers=headers1, data=payload1)

            # print(response.text)
            print('last responseee------------',response1.text)



        if rflag==1:
            return redirect('https://stage.docullyvdr.com/#/manage-subscription/'+str(pk)+'/start', status=status.HTTP_201_CREATED)
        else:
            # return redirect('https://services.docullyvdr.com/#/payment-successful/'+str(ccavenuedataa.ref_id), status=status.HTTP_201_CREATED)
            return redirect('https://stage.docullyvdr.com/#/payment-successful/success', status=status.HTTP_201_CREATED)



class zoho_plan(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self,request,format=None):

        url = "https://accounts.zoho.com/oauth/v2/token"

        payload = 'refresh_token=1000.6ff64f5c33f604d0969683ed84701772.28ac1ba0255435b0f3c3faadf928362a&client_id=1000.ST9XGX4LSA0JI9WDZN9BMA3QY4WS1M&client_secret=313a88810dd3ab38bbd42088ee24d43a7c86313d3e&redirect_uri=https%3A%2F%2Fservices.docullyvdr.com&grant_type=refresh_token'
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Cookie': 'JSESSIONID=2AE2AA1795AB74B4B281E49ED15AC764; _zcsr_tmp=8eb94bb9-8a2a-4c31-8529-7557497f81b6; b266a5bf57=dcb92d0f99dd7421201f8dc746d54606; iamcsr=8eb94bb9-8a2a-4c31-8529-7557497f81b6'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(response.text)
        print('0000000000000000',result)
        # for i in result:

        ss=result['access_token']
        acc_token=f"Zoho-oauthtoken {ss}"
        print('-------',acc_token)



        url1 = "https://www.zohoapis.com/subscriptions/v1/plans"

        payload1 = {}
        headers1 = {
          'Authorization': acc_token,
          'X-com-zoho-subscriptions-organizationid': '775478479'
        }

        response1 = requests.request("GET", url1, headers=headers1, data=payload1)
        res1= json.loads(response1.text)
        print('-------',res1) 
        return Response(res1,status=status.HTTP_201_CREATED)




from random import randrange
    
class Generate_otp(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self,request,pk,format=None):
        # username = request.data['username']
        # user = request.user.id
        # otp = request.data['otp']
        num = randrange(100000, 1000000)
        otp_model.objects.create(dataroom_id=pk,user=request.user,otp=num)
        name = Dataroom.objects.get(id=pk).dataroom_nameFront
        utils.send_otp_email(subject= f'OTP (One Time Password) for accessing {name} on DocullyVDR',first_name=request.user.first_name,last_name=request.user.last_name, to =request.user.email.lower(), otp =num,name=name)
        return Response(status=status.HTTP_201_CREATED) 
        

from datetime import datetime, timedelta
class Verify_otp(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self,request,pk,format=None):
        user = request.user.id
        otp = request.data['otp']
        print('------------otpppp-----------',otp)
        otp_obj=otp_model.objects.filter(dataroom_id=pk,user=request.user).last()
        minus_time=otp_obj.created+timedelta(seconds=61)
        print('------------otpppp----------111111-',otp_obj.otp)
        if int(otp_obj.otp)==int(otp):
            if datetime.now() <= minus_time:
                return Response('OTP verified successfully.',status=status.HTTP_201_CREATED) 
            else:
                return Response('OTP has expired. Request a new OTP.',status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response('Incorrect OTP',status=status.HTTP_400_BAD_REQUEST) 






def zoho_custom_plan(request):
    return render(request,"zoho_custom_plan1.html")

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
        data=subscriptionplan.objects.filter(planstatus=True,is_deleted=False)
        dataa=subscriptionplanSerializer(data,many=True)
        data=dataa.data
        for i in data:
            if i['name']=='PRO':
                i['price_id']='price_1QexfEKwlmjvMtQcckBojQ1d'
            elif i['name']=='LITE':
                i['price_id']='price_1QmDa0KwlmjvMtQcNqpkgHem'
        return Response(data)

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
        import datetime
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).exists():
            data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).first()
            dataa=planinvoiceuserwiseSerializer(data,many=False)
            data11=dataa.data
            if 'trial' in data.plan.name.lower() or data.cancel_at_monthend==True:
                data11['auto_renewal_date']=''
            else:
                # data11['auto_renewal_date']=data.end_date + datetime.timedelta(days=1)
                data11['auto_renewal_date']=data.end_date
                try:
                    dateobject=datetime.datetime.strptime(str(data11['auto_renewal_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                except:
                    dateobject=datetime.datetime.strptime(str(data11['auto_renewal_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
                data11['auto_renewal_date']=dateobject.strftime("%d/%m/%Y")
            data11['s_addoncount']=len(data.addon_plans.all())
            data11['d_addoncount']=len(data.dvd_addon_plans.all())
            try:
                dateobject=datetime.datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            except:
                dateobject=datetime.datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')

            data11['created_date']=dateobject.strftime("%d/%m/%Y")
            try:
                dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                data11['start_date']=dateobject.strftime("%d/%m/%Y")
            except:
                dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
                data11['start_date']=dateobject.strftime("%d/%m/%Y")
            try:
                dateobject=datetime.datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            except:
                dateobject=datetime.datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
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
                # data11['auto_renewal_date']=data.end_date + datetime.timedelta(days=1)
                data11['auto_renewal_date']=data.end_date

                dateobject=datetime.datetime.strptime(str(data11['auto_renewal_date']).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                data11['auto_renewal_date']=dateobject.strftime("%d/%m/%Y")            
            data11['s_addoncount']=len(data.addon_plans.all())
            data11['d_addoncount']=len(data.dvd_addon_plans.all())
            dateobject=datetime.datetime.strptime(str(data.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['created_date']=dateobject.strftime("%d/%m/%Y")
            try:
                dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                data11['start_date']=dateobject.strftime("%d/%m/%Y")
            except:
                dateobject=datetime.datetime.strptime(str(data.start_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S')
                data11['start_date']=dateobject.strftime("%d/%m/%Y")
            dateobject=datetime.datetime.strptime(str(data.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
            data11['end_date']=dateobject.strftime("%d/%m/%Y")

            return Response(data11,status=status.HTTP_201_CREATED)

        else:

            return Response('false',status=status.HTTP_400_BAD_REQUEST)


# class addon_dvd_post(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )  

#   def post(self, request,pk, format=None):
#       user=request.user
#       data=request.data 
#       # pk=data.get('pid')

#       obj=dvd_addon_invoiceuserwise()
#       obj.user_id=user.id
#       obj.dvd_addon_plan_id=dvd_addon_plans.objects.filter().first().id
#       obj.dataroom_id=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first().dataroom.id
#       obj.quantity=int(data.get('dvd_quantity'))
#       obj.total_cost=int(data.get('total_cost'))
#       obj.save()

#       plandata1=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
#       plandata1.dvd_addon_plans.add(obj)
#       plandata1.save()

#       data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
#       dataa=planinvoiceuserwiseSerializer(data,many=False)
#       utils.dvd_addon_request(subject= 'Data DVD request', to =user.email.lower(), first_name = user.first_name, data =obj)
#       utils.send_mail_to_superadmin(subject= 'User Activity- Data DVD #'+str(data.dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =data,addondata=obj,projectname=data.project_name,payment_reference='',upgradef=0,quantityflag=1)                    
#       return Response(dataa.data)


class addon_dvd_post(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def post(self, request,pk, format=None):
        user=request.user
        data=request.data 
        # pk=data.get('pid')
        cart_id_obj=ccavenue_payment_cartids()
        cart_id_obj.user_id=user.id
        cart_id_obj.is_DVD_addon=True
        cart_id_obj.save()

        tempidd=pk
        p_merchant_id = '48133'
        p_order_id = str(cart_id_obj.id)
        p_currency = 'AED'
        p_amount = str(float(data.get('total_cost'))*3.67)
        p_redirect_url = 'https://stage.docullyvdr.com/projectName/newplandvd_payment/'+str(pk)+'/'+str(int(data.get('dvd_quantity'))+12345)+'/'
        p_language = 'EN'

        # access_code='AVXY03ID76AY64YXYA'
        # workingKey='94DEDF16E45876158DCC2ADDF67BC754'
        access_code='AVIH04JJ41CN55HINC'
        workingKey='BE768C208260B6EE9FC6223E5392D727'
        p_cancel_url = 'https://stage.docullyvdr.com/#/manage-subscription/'+str(pk)+'/dvdFail'

                                
        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency="+p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&response_type=JSON'
        encryption = encrypt(merchant_data,workingKey)
        # newurl="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction&merchant_id="+p_merchant_id+"&encRequest="+encryption+"&access_code="+access_code
        newurl='https://stage.docullyvdr.com/projectName/teststripe/'+str(pk)+'/'+str(cart_id_obj.id)+'/'+str('dvd')+'/'+str(pk)+'/'+str(p_amount)+'/'+str(int(data.get('dvd_quantity'))+12345)+'/'
        return Response(newurl, status=status.HTTP_201_CREATED)                                    


class dvd_addon_pay(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request,planid,cartid,dvd_quantity,amount,format=None):
        pk=planid
        plandata1=planinvoiceuserwise.objects.filter(id=pk).first()
        user=User.objects.filter(id=plandata1.user.id).first()

        obj=dvd_addon_invoiceuserwise()
        obj.user_id=user.id
        obj.dvd_addon_plan_id=dvd_addon_plans.objects.filter().first().id
        obj.dataroom_id=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first().dataroom.id
        obj.quantity=int(dvd_quantity)
        obj.total_cost=int(amount)
        obj.is_payment_done=True
        # obj.ccavenue_cartid=cartid
        obj.planid=pk
        obj.save()

        plandata1=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        plandata1.dvd_addon_plans.add(obj)
        plandata1.save()
        ccavenue_data=ccavenue_payment_cartids.objects.filter(id=cartid).last()
        data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        dataa=planinvoiceuserwiseSerializer(data,many=False)
        utils.dvd_addon_request(subject= 'Your Data DVD order on Docully for Project '+str(data.dataroom.dataroom_nameFront), to =user.email.lower(), first_name = user.first_name, data =obj,refno='1000')
        utils.send_mail_to_superadmin(subject= 'User Activity- Data DVD #'+str(data.dataroom.id), userid=user.id, first_name = user.first_name, user_email=user.email ,data =data,addondata=obj,projectname=data.project_name,payment_reference='1000',upgradef=0,quantityflag=1)                    

        ccavenue_payment_cartids.objects.filter(id=cartid).update(dvd_plan_id=obj.id,is_payment_done=True)

        return redirect('http://20.198.98.31/#/manage-subscription/'+str(pk)+'/dvdSuccess/'+str(1000))

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
            upgrade_plan_data = subscriptionplan.objects.filter(cost__gt=bought_plan.plan.cost).order_by('cost')
            result_data = subscriptionplanSerializer(upgrade_plan_data,many=True).data
            return Response(result_data,status=status.HTTP_200_OK)
        else:
            return Response({'data':'No plans for upgrade'},status=status.HTTP_204_NO_CONTENT)

class getreactivateplans(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    # permission_classes = [permissions.AllowAny]

    def get(self,request,pk):
        user = request.user
        # bought_plan = planinvoiceuserwise.objects.filter(user_id=user.id,payment_complete=True).first()
        bought_plan = planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
        if bought_plan:
            upgrade_plan_data = subscriptionplan.objects.filter()
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
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).exists():
            planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).update(is_plan_active=False,cancel_at_monthend=True,auto_renewal=False,is_cancelled=True,cancel_at=datetime.datetime.now())
            data89=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()        
            Dataroom.objects.filter(id=data89.dataroom.id).update(is_expired=True)      
            utils.send_plancancelemail_email(subject= 'Cancellation request received for your Docully Subscription', to = str(data89.user.email), first_name = data89.user.first_name, data =data89,projectname=data89.dataroom.dataroom_nameFront)
            utils.send_plancancelemail_emailtwo(subject= 'Your Docully Subscription plan has been cancelled', to = str(data89.user.email), first_name = data89.user.first_name, data =data89,projectname=data89.dataroom.dataroom_nameFront)        
            return Response('success',status=status.HTTP_201_CREATED)
        else:
            return Response('fail',status=status.HTTP_400_BAD_REQUEST)


class reactivate_user_plan(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        data89=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).last()
        if data89:
            planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).update(cancel_at_monthend=False,auto_renewal=True)
            utils.send_autorenewon_email(subject= 'Your Docully Subscription plan will now auto renew.', to =str(user.email), first_name = user.first_name, data =data89,projectname=data89.dataroom.dataroom_nameFront)
            return Response('success',status=status.HTTP_201_CREATED)
        else:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)



class userplan_stopat_monthend(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).exists():   
            planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).update(cancel_at_monthend=True,auto_renewal=False)
            data89=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True).last()
            utils.send_autorenewoff_email(subject= 'Your Docully Subscription plan will expire on ', to =str(user.email), first_name = user.first_name, data =data89,projectname=data89.dataroom.dataroom_nameFront)
            return Response('success',status=status.HTTP_201_CREATED)
        else:
            return Response('fail',status=status.HTTP_400_BAD_REQUEST)


class addon_get(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request,pk, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).exists():
            plan_data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).first()
            addon_data=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,dataroom_id=plan_data.dataroom.id)
            addon_dataa=addon_plan_invoiceuserwiseSerializer(addon_data,many=True).data
            count=len(addon_dataa)
            return Response({'data': addon_dataa,'size':count},status=status.HTTP_201_CREATED)
        else:
            return Response(None,status=status.HTTP_201_CREATED)


class invoice_history(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self,request,pk, format=None):
        user=request.user
        dataa=[]
        count=0
        

        if planinvoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,payment_complete=True).exists():
            plan_data=planinvoiceuserwise.objects.filter(user_id=user.id,payment_complete=True,dataroom_id=pk)
            dataa.extend(planinvoiceuserwiseSerializer(plan_data,many=True).data)
            count=len(planinvoiceuserwiseSerializer(plan_data,many=True).data)+count

        if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,is_renewal=False).exists():
            addon_data=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,is_renewal=False)
            dataa.extend(addon_plan_invoiceuserwiseSerializer(addon_data,many=True).data)
            count=len(addon_plan_invoiceuserwiseSerializer(addon_data,many=True).data)+count

        if dvd_addon_invoiceuserwise.objects.filter(user_id=user.id,dataroom_id=pk,is_payment_done=True).exists():
            dvdaddon_data=dvd_addon_invoiceuserwise.objects.filter(user_id=user.id,is_payment_done=True,dataroom_id=pk)
            dataa.extend(dvd_addon_invoiceuserwiseSerializer(dvdaddon_data,many=True).data)
            count=len(dvd_addon_invoiceuserwiseSerializer(dvdaddon_data,many=True).data)+count
        dataa.sort(key=lambda item:item['created_date'], reverse=True)

        return Response({'data': dataa,'size':count},status=status.HTTP_201_CREATED)



# class invoice_historyaddon(APIView):
#   authentication_classes = (TokenAuthentication, )
#   permission_classes = (IsAuthenticated, )  

#   def get(self,request,pk, format=None):
#       user=request.user
#       if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).exists():
#           plan_data=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk)
#           dataa=planinvoiceuserwiseSerializer(plan_data,many=False).data
#           count=len(dataa)
#           return Response({'data': dataa,'size':count},status=status.HTTP_201_CREATED)
#       else:
#           return Response(None,status=status.HTTP_400_BAD_REQUEST)



class userbiilingdetails(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )  

    def get(self, request, format=None):
        user=request.user
        if planinvoiceuserwise.objects.filter(user_id=user.id,payment_complete=True).exists():
            data=planinvoiceuserwise.objects.filter(user_id=user.id,payment_complete=True).last()            
            dataa=planinvoiceuserwiseSerializer(data,many=False)        
            return Response(dataa.data,status=status.HTTP_201_CREATED)

        else:

            return Response('false',status=status.HTTP_400_BAD_REQUEST)




class export_invoice(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk, format=None):
        user=request.user
        addon_plan_invoiceuserwise.objects.filter(id=10).update(is_renewal=True)
        if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk).exists():
                dataa=planinvoiceuserwise.objects.get(user_id=user.id,id=pk)
                addondataa=addon_plan_invoiceuserwise.objects.filter(planid=str(dataa.id),is_renewal=True,is_plan_active=True,user_id=user.id).last()
                ccavenuedata=ccavenue_payment_cartids.objects.filter(new_plan_id=pk).last()
                tempid=randint(00000,99999999)
                # Importing Required Module
                from reportlab.pdfgen import canvas

                # Creating Canvas
                # c = canvas.Canvas('/home/cdms_backend/cdms2/media/fileviewcatche/invoicepdf'+str(tempid)+'.pdf',pagesize=(595,842),bottomup=0)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
                c = canvas.Canvas(response,pagesize=(595,842),bottomup=0)
                c.translate(30,120)
                c.scale(1,-1)
                c.drawImage("https://services.docullyvdr.com/assets/images/logo.png",0,40,width=200,height=50, mask='auto')


                c.scale(1,-1)
                c.translate(-30,-120)
                c.setFont("Helvetica",30)
                c.drawCentredString(480,40,"INVOICE")

                c.setFont("Helvetica-Bold",10)
                c.drawCentredString(480,60,"Docully Innovation Limited")
                c.setFont("Helvetica",10)
                c.drawCentredString(480,75,"DIFC Fintech Hive, Level 4,")
                c.drawCentredString(480,90,"Office 8 & 9, Gate District 5")
                c.drawCentredString(480,105,"Dubai, Dubai")
                c.drawCentredString(480,120,"United Arab Emirates")
                c.drawCentredString(480,145,"+971504127097")
                c.drawCentredString(480,160,"www.docully.com")


                # Line Seprating the page header from the body
                c.line(15,175,585,175)
                c.setFont("Helvetica-Bold",10)

                c.drawString(30,195,"BILL TO")
                if dataa.company_name is not None:
                    c.drawString(30,210,dataa.company_name)
                else:
                    c.drawString(30,210,dataa.user.company_name)



                c.drawCentredString(383,193,'Invoice Number:')
                c.drawCentredString(353,213,'Payment Reference Number:')
                c.drawCentredString(390,233,'Invoice Date:')
                c.drawCentredString(388,253,'Payment Due:')
                c.drawCentredString(385,273,'Plan Start Date:')
                c.drawCentredString(386,293,'Plan End Date:')
                c.drawCentredString(375,313,'Amount Due (USD):')
                

                c.drawString(30,345,'Items')
                c.drawString(250,345,'Quantity')
                c.drawString(360,345,'Price')
                c.drawString(470,345,'Amount')


                
                c.drawString(30,375,'Software Subscription Plan')







                c.drawString(430,313,'$'+str(dataa.grand_total)+'.00')








                c.setFont("Helvetica",10)
                c.drawString(30,225,str(dataa.user.first_name)+' '+str(dataa.user.last_name))
                c.drawString(30,240,str(dataa.billing_address))
                c.drawString(30,255,str(dataa.billing_city)+','+str(dataa.billing_state))
                

                c.drawString(30,390,str(dataa.plan.name)+' Plan Software Subscription')
                c.drawString(30,405,'Storage - '+str(dataa.plan.storage)+' GB')
                c.drawString(30,420,'Users - Unlimited')
                c.drawString(30,435,'Project Name - '+str(dataa.dataroom.dataroom_nameFront))
                c.drawString(30,450,'Project Id - '+str(dataa.dataroom.id))



                c.drawString(270,375,'1')
                c.drawString(360,375,'$'+str(dataa.plan.cost)+'.00')
                c.drawString(470,375,'$'+str(dataa.plan.cost)+'.00')
                


                datetodays=datetime.datetime.now().date()
                dateobject1=datetime.datetime.strptime(str(dataa.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                paymentdate=dateobject1.strftime("%Y-%m-%d")
                if 'trial' in str(dataa.plan.name).lower():
                    dateobject2=datetime.datetime.strptime(str(dataa.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                    startdate=dateobject2.strftime("%Y-%m-%d")
                else:
                    dateobject2=datetime.datetime.strptime(str(dataa.paid_at).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                    startdate=dateobject2.strftime("%Y-%m-%d")
                dateobject3=datetime.datetime.strptime(str(dataa.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                enddate=dateobject3.strftime("%Y-%m-%d")



                c.drawString(430,193,'DIL'+str(dataa.id))
                if ccavenuedata:
                    if ccavenuedata.ref_id:
                        c.drawString(430,213,str(ccavenuedata.ref_id))
                else:
                    c.drawString(430,213,'')
                c.drawString(430,233,str(datetodays))
                c.drawString(430,253,str(paymentdate))
                c.drawString(430,273,str(startdate))
                c.drawString(430,293,str(enddate))





                if dataa.po_box:
                    c.drawString(30,270,dataa.po_box)
                c.drawString(30,285,dataa.user.email)

                c.line(15,330,585,330)
                
                c.line(15,355,585,355)
                
                c.line(15,460,585,460)




                if addondataa:
                    
                        c.setFont("Helvetica-Bold",10)
                        c.drawString(296,555,'Amount Due (USD):')
                        c.drawString(470,555,'$'+str(dataa.grand_total)+'.00')
                        c.drawString(30,575,'Notes / Terms')

                        c.drawString(30,480,'Additional Storage Addon')

                        c.setFont("Helvetica",10)

                        c.drawString(30,495,'Storage - 1 GB')
                        c.drawString(270,480,str(addondataa.quantity))
                        c.drawString(360,480,'$'+str(addondataa.total_cost)+'.00')
                        c.drawString(470,480,'$'+str(addondataa.total_cost)+'.00')
                        c.line(15,510,585,510)
                        c.line(295,535,585,535)


                        c.drawString(360,525,'Total:')

                        c.drawString(470,525,'$'+str(dataa.grand_total)+'.00')




                        c.drawString(30,590,'International Wire Transfer')
                        c.drawString(30,610,'Account Name - Docully Innovation Limited')
                        c.drawString(30,625,'Bank Name - Mashreq Bank')
                        c.drawString(30,640,'Account number - 019100399219')
                        c.drawString(30,655,'Account Type - Current')
                        c.drawString(30,670,'Swift Code - BOMLAEAD')
                        c.drawString(30,685,'Swift Routing Code: 203320101')
                        c.drawString(30,700,'IBAN - A E 9 4 0 3 * * * * * * * * * * 0 3 9 9 2 1 9')
                        c.drawString(150,800,'This is a system generated document. Does not require a signature.')






                else:

                    c.drawString(360,480,'Total:')

                    c.drawString(470,480,'$'+str(dataa.grand_total)+'.00')
                    c.line(295,495,585,495)

                    c.drawString(470,515,'$'+str(dataa.grand_total)+'.00')

                    c.drawString(296,515,'Amount Due (USD):')

                    c.drawString(30,550,'Notes / Terms')

                    c.drawString(30,565,'International Wire Transfer')
                    c.drawString(30,585,'Account Name - Docully Innovation Limited')
                    c.drawString(30,600,'Bank Name - Mashreq Bank')
                    c.drawString(30,615,'Account number - 019100399219')
                    c.drawString(30,630,'Account Type - Current')
                    c.drawString(30,645,'Swift Code - BOMLAEAD')
                    c.drawString(30,660,'Swift Routing Code: 203320101')
                    c.drawString(30,675,'IBAN - A E 9 4 0 3 * * * * * * * * * * 0 3 9 9 2 1 9')
                    c.drawString(150,800,'This is a system generated document. Does not require a signature.')
                    


                c.showPage()
                c.save()
                return response

        else:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)





class exportaddondvd_invoice(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk, format=None):
        user=request.user
        if dvd_addon_invoiceuserwise.objects.filter(user_id=user.id,id=pk).exists():
                addondataa=dvd_addon_invoiceuserwise.objects.filter(user_id=user.id,id=pk).last()
                dataa=planinvoiceuserwise.objects.filter(id=addondataa.planid).last()
                ccavenuedata=ccavenue_payment_cartids.objects.filter(dvd_plan_id=pk).last()
                # Importing Required Module
                from reportlab.pdfgen import canvas

                # Creating Canvas
                # c = canvas.Canvas('/home/cdms_backend/cdms2/media/fileviewcatche/invoicepdf'+str(tempid)+'.pdf',pagesize=(595,842),bottomup=0)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=invoice_'+str(dataa.dataroom.dataroom_name)+'.pdf'
                c = canvas.Canvas(response,pagesize=(595,842),bottomup=0)
                c.translate(30,120)
                c.scale(1,-1)
                c.drawImage("https://services.docullyvdr.com/assets/images/logo.png",0,40,width=200,height=50, mask='auto')


                c.scale(1,-1)
                c.translate(-30,-120)
                c.setFont("Helvetica",30)
                c.drawCentredString(480,40,"INVOICE")

                c.setFont("Helvetica-Bold",10)
                c.drawCentredString(480,60,"Docully Innovation Limited")
                c.setFont("Helvetica",10)
                c.drawCentredString(480,75,"DIFC Fintech Hive, Level 4,")
                c.drawCentredString(480,90,"Office 8 & 9, Gate District 5")
                c.drawCentredString(480,105,"Dubai, Dubai")
                c.drawCentredString(480,120,"United Arab Emirates")
                c.drawCentredString(480,145,"+971504127097")
                c.drawCentredString(480,160,"www.docully.com")


                # Line Seprating the page header from the body
                c.line(15,175,585,175)
                c.setFont("Helvetica-Bold",10)

                c.drawString(30,195,"BILL TO")
                if dataa.user.company_name != None:
                    c.drawString(30,210,dataa.user.company_name)
                else:
                    c.drawString(30,210,'')



                c.drawCentredString(383,193,'Invoice Number:')
                c.drawCentredString(353,213,'Payment Reference Number:')
                c.drawCentredString(390,233,'Invoice Date:')
                c.drawCentredString(388,253,'Payment Due:')

                c.drawCentredString(375,273,'Amount Due (USD):')
                

                c.drawString(30,320,'Items')
                c.drawString(250,320,'Quantity')
                c.drawString(360,320,'Price')
                c.drawString(470,320,'Amount')


                c.drawString(360,390,'Total:')
                
                c.drawString(30,350,'Data DVD Addon Purchase')





                c.drawString(296,420,'Amount Due (USD):')

                c.drawString(470,420,'$'+str(addondataa.total_cost)+'.00')

                c.drawString(430,273,'$'+str(addondataa.total_cost)+'.00')


                c.drawString(30,460,'Notes / Terms')






                c.setFont("Helvetica",10)
                c.drawString(30,225,str(dataa.user.first_name)+' '+str(dataa.user.last_name))
                c.drawString(30,240,str(dataa.billing_address))
                c.drawString(30,255,str(dataa.billing_city)+','+str(dataa.billing_state))
                

                c.drawString(270,350,str(addondataa.quantity))
                c.drawString(360,350,'$'+str(addondataa.total_cost)+'.00')
                c.drawString(470,350,'$'+str(addondataa.total_cost)+'.00')
                

                c.drawString(470,390,'$'+str(addondataa.total_cost)+'.00')

                datetodays=datetime.datetime.now().date()
                dateobject1=datetime.datetime.strptime(str(addondataa.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                paymentdate=dateobject1.strftime("%Y-%m-%d")




                c.drawString(430,193,'DIL'+str(addondataa.id))
                if ccavenuedata:
                    if ccavenuedata.ref_id:
                        c.drawString(430,213,str(ccavenuedata.ref_id))
                else:
                    c.drawString(430,213,'')
                c.drawString(430,233,str(datetodays))
                c.drawString(430,253,str(paymentdate))






                if dataa.po_box:
                    c.drawString(40,270,dataa.po_box)
                c.drawString(30,285,dataa.user.email)


                c.drawString(30,475,'International Wire Transfer')
                c.drawString(30,500,'Account Name - Docully Innovation Limited')
                c.drawString(30,515,'Bank Name - Mashreq Bank')
                c.drawString(30,530,'Account number - 019100399219')
                c.drawString(30,545,'Account Type - Current')
                c.drawString(30,560,'Swift Code - BOMLAEAD')
                c.drawString(30,575,'Swift Routing Code: 203320101')
                c.drawString(30,590,'IBAN - A E 9 4 0 3 * * * * * * * * * * 0 3 9 9 2 1 9')
                c.drawString(150,800,'This is a system generated document. Does not require a signature.')

                c.line(15,305,585,305)
                
                c.line(15,330,585,330)
                
                c.line(15,370,585,370)
                
                c.line(295,400,585,400)

                c.showPage()
                c.save()
                return response

        else:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)







class exportaddon_invoice(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk, format=None):
        user=request.user
        if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,id=pk,is_renewal=False).exists():
                addondataa=addon_plan_invoiceuserwise.objects.get(user_id=user.id,id=pk,is_renewal=False)
                dataa=planinvoiceuserwise.objects.filter(id=addondataa.planid).last()
                # ccavenuedata=ccavenue_payment_cartids.objects.get(new_plan_id=pk)
                # Importing Required Module
                from reportlab.pdfgen import canvas

                # Creating Canvas
                # c = canvas.Canvas('/home/cdms_backend/cdms2/media/fileviewcatche/invoicepdf'+str(tempid)+'.pdf',pagesize=(595,842),bottomup=0)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
                c = canvas.Canvas(response,pagesize=(595,842),bottomup=0)
                c.translate(30,120)
                c.scale(1,-1)
                c.drawImage("https://services.docullyvdr.com/assets/images/logo.png",0,40,width=200,height=50, mask='auto')


                c.scale(1,-1)
                c.translate(-30,-120)
                c.setFont("Helvetica",30)
                c.drawCentredString(480,40,"INVOICE")

                c.setFont("Helvetica-Bold",10)
                c.drawCentredString(480,60,"Docully Innovation Limited")
                c.setFont("Helvetica",10)
                c.drawCentredString(480,75,"DIFC Fintech Hive, Level 4,")
                c.drawCentredString(480,90,"Office 8 & 9, Gate District 5")
                c.drawCentredString(480,105,"Dubai, Dubai")
                c.drawCentredString(480,120,"United Arab Emirates")
                c.drawCentredString(480,145,"+971504127097")
                c.drawCentredString(480,160,"www.docully.com")


                # Line Seprating the page header from the body
                c.line(15,175,585,175)
                c.setFont("Helvetica-Bold",10)

                c.drawString(30,195,"BILL TO")
                if dataa.user.company_name !=None:
                    c.drawString(30,210,dataa.user.company_name)
                else:
                    c.drawString(30,210,'')



 

                c.drawCentredString(383,193,'Invoice Number:')
                c.drawCentredString(353,213,'Payment Reference Number:')
                c.drawCentredString(390,233,'Invoice Date:')
                c.drawCentredString(388,253,'Payment Due:')
                c.drawCentredString(385,273,'Plan Start Date:')
                c.drawCentredString(386,293,'Plan End Date:')
                c.drawCentredString(375,313,'Amount Due (USD):')
                

                c.drawString(30,345,'Items')
                c.drawString(250,345,'Quantity')
                c.drawString(360,345,'Price')
                c.drawString(470,345,'Amount')


                c.drawString(360,423,'Total:')
                
                c.drawString(30,373,'Additional Storage Addon')





                c.drawString(296,450,'Amount Due (USD):')

                c.drawString(470,450,'$'+str(addondataa.addon_plan.cost)+'.00')

                c.drawString(430,313,'$'+str(addondataa.addon_plan.cost)+'.00')


                c.drawString(30,470,'Notes / Terms')






                c.setFont("Helvetica",10)
                c.drawString(30,225,str(dataa.user.first_name)+' '+str(dataa.user.last_name))
                c.drawString(30,240,str(dataa.billing_address))
                c.drawString(30,255,str(dataa.billing_city)+','+str(dataa.billing_state))
                

                c.drawString(30,387,'Storage - '+str(addondataa.addon_plan.storage)+' GB')



                c.drawString(270,375,'1')
                c.drawString(360,375,'$'+str(addondataa.addon_plan.cost)+'.00')
                c.drawString(470,375,'$'+str(addondataa.addon_plan.cost)+'.00')
                

                c.drawString(470,423,'$'+str(addondataa.addon_plan.cost)+'.00')

                datetodays=datetime.datetime.now().date()
                dateobject1=datetime.datetime.strptime(str(addondataa.created_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                paymentdate=dateobject1.strftime("%Y-%m-%d")
                dateobject2=datetime.datetime.strptime(str(addondataa.paid_at).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                startdate=dateobject2.strftime("%Y-%m-%d")
                dateobject3=datetime.datetime.strptime(str(addondataa.end_date).replace('T',' ',1),'%Y-%m-%d %H:%M:%S.%f')
                enddate=dateobject3.strftime("%Y-%m-%d")



                c.drawString(430,193,'DIL'+str(addondataa.id))
                # if ccavenuedata.ref_id is not None:
                    # c.drawString(430,213,str(ccavenuedata.ref_id))
                # else:
                c.drawString(430,213,'')
                c.drawString(430,233,str(datetodays))
                c.drawString(430,253,str(paymentdate))
                c.drawString(430,273,str(startdate))
                c.drawString(430,293,str(enddate))





                if dataa.po_box:
                    c.drawString(30,270,dataa.po_box)
                c.drawString(30,285,dataa.user.email)


                c.drawString(30,485,'International Wire Transfer')
                c.drawString(30,505,'Account Name - Docully Innovation Limited')
                c.drawString(30,520,'Bank Name - Mashreq Bank')
                c.drawString(30,535,'Account number - 019100399219')
                c.drawString(30,550,'Account Type - Current')
                c.drawString(30,565,'Swift Code - BOMLAEAD')
                c.drawString(30,580,'Swift Routing Code: 203320101')
                c.drawString(30,595,'IBAN - A E 9 4 0 3 * * * * * * * * * * 0 3 9 9 2 1 9')
                c.drawString(150,800,'This is a system generated document. Does not require a signature.')

                c.line(15,330,585,330)
                
                c.line(15,355,585,355)
                
                c.line(15,406,585,406)
                
                c.line(295,435,585,435)

                c.showPage()
                c.save()
                return response

        else:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)




class payment_overdue(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,pk,format=None):
        user=request.user
        import datetime
        totalcharge=0
        totaladdon=0
        planflag=0
        addonflag=0
        extraaddon=0
        tempplan=planinvoiceuserwise.objects.filter(id=pk).first()
        if tempplan.dataroom.addon_payment_overdue==True:
            if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=pk,is_payment_done=False).exists():
                addondata=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.id,is_payment_done=False)
                for i in addondata:
                    totalcharge=int(i.total_cost)+totalcharge
                    totaladdon=totaladdon+int(i.quantity)
                    addonflag=1

        if  tempplan.dataroom.addon_payment_overdue==True or tempplan.dataroom.plan_payment_overdue==True:
            print('coming here', planinvoiceuserwiseSerializer(planinvoiceuserwise.objects.get(id=pk),many=False).data)
            if planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).exists():
                planindata=planinvoiceuserwise.objects.filter(user_id=user.id,id=pk,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).last()
                totalcharge=int(planindata.plan.cost)+totalcharge
                planflag=1
                if addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.new_invoiceid,is_payment_done=False).exists():
                    addondata=addon_plan_invoiceuserwise.objects.filter(user_id=user.id,planid=planindata.new_invoiceid,is_payment_done=False)
                    for j in addondata:
                        totalcharge=int(j.total_cost)+totalcharge
                        totaladdon=totaladdon+int(j.quantity)       
                        extraaddon=1

        print(planflag,extraaddon)

        if request.GET.get('overdueamount')=='8567':
            return Response(totalcharge,status=status.HTTP_201_CREATED)
        else:
            if totalcharge!=0:
                cart_id_obj=ccavenue_payment_cartids()
                cart_id_obj.user_id=user.id
                cart_id_obj.is_renewal=True
                if extraaddon==1 and addonflag==0:
                    cart_id_obj.is_storage_addon=True
                    cart_id_obj.storage_addon_id=addondata.id
                    cart_id_obj.new_plan_id=planindata.new_invoiceid
                elif    planflag==1 and extraaddon==0:
                    cart_id_obj.new_plan_id=planindata.new_invoiceid
                elif    planflag==0 and addonflag==1:
                    cart_id_obj.is_storage_addon=True
                    cart_id_obj.storage_addon_id=addondata.id
                
                else:
                    cart_id_obj.is_storage_addon=True
                    cart_id_obj.storage_addon_id=j.id
                    cart_id_obj.new_plan_id=planindata.new_invoiceid
                cart_id_obj.save()
                p_merchant_id = '48133'
                p_order_id = str(cart_id_obj.id)
                p_currency = 'AED'
                p_amount = str(float(totalcharge)*3.67)
                p_language = 'EN'
                # access_code='AVXY03ID76AY64YXYA'
                # workingKey='94DEDF16E45876158DCC2ADDF67BC754'
                access_code='AVIH04JJ41CN55HINC'
                workingKey='BE768C208260B6EE9FC6223E5392D727'
                tempid=1234+int(pk)
                p_cancel_url = 'http://20.198.98.31/#/manage-subscription/'+str(pk)+'/overdueFail'
                p_redirect_url = 'http://20.198.98.31/projectName/manualrenewal/'+str(tempid)+'/'
                todaysdate=datetime.datetime.now()
                todaysdate2=datetime.datetime.strptime(str(todaysdate),'%Y-%m-%d %H:%M:%S.%f')
                todaysdate3=todaysdate2.strftime("%d-%m-%Y")
                merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency="+p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&response_type=JSON&si_type=ONDEMAND&si_mer_ref_no='+p_order_id+'&si_is_setup_amt=Y&si_start_date='+str(todaysdate3)
                encryption = encrypt(merchant_data,workingKey)
                # newurl="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction&merchant_id="+p_merchant_id+"&encRequest="+encryption+"&access_code="+access_code
                nurl='http://20.198.98.31/projectName/teststripe/'+str(pk)+'/'+str(cart_id_obj.id)+'/'+str('manual')+'/'+str(tempid)+'/'+str(p_amount)+'/'+'none'+'/'
                return Response(nurl, status=status.HTTP_201_CREATED) 
                # return Response(newurl,status=status.HTTP_201_CREATED)
            else:
                return Response(None,status=status.HTTP_400_BAD_REQUEST)

                


class payment_overdue_pay(APIView):
    permission_classes = (AllowAny,)

    def get(self,request,pk,pk2,format=None):
        pk=int(pk)-1234
        import datetime
        ccdata=ccavenue_payment_cartids.objects.filter(id=pk2).last()
        if addon_plan_invoiceuserwise.objects.filter(planid=pk,is_payment_done=False).exists():
            addondata=addon_plan_invoiceuserwise.objects.filter(planid=pk,is_payment_done=False)
            for i in addondata:
                addon_plan_invoiceuserwise.objects.filter(id=i.id).update(is_payment_done=True,paid_at=datetime.datetime.now())
                plandataa=planinvoiceuserwise.objects.filter(id=pk).last()
                utils.send_mail_to_superadmin(subject= 'Data Storage Addon #'+str(i.dataroom.id), userid=i.user.id, first_name = i.user.first_name, user_email=i.user.email ,data =plandataa,addondata=i,projectname=plandataa.project_name,payment_reference='0111',upgradef=0,quantityflag=0)                      
                Dataroom.objects.filter(id=i.dataroom.id).update(addon_payment_overdue=False,is_expired=False)
        
        if planinvoiceuserwise.objects.filter(id=pk,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).exists():
            planindata=planinvoiceuserwise.objects.filter(id=pk,is_latest_invoice=True,is_plan_active=False,plan_renewed=True).last()
            planinvoiceuserwise.objects.filter(id=planindata.id).update(is_latest_invoice=False,is_plan_active=False)
            planinvoiceuserwise.objects.filter(id=planindata.new_invoiceid).update(payment_complete=True,is_latest_invoice=True,is_plan_active=True,paid_at=datetime.datetime.now())
            Dataroom.objects.filter(id=planindata.dataroom.id).update(plan_payment_overdue=False)                       
            newpladata=planinvoiceuserwise.objects.filter(id=planindata.new_invoiceid).last()
            if addon_plan_invoiceuserwise.objects.filter(user_id=planindata.user.id,planid=planindata.new_invoiceid,is_payment_done=False).exists():
                Dataroom.objects.filter(id=planindata.dataroom.id).update(addon_payment_overdue=False)                                      
                addondata=addon_plan_invoiceuserwise.objects.filter(user_id=planindata.user.id,planid=planindata.new_invoiceid,is_payment_done=False)
                for i in addondata:
                    addonid=i.id
                    addon_plan_invoiceuserwise.objects.filter(id=i.id).update(is_payment_done=True,paid_at=datetime.datetime.now())                                 
                utils.send_mail_to_superadmin(subject= 'User Activity- Plan Renewal #'+str(planindata.dataroom.id), userid=planindata.user.id, first_name = planindata.user.first_name, user_email=planindata.user.email ,data =newpladata,addondata=i,projectname=planindata.project_name,payment_reference='0111',upgradef=0,quantityflag=0)                                   
                utils.send_planrenewal_email(subject= 'Your Docully Subscription is renewed successfully', to =planindata.user.email, first_name = planindata.user.first_name, data =newpladata,projectname=planindata.dataroom.dataroom_nameFront,isaddon=True,addondata=addondata)
            
            else:
                utils.send_mail_to_superadmin(subject= 'User Activity- Plan Renewal #'+str(newpladata.dataroom.id), userid=newpladata.user.id, first_name = newpladata.user.first_name, user_email=newpladata.user.email ,data =newpladata,addondata=0,projectname=newpladata.project_name,payment_reference='0111',upgradef=0,quantityflag=0)                    
                utils.send_planrenewal_email(subject= 'Your Docully Subscription is renewed successfully', to =planindata.user.email, first_name = planindata.user.first_name, data =newpladata,projectname=planindata.dataroom.dataroom_nameFront,isaddon=False,addondata='')
            return redirect('http://20.198.98.31/#/manage-subscription/'+str(planindata.new_invoiceid)+'/overdueSuccess/'+str('ccdata.ref_id'))
        else:
            return redirect('http://20.198.98.31/#/manage-subscription/'+str(pk)+'/overdueSuccess/'+str('ccdata.ref_id'))


class dvd_plans(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,format=None):
        data=dvd_addon_plans.objects.filter(planstatus=True)
        dataa=dvd_addon_plansSerializer(data,many=True).data
        return Response(dataa,status=status.HTTP_201_CREATED)



class buttonvisibilitycheck(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self,request,format=None):
        subscription=False
        myteams=False
        Channels=False
        userid=request.user.id
        from myteams.models import chanelMembers,Mychanels,MyTeams,TeamMembers
        subscription=planinvoiceuserwise.objects.filter(user_id=userid).exists()
        if chanelMembers.objects.filter(member_id=userid).exists() or Mychanels.objects.filter(user_id=userid).exists():
            Channels=True
        if TeamMembers.objects.filter(member_id=userid).exists() or MyTeams.objects.filter(user_id=userid).exists():
            myteams=True


        return Response({'subscription':subscription,'Channels':Channels,'myteams':myteams},status=status.HTTP_201_CREATED)

class editonlinedataroomView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        data=request.data
        user = request.user
        if user.is_superadmin:
            Dataroom.objects.filter(id=data.get('dataroomid')).update(dataroom_nameFront=data.get('dataroom_nameFront'),dataroom_storage_allocated=data.get('dataroom_storage_allocated'))
            planinvoiceuserwise.objects.filter(id=data.get('planinvoiceid'),dataroom_id=data.get('dataroomid'),is_latest_invoice=True).update(end_date=data.get('end_date'),auto_renewal=data.get('auto_renewal'))
            return Response({'data':'updated successfully'}, status=status.HTTP_201_CREATED)
        return Response({'msg':'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)




from django.shortcuts import render, redirect

from .ccavutil import encrypt,decrypt
from string import Template
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
import json



class dataroomdeleteapirvgg(APIView):
    permission_classes = (AllowAny,)

    def get(self, request,format=None):
                # from .models import addon_plan_tempforsameday,addon_plan_invoiceuserwise,planinvoiceuserwise,addon_plans,subscriptionplan,ccavenue_payment_cartids,pendinginvitations
                # from dataroom.models import Dataroom,DataroomDisclaimer,Watermarking
                # from Vote.models import Vote
                # from data_documents.models import DataroomFolder
                from datetime import timedelta,datetime
                # from django.utils import timezone
                # from django.db.models import F
                # from .utils import send_mail_to_superadmin
                # from django.db.models import Count, Min, Sum, Avg
                # import requests
                # from .ccavutil import encrypt,decrypt
                # import json
                # from azure.storage.blob import BlockBlobService,PublicAccess
                # from notifications.models import AllNotifications,Notifications
                # from users_and_permission.models import DataroomGroups,DataroomMembers,DataroomGroupPermission
                # from myteams.models import MyTeams,chanelMembers
                # # dataa=MyTeams.objects.filter().last()
                # # MyTeams.objects.filter(id=dataa.id).update(onlinesubscriber=False)
                # # return redirect('https://services.docullyvdr.com/projectName/newplan_process/'+str(530)+'/')

                # # print(request.GET.get('dataroomid'))
                # # Dataroom.objects.filter(id=request.GET.get('dataroomid')).update(offlinedataroom=True)
                # # planinvoiceuserwise.objects.filter(plan_id=4,is_latest_invoice=True).update(is_plan_active=True)

                # start_datee = datetime.now()
                # end_datee = start_datee + timedelta(days=1) 
                # print('1111111111111111111111111',start_datee,end_datee,timezone.now())
                # if planinvoiceuserwise.objects.filter(end_date__lte=end_datee,auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
                #   temp_plandata1=planinvoiceuserwise.objects.filter(end_date__lte=end_datee,auto_renewal=False,is_latest_invoice=True,is_plan_active=True,is_expired=False)
                #   for j in temp_plandata1:
                #       print('0000000',j.end_date)
                #       plandataa=subscriptionplan.objects.filter(id=j.plan.id).first()
                #       planinvoiceuserwise.objects.filter(id=j.dataroom.id).update(is_plan_active=False)
                #       if 'trial' in plandataa.name.lower():
                #           print('111111')
                #           Dataroom.objects.filter(id=j.dataroom.id).update(is_expired=True,trial_expired=True)

                # return Response('done')
                # start_datee = datetime.now()
                # end_datee = start_datee + timedelta(days=1) 
                # # print('1111111111111111111111111',start_datee,end_datee,timezone.now())


                # if planinvoiceuserwise.objects.filter(end_date__lte=end_datee,cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False).exists():
                #   temp_plandata=planinvoiceuserwise.objects.filter(end_date__lte=end_datee,cancel_at_monthend=False,auto_renewal=True,is_latest_invoice=True,is_plan_active=True,is_expired=False)
                #   # print('22222222222222222222')
                #   for k in temp_plandata:
                #       print(k.id,'iiiiiiiiiiiddddddddddd')


                from azure.storage.blob import BlockBlobService,PublicAccess,ContentSettings
                container_name ='docullycontainer'
                # sas_url='?sv=2021-10-04&ss=btqf&srt=sco&st=2023-02-25T11%3A51%3A17Z&se=2024-02-25T11%3A51%3A00Z&sp=rl&sig=AWXxw55%2FTC%2BUSOIlVQC3naDahCCebIBNszSFRdqRfBc%3D'
                block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==',sas_token = sas_url)
                # block_blob_service.delete_blob(containter_name, 'images/dataroom-icon.png', snapshot=None)
                block_blob_service.create_blob_from_path(container_name,'media/images/dataroom-icon.png',"/home/cdms_backend/cdms2/mediaa/DocullyVDR_logo.png",content_settings=ContentSettings(content_type='image/png'))
                # block_blob_service.create_blob_from_path(container_name,'media/images1/dataroom-icon.png',"/home/cdms_backend/cdms2/mediaa/dataroom-icon.png",content_settings=ContentSettings(content_type='image/png'))

                return HttpResponse('---doene')

                # from dataroom.models import DataroomView
                # print('hio')
                # data=DataroomView.objects.filter(dataroom_id=584).last()
                # DataroomView.objects.filter(id=data.id).delete()
                # # dataa=DataroomSerializer(data,many=False).data

                # return Response(data.id)
                # planinvoiceuserwise.objects.filter(id=575).update(plan_id=2,end_date=datetime.now()+timedelta(days=26))


                # # os.chdir("/home/cdms_backend/cdms2")
                # if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(178)+".pdf"):
                #   os.remove("/home/cdms_backend/cdms2/Admin_Watermark/first"+str(178)+".pdf")                 
                #   if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(178)+".pdf"):
                #       os.remove("/home/cdms_backend/cdms2/Admin_Watermark/second"+str(178)+".pdf")    
                #   if os.path.exists("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(178)+".pdf"):
                #       os.remove("/home/cdms_backend/cdms2/Admin_Watermark/third"+str(178)+".pdf") 
                #       return Response('fff')
                # DataroomFolder.objects.filter(dataroom_id=491).delete()
                # AllNotifications.objects.filter(dataroom_id=491).delete()
                # Notifications.objects.filter(dataroom_id=491).delete()
                # Watermarking.objects.filter(dataroom_id=491).delete()
                # pendinginvitations.objects.filter(dataroom_id=491).delete()
                # DataroomGroups.objects.filter(dataroom_id=491).delete()
                # DataroomMembers.objects.filter(dataroom_id=491).delete()
                # DataroomGroupPermission.objects.filter(dataroom_id=491).delete()
                # Vote.objects.filter(dataroom_id=491).delete()
@csrf_exempt
@permission_classes([AllowAny])
def newplandvd_payment(request,pk,pk1):
    # workingKey = 'BE768C208260B6EE9FC6223E5392D727'
    # encResp= request.POST.get('encResp')
    # decResp = decrypt(encResp,workingKey)

    # y = json.loads(decResp)
    # print(y['order_status'],y['tracking_id'],'0000000000000000000000000')
    # if y['order_status']=='Success':
    #     ccavenue_payment_cartids.objects.filter(id=y['order_id']).update(ref_id=y['tracking_id'],bank_ref_id=y['bank_ref_no'])
    cart_id=request.GET.get('cart_id')
    pay_id=request.GET.get('pay_id')
    cust_id=request.GET.get('cust_id')
    ccavenue_payment_cartids.objects.filter(id=cart_id).update(ref_id=cust_id,bank_ref_id=pay_id)
    pk1=int(pk1)-12345

    # total_amount=str(int(float(y['amount'])/3.67))
    total_amount=str(int(float(pk1*200)/3.67))
    return redirect('http://20.198.98.31/projectName/dvd_addon_pay/'+str(pk)+'/'+str(1000)+'/'+str(pk1)+'/'+str(total_amount)+'/')
    # else:
    #     ccavenue_payment_cartids.objects.filter(id=y['order_id']).update(ref_id=y['tracking_id'])
    #     return redirect('https://services.docullyvdr.com/#/manage-subscription/'+str(pk)+'/dvdFail')

@csrf_exempt
@permission_classes([AllowAny])
def newplan_payment(request,pk,pk1):
    # workingKey = 'BE768C208260B6EE9FC6223E5392D727'
    # encResp= request.POST.get('encResp')
    # decResp = decrypt(encResp,workingKey)
    # # print(decResp,'decResppppppppppp',type(decResp))
    # # decResp=json.dumps(decResp)
    # print(decResp,'jsondump response',type(decResp))
    # y = json.loads(decResp)
    # print(y,'yyyyyyyyyyyyyyyyyyyyyy')
    # print(y['order_status'],y['tracking_id'],y['si_created'],y['si_ref_no'],'0000000000000000000000000')

    # if y['order_status']=='Success':
    cart_id=request.GET.get('cart_id')
    pay_id=request.GET.get('pay_id')
    cust_id=request.GET.get('cust_id')

    ccavenue_payment_cartids.objects.filter(id=cart_id).update(ref_id=cust_id,bank_ref_id=pay_id)
    return redirect('http://20.198.98.31/projectName/newplan_process/'+str(pk)+'/')
    # else:
    #     ccavenue_payment_cartids.objects.filter(id=y['order_id']).update(ref_id=y['tracking_id'])
    #     if pk1=='674653':
    #         return redirect('https://services.docullyvdr.com/#/billing-term/end')
    #     else:
    #         return redirect('https://services.docullyvdr.com/#/subscription')

@csrf_exempt
@permission_classes([AllowAny])
def manualrenewal(request,pk):
    # workingKey = '94DEDF16E45876158DCC2ADDF67BC754'
    # workingKey = 'BE768C208260B6EE9FC6223E5392D727'
    # encResp= request.POST.get('encResp')
    # decResp = decrypt(encResp,workingKey)

    # y = json.loads(decResp)
    # print('-str(pk)---------',str(pk))
    # print('https://services.docullyvdr.com/#/manage-subscription/',str(pk),'/overdueFail')
    # if y['order_status']=='Success':
    cart_id=request.GET.get('cart_id')
    pay_id=request.GET.get('pay_id')
    cust_id=request.GET.get('cust_id')    
    # ccavenue_payment_cartids.objects.filter(id=y['order_id']).update(ref_id=y['tracking_id'],bank_ref_id=y['bank_ref_no'],si_ref_id=y['si_ref_no'])
    ccavenue_payment_cartids.objects.filter(id=cart_id).update(ref_id=cust_id,bank_ref_id=pay_id)
    return redirect('http://20.198.98.31/projectName/payment_overdue_pay/'+str(pk)+'/'+str(23)+'/')
    # else:
    #     pk=int(pk)-1234
    #     ccavenue_payment_cartids.objects.filter(id=y['order_id']).update(ref_id=y['tracking_id'])
    #     return redirect('https://services.docullyvdr.com/#/manage-subscription/'+str(pk)+'/overdueFail')



# {"merchant_param5":"","merchant_param4":"","merchant_param3":"","billing_name":"Harvinder Singh","merchant_param2":"","status_message":"DECLINED","si_status":"INAC","merchant_param1":"","response_type":"JSON","billing_city":"Mumbai","amount":"1.0","order_status":"Failure","billing_country":"India","billing_address":"Mumbai","bank_qsi_no":"null","discount_value":"0.0","billing_zip":"","delivery_country":"","billing_tel":"7900075531","failure_message":"","order_id":"422","bank_ref_no":"null","delivery_address":"","status_code":"62","si_ref_no":"SI2131210216878","billing_state":"","si_mer_ref_no":"422","payment_mode":"Credit Card","vault":"N","delivery_state":"","card_holder_name":"Harvinder Singh","offer_type":"null","delivery_name":"","offer_code":"null","bank_receipt_no":"null","tracking_id":"110021982741","delivery_city":"","delivery_zip":"","delivery_tel":"","currency":"AED","si_created":"Y","eci_value":"05","card_name":"Visa","billing_email":"h@docully.com","mer_amount":"1.0"}






class Time_zone_List(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        tz=TimeZonesList.objects.order_by('country').values()
        return Response(tz,status=status.HTTP_200_OK)

    def post(self, request,pk,pk1 ,format=None):
        if User_time_zone.objects.filter(user_id=pk).exists():
            User_time_zone.objects.filter(user_id=pk).update(time_zone_id=pk1)
        else:
            User_time_zone.objects.create(user_id=pk ,time_zone_id=pk1)



class Get_Stripe_Products(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        import stripe
        stripe.api_key = "sk_test_51PgWGDKwlmjvMtQc4vAA7I9FZbhCucWQPRSs4VoHMqAadpULmrAL2conK5W1nMpWd7mXzs0Xe96PSjVBfQZrBK8d00sGeO6vVh"

        # stripe_list=stripe.Product.list(limit=2)
        # for i in stripe_list

        return Response(stripe_list)


import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method=="POST":
        # try:
        print('------------------------',request.body)
        data = json.loads(request.body)
        price_id = data.get("price_id")  # Pass Pro/Lite Price ID from Angular

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="http://stage.docullyvdr.com/success_stripe?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://stage.docullyvdr.com/cancel_stripe",
        )
        print('-------------------urllllll',checkout_session.url)
        return JsonResponse({"url": checkout_session.url})
        # except Exception as e:
        #     return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
def report_usage(request):
    try:
        data = json.loads(request.body)
        subscription_item_id = data.get("subscription_item_id")  # Stripe Subscription Item ID
        extra_gb_used = data.get("extra_gb_used")  # Extra GB used

        stripe.SubscriptionItem.create_usage_record(
            subscription_item=subscription_item_id,
            quantity=extra_gb_used,
            action="increment",
        )
        return JsonResponse({"status": "Usage recorded successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = "your_webhook_secret"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        if event["type"] == "invoice.payment_succeeded":
            # Handle successful payment
            pass

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)