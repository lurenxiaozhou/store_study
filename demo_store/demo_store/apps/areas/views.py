from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import serializers

from .models import Area
# Create your views here.



class AreasViewSet(ReadOnlyModelViewSet):

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