from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from . import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView

# Create your views here.
from .serializers import CreateUserSerializer


class UserView(CreateAPIView):

    serializer_class = CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    """用户基本信息"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]  # 指明必须登录认真后才能访问

    def get_object(self):
        # 返回当前请求的用户
        #　在类视图对象中，可以通过类视图对象的属性获取ｒｅｑｕｅｓｔ
        # 在django的请求request中，user属性表明当前请求的用户
        return self.request.user


class EmailView(UpdateAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]  # 指明必须登录认真后才能访问

    def get_object(self):
        return self.request.user



# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})



class AddPassWordView(CreateAPIView):
    serializer_class=serializers.AddPWSerializer








