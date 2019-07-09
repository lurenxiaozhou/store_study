import re

from rest_framework import serializers

from .models import Area
from users.models import Address


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id','name']


class SubAreaSerializer(serializers.ModelSerializer):
    subs = AreaSerializer(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ['id','name','subs']


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID',required=True)
    city_id = serializers.IntegerField(label='市ID',required=True)
    district_id = serializers.IntegerField(label='区ID',required=True)

    class Meta:
        model = Address
        exclude = ['user','is_deleted','create_time','update_time']


    def validate_mobile(self,value):
        # 验证手机号
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def create(self, validated_data):
        # 保存
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ['title']


