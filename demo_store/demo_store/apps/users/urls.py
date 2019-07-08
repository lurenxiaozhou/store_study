from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns=[
    url(r'^users/$',views.UserView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token),  # 登录认证
    url(r'^user/$',views.UserDetailView.as_view()), # 个人中心基本信息
    url(r'^email/$',views.EmailView.as_view()),
    url(r'^emails/verification/$',views.VerifyEmailView.as_view())

]