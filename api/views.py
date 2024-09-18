from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .serializers import LoginSerializer
# Create your views here.

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
