from django.conf.urls import url
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app import views
from app.views import RefreshTokenView

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view()),
    url(r'^token_refresh/$', RefreshTokenView.as_view(), name='token_refresh'),
    url(r'^register/(?P<id>\d+)?', views.RegisterView.as_view()),
    url(r'api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]