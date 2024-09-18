from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)    
    password = serializers.CharField(max_length=100, write_only=True)


class LoginReturnSerializer(serializers.Serializer):

    pass



