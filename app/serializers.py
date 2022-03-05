from jwt import decode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer

from MIS_server import settings


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['username'] = self.user.username
        data['user_id'] = self.user.id

        return data


class MyTokenVerifySerializer(TokenVerifySerializer):

    def validate(self, attrs):
        """
        attrs['token']: 是请求的token
        settings.SECRET_KEY: setting.py默认的key 除非在配置文件中修改了
        algorithms: 加密的方法
        """
        decoded_data = decode(attrs['token'], settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_data
