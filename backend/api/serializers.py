from rest_framework import serializers
from django.contrib.auth import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
        
    
    
