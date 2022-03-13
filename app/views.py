import json

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, HttpResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenViewBase

from app import models
from app.serializers import MyTokenObtainPairSerializer, MyTokenVerifySerializer
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
            serializer_valid.is_valid(raise_exception=True)
            serializer_valid.validated_data['username'] = user_info['username']
            obj = models.User.objects.filter(username=username).first()
            psd = check_password(psd, obj.password)
            if not obj:
                response = self.wrap_json_response(code=ReturnCode.FAILED, message='用户名不存在!')
            else:
                if psd:
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


def verify_info(request, *args, **kwargs):
    """身份验证视图"""
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        try:
            username = models.User.objects.filter(username=data['username'])
            if not username.filter(real_name=data['realName']).exists():
                res = {'code': ReturnCode.FAILED, 'message': '真实姓名错误'}
            elif not username.filter(phone=data['phoneNumber']).exists():
                res = {'code': ReturnCode.FAILED, 'message': '手机号码错误'}
            elif not username.filter(email=data['email']).exists():
                res = {'code': ReturnCode.FAILED, 'message': '电子邮箱错误'}
            elif username.filter(real_name=data['realName'], phone=data['phoneNumber'], email=data['email']).exists():
                res = {'code': ReturnCode.SUCCESS, 'message': '身份验证成功'}
            else:
                res = {'code': ReturnCode.FAILED, 'message': '身份验证失败'}
        except Exception as e:
            print(e)
            res = {'code': ReturnCode.FAILED, 'message': '账号不存在'}
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