import logging
import random

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework import status
from celery_tasks.sms.tasks import send_sms_code

from demo_store.libs.captcha.captcha import captcha
from users.models import User
from .serializers import ImageCodeCheckSerializers
from . import constants,serializers
from demo_store.utils.yuntongxun.sms import CCP
# Create your views here.


logger = logging.getLogger('django')


class MobileCountView(APIView):
    # 获取指定手机号数量
    def get(self,request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        data={
            'mobile':mobile,
            'count':count
        }

        return Response(data)


class UsernameCountView(APIView):
    # 获取指定用户
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data={
            'username':username,
            'count':count
        }

        return Response(data)


class SMSCodeView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializers
    # 1.校验参数 2.生成短信验证码 3.保存验证码 保存发送记录 4.发送短信 5.返回
    def get(self,request,mobile):
        # 校验参数 由序列化器完成
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0,999999)

        # 保存验证码 保存发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex("sms_%s"%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        # redis_conn.setex("send_flag_%s"%mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        # redis 管道
        pl = redis_conn.pipeline()
        pl.setex("sms_%s"%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        print(sms_code)
        pl.setex("send_flag_%s"%mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        # 管道执行
        pl.execute()

        # # 发送短信

        # try:
        #     ccp=CCP()
        #     expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        #     result=ccp.send_template_sms(mobile,[sms_code,expires],constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error("发送短信验证码短信[异常][mobile:%s,message:%s]"%(mobile,e))
        #     return Response({"message":"failed"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     if result == 0:
        #         logger.info("发送短信验证码短信[正常][mobile:%s]"%mobile)
        #         return Response({"message":"OK"})
        #     else:
        #         logger.info("发送短信验证码短信[失败][mobile:%s]" % mobile)
        #         return Response({"message":"failed"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 使用celery发送短信
        # expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        # send_sms_code.delay(mobile,sms_code,expires,constants.SMS_CODE_TEMP_ID)

        return Response({'message':'OK'})


class ImageCodeView(APIView):
    #  1生成验证码图片 2保存真实验证码到redis 3 返回响应
    def get(self,request,image_code_id):

        text,image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        print(text)
        return HttpResponse(image, content_type='image/jpg')