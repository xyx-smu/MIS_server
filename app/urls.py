from django.conf.urls import url
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app import views
from app.views import RefreshTokenView

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view()),
    url(r'^token_refresh/$', RefreshTokenView.as_view(), name='token_refresh'),
    url(r'^register/(?P<id>\d+)?', views.RegisterView.as_view()),
    url(r'api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^check_username/$', views.check_username),
    url(r'^get_email_code/$', views.get_email_code),  # 获取邮箱验证码
    url(r'^verify_info/$', views.verify_info),
    url(r'^set_password/$', views.set_password),
]