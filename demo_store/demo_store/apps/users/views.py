from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from goods.serializers import SKUSerializer
from .models import User
from . import serializers,constants
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView

# Create your views here.
from .serializers import CreateUserSerializer, AddUserBrowsingHistorySerializer


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


class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        保存
        """
        return self.create(request)

    def get(self,request):
        # 获取
        user_id = request.user.id

        redis_conn = get_redis_connection('history')
        history =redis_conn.lrange('history_%s'%user_id,0,constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)
        skus=[]
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        s = SKUSerializer(skus,many=True)

        return Response(s.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """ 用户登录认证视图"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 如果用户成功登录合并购物车
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)
        return response














