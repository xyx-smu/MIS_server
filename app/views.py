import json

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
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
