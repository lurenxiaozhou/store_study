from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from django.http import HttpResponse
from demo_store.libs.captcha.captcha import captcha
from . import constants
# Create your views here.



class ImageCodeView(APIView):
    #  1生成验证码图片 2保存真实验证码到redis 3 返回响应
    def get(self,request,image_code_id):

        text,image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)

        return HttpResponse(image, content_type='image/jpg')