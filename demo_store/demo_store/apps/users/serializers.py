from django_redis import get_redis_connection
from rest_framework import serializers
import re

from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_active_email
from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户的序列化器"""
    password2 =serializers.CharField(label='确认密码',write_only=True)
    sms_code =serializers.CharField(label='短信验证码',write_only=True)
    allow =serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='JWT token',read_only=True)

    class Meta:
        model = User
        fields = ('id','username','password','password2','sms_code','mobile','allow','token')
        extra_kwargs={
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'只允许5-20个字符的用户名',
                    'max_length':'只允许5-20个字符的用户名'
                }
            },
            'password': {
                'write_only':True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '只允许8-20个字符的密码',
                    'max_length': '只允许8-20个字符的密码'
                }
            }
        }
    def validate_mobile(self,value):
        """验证手机"""
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError("手机号格式错误")
        return value

    def validate_allow(self,value):
        # 检测用户是否同意协议
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self,data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一样')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get("sms_%s" % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        # 重写保存方法，增加密码加密

        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # user = User.objects.create(**validated_data)
        user= super().create(validated_data)

        user.set_password(validated_data['password'])
        user.save()

        # 签发ｊｗｔ　token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""
    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')

    def update(self, instance, validated_data):
        """

        :param instance: 视图传过来的user对象
        :param validated_data:
        :return:
        """

        email = validated_data['email']

        instance.email = email

        instance.save()

        # 生成激活链接
        url = instance.generate_verify_email_url()

        # 发送邮件
        send_active_email.delay(email,url)

        return instance