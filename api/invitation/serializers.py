from ..models import Invitation
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Invitation
from django.shortcuts import get_object_or_404

class InvitationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'title', 'content', 'status', 'duration','project', 'username']
    
    def create(self, validated_data):
        username = validated_data.pop('username')
        receiver = validated_data.get('receiver') or get_object_or_404(
            User.objects.only('id').filter(username=username),
            username=username
        )
        validated_data['receiver'] = receiver
        return super().create(validated_data)

    def update(self, instance, validated_data):
        status = validated_data.get('status')
        if status is True:
            instance.project.managers.add(instance.receiver)
        return super().update(instance, validated_data)


