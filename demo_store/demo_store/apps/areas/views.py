from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet,GenericViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework import mixins, status

from . import serializers,constants

from .models import Area
# Create your views here.



class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer


class AddressViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    """
    用户地址新增与删除
    """

    serializer_class = serializers.UserAddressSerializer

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 检查用户地址数据数量不能超过20上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message':'保存地址数据已达上限'},status=status.HTTP_400_BAD_REQUEST)
        return super().create(request,*args,**kwargs)

    def get_queryset(self):

        return self.request.user.addresses.filter(is_deleted=False)

    def list(self,request,*args,**kwargs):
        # 用户地址列表数据
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        user = self.request.user
        return Response({
            'user_id':user.id,
            'default_address_id':user.default_address_id,
            'limit':constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses':serializer.data
        })

    def destroy(self,request,*args,**kwargs):
        # 逻辑删除
        address = self.get_object()

        address.is_deleted=True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'],detail=True)
    def status(self,request,pk=None):
        # 设置默认地址

        address = self.get_object()
        request.user.default_address = address
        request.user.save()

        return Response({'message':'OK'},status=status.HTTP_200_OK)

    @action(methods=['put'],detail=True)
    def title(self,request,pk=None,address_id=None):
        # 修改标题
        address = self.get_object()
        serializer = self.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)






