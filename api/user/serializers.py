from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate_password(self, password: str):
        try:
            validate_password(password)
            return password

        except exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages)

    def create(self, validated_data: dict):
        return User.objects.create_user(**validated_data)
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    
    
