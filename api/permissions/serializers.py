from rest_framework import serializers
from .models import Permissions

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = ['project', 'user', 'canEdit', 'canDelete', 'canAdd', 'canFinish', 
                 'canAddMember', 'canRemoveMember']
