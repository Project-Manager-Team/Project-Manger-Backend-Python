from rest_framework import generics

from .serializers import UserSerializer


class UserRegister(generics.CreateAPIView):
    serializer_class = UserSerializer
