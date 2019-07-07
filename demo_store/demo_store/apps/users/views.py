from django.shortcuts import render
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













