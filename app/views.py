import json
import time
from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, HttpResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenViewBase

from app import models
from app.serializers import MyTokenObtainPairSerializer, MyTokenVerifySerializer
from utils.email_send import send_email
from utils.response import CommonResponseMixin, ReturnCode


class MyObtainTokenPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LoginView(MyObtainTokenPairView, CommonResponseMixin):
    """登录视图"""

    def post(self, request, *args, **kwargs):
        user_info = request.data
        serializer_valid = self.get_serializer(data=user_info)
        username = user_info['username']
        psd = user_info['password']
        try:
            obj = models.User.objects.filter(username=username).first()
            if not obj:
                response = self.wrap_json_response(code=ReturnCode.FAILED, message='用户名不存在!')
            else:
                psd = check_password(psd, obj.password)
                if psd:
                    serializer_valid.is_valid(raise_exception=True)
                    response = self.wrap_json_response(code=ReturnCode.SUCCESS,
                                                       data=serializer_valid.validated_data)
                else:
                    response = self.wrap_json_response(code=ReturnCode.FAILED, message='用户名或密码错误，请重新输入!')
        except Exception as e:
            print(e)
            response = self.wrap_json_response(code=ReturnCode.FAILED, message='登录失败,原因为' + str(e))
        return Response(response)


class RefreshTokenView(TokenRefreshView, CommonResponseMixin):

    def post(self, request, *args, **kwargs):
        serializer_valid = self.get_serializer(data=request.data)
        try:
            serializer_valid.is_valid(raise_exception=True)
            response = self.wrap_json_response(data=serializer_valid.validated_data)
            print(response)
        except Exception as e:
            print(e)
            response = self.wrap_json_response(code=ReturnCode.UNAUTHORIZED, message="您提供的refresh-token已经失效")
        return Response(response)


class MyTokenVerifyView(TokenViewBase):
    serializer_class = MyTokenVerifySerializer


class RegisterView(View, CommonResponseMixin):
    """注册视图"""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode())
            username = data['username']
            if_exist_nick = models.User.objects.filter(username=username).exists()
            if if_exist_nick:
                response = self.wrap_json_response(code=ReturnCode.FAILED, message="用户名'" + username + "'已存在")
            else:
                data = {'username': username, 'real_name': data['realName'], 'password': data['password'],
                        'phone': data['phoneNumber'], 'email': data['email']}
                models.User.objects.create(**data)
                response = self.wrap_json_response(code=ReturnCode.SUCCESS, message="注册成功")
        except Exception as e:
            print(e)
            response = self.wrap_json_response(code=ReturnCode.FAILED, message=e)
        return JsonResponse(response)


def check_username(request, *args, **kwargs):
    """选择账号视图"""
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        try:
            isexist = models.User.objects.filter(username=data['username']).exists()
            if isexist:
                res = {'code': ReturnCode.SUCCESS, 'message': '账号存在'}
            else:
                res = {'code': ReturnCode.FAILED, 'message': '账号不存在'}
        except Exception as e:
            print(e)
            res = {'code': ReturnCode.FAILED, 'message': '用户不存在'}
        return HttpResponse(json.dumps(res), content_type="application/json")


def get_email_code(request, *args, **kwargs):
    """获取邮箱验证码视图"""
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        try:
            user = models.User.objects.filter(username=data['username'])
            if user.filter(email=data['email']).exists():
                send_email(data['email'])
                res = {'code': ReturnCode.SUCCESS, 'message': '验证码已发送，请查收邮件！'}
            else:
                res = {'code': ReturnCode.FAILED, 'message': '邮箱与用户绑定邮箱不一致！'}
        except Exception as e:
            print(e)
            res = {'code': ReturnCode.FAILED, 'message': '账号不存在'}
        return HttpResponse(json.dumps(res), content_type="application/json")


def verify_info(request, *args, **kwargs):
    """身份验证视图"""
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        try:
            curr_email = models.EmailVerifyRecord.objects.filter(email=data['email']).first()
            print(curr_email)
            curr_code = curr_email.code
            code_time = curr_email.send_time.astimezone().timestamp()
            now_time = datetime.now().timestamp()
            diff = round((now_time - code_time))
            if curr_code == data['emailCode']:
                if diff < 5*60:
                    res = {'code': ReturnCode.SUCCESS, 'message': '身份验证成功'}
                else:
                    res = {'code': ReturnCode.FAILED, 'message': '该验证码已过期，请重新获取！'}
            else:
                res = {'code': ReturnCode.FAILED, 'message': '验证码错误！'}
        except Exception as e:
            print(e)
            res = {'code': ReturnCode.FAILED, 'message': e}
        return HttpResponse(json.dumps(res), content_type="application/json")


def set_password(request, *args, **kwargs):
    """设置新密码视图"""
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        password = data['password']
        psw = make_password(password, None, 'pbkdf2_sha256')
        try:
            models.User.objects.filter(username=data['username']).update(password=psw)
            res = {'code': ReturnCode.SUCCESS, 'message': '密码修改成功'}
        except Exception as e:
            print(e)
            res = {'code': ReturnCode.FAILED, 'message': '账户不存在'}
        return HttpResponse(json.dumps(res), content_type="application/json")
