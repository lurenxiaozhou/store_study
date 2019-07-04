from django.shortcuts import render

from rest_framework.generics import CreateAPIView

# Create your views here.
from .serializers import CreateUserSerializer


class UserView(CreateAPIView):

    serializer_class = CreateUserSerializer