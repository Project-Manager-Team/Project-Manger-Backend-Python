from ..models import Invitation
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Invitation
from rest_framework import serializers
from django.shortcuts import get_object_or_404
class InvitationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    class Meta:
        model = Invitation
        fields = ['id', 'title', 'context', 'status', 'duration','project', 'username']
    def create(self, validated_data):
        username = validated_data.pop('username')
        receiver = get_object_or_404(User.objects.all(), username=username)
        validated_data['receiver'] = receiver
        return super().create(validated_data)


        