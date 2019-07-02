from django_redis import get_redis_connection
from rest_framework import serializers



class ImageCodeCheckSerializers(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4,min_length=4)

    def validate(self, attrs):
        # 获取前端传入的参数
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询真实的图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get("img_%s" %image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        # 删除redis中的图片验证码
        redis_conn.delete('img_%s'%image_code_id)

        # 比较图片验证码
        real_image_code_text = real_image_code_text.decode()
        print(real_image_code_text,text.lower())
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # 判断是否在60s内
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s"%mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')
        return attrs