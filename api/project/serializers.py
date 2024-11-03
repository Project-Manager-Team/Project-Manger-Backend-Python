from rest_framework import serializers
from ..models import Project
from collections import deque
from django.contrib.auth.models import User
from django.utils import timezone  # Added import

class ProjectSerializer(serializers.ModelSerializer):
    parentId = serializers.IntegerField(required=False, allow_null=True)
    managers = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'beginTime', 'completeTime',
                  'endTime', 'type', 'managers', 'owner', 'parentId', 'progress', 'diffLevel']
    
    def get_managers(self, obj):
        return [
            {
                "username": manager.username,
                "avatar": manager.userprofile.avatar.url if hasattr(manager, 'userprofile') and manager.userprofile.avatar else None
            }
            for manager in obj.managers.all()
        ]
    
    def get_owner(self, obj):
        owner = obj.owner
        return {
            "username": owner.username,
            "avatar": owner.userprofile.avatar.url if hasattr(owner, 'userprofile') and owner.userprofile.avatar else None
        } if owner else None
    
    def create(self, validated_data):
        parentId = validated_data.pop('parentId', None)
        if parentId is None:
            parent = Project.objects.get(owner=self.context['request'].user, type="personal")
            validated_data['parent_id'] = parent.id
        else:
            parent = Project.objects.get(id=parentId)
            parent.type = 'project'
            parent.save()
            
        validated_data['parent'] = parent
        
        project = super().create(validated_data)
        manager_ids = self.initial_data.get('manager_ids', [])
        project.managers.set(User.objects.filter(id__in=manager_ids))
        return project
    
    def update(self, instance, validated_data):
        manager_ids = self.initial_data.get('manager_ids')
        if manager_ids is not None:
            instance.managers.set(User.objects.filter(id__in=manager_ids))
        return super().update(instance, validated_data)

    def validate(self, data):
        request = self.context.get('request')
        if self.instance:
            if self.instance.type == 'task' and self.instance.endTime:
                current_time = timezone.now()
                new_progress = data.get('progress', self.instance.progress)
                if new_progress >= 100 and current_time > self.instance.endTime:
                    raise serializers.ValidationError("Cannot mark the task as completed after its end time.")
        return data



