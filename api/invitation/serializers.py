from ..models import Invitation
from rest_framework import serializers


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['title', 'context', 'receiver', 'project']
        