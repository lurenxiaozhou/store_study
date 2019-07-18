from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .serializers import OAuthQQUserSerializer
from .models import OAuthQQUser
from .exceptions import OAuthQQAPIError
from .utils import OAuthQQ
from carts.utils import merge_cart_cookie_to_redis


class QQAuthURLView(APIView):
    """获取qq登录的url"""

    def get(self,request):
        """提供用于qq登录的url"""

        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()

        return Response({"login_url":login_url})


class QQAuthUserView(CreateAPIView):
    """qq登录的用户"""
    serializer_class = OAuthQQUserSerializer

    def get(self,request):
        """1.获取coed
        2.凭借code 获取access_token
        3.凭借access_token 获取openid
        4.根据openid查询数据库OAuthQQUser 判读数据是否存在
        5.如果数据存在，表示用户已经邦定过身份，签发 jwt token
        6.如果数据不存在，处理openid并返回
        """
        # 1.获取coed
        code = request.query_params.get('code')

        if not code:
            return Response({"message":'缺少code'},status=status.HTTP_400_BAD_REQUEST)

        # 2.凭借code 获取access_token
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            # 3.凭借access_token 获取openid
            openid = oauth_qq.get_openid(access_token)
        except OAuthQQAPIError:
            return Response({"message":"访问qq接口异常"},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4根据openid查询数据库OAuthQQUser 判读数据是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在了，处理openid并返回
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({'access_token':access_token})
        else:
            # 5.如果数据存在，表示用户已经邦定过身份，签发 jwt token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_payload = api_settings.JWT_ENCODE_PAYLOAD

            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_payload(payload)

            # return Response({
            #     "username":user.username,
            #     "user_id":user.id,
            #     "token":token
            # })
            response = Response({
                "username":user.username,
                "user_id":user.id,
                "token":token
            })

            # 合并购物车
            response = merge_cart_cookie_to_redis(request,user,response)

            return response
    # def post(self,requset):
    #     """
    #     1.获取数据
    #     2.效验参数
    #     3.判断用户是否存在
    #     4.如果存在，绑定， 创建QQAuthUser数据
    #     5.如果不存在，先创建User ，创建QQAuthUser数据
    #     6.签发JWT token
    #     :param requset:
    #     :return:
    #     """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # 合并购物车
        user = self.user
        response = merge_cart_cookie_to_redis(request,user,response)

        return response


