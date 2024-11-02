from rest_framework import serializers
from ..models import Project
from collections import deque
from django.contrib.auth.models import User
from django.utils import timezone  # Added import

class ProjectSerializer(serializers.ModelSerializer):
    parentId = serializers.IntegerField(required=False, allow_null=True)
    managerNames = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'beginTime', 'completeTime',
                  'endTime', 'type', 'managerNames', 'parentId', 'progress', 'diffLevel']
    
    def get_managerNames(self, obj):
        return list(obj.managers.values_list('username', flat=True))
    
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
        """
        Ensure that a task cannot be marked as completed after its end time.
        """
        request = self.context.get('request')
        if self.instance:
            if self.instance.type == 'task' and self.instance.endTime:
                current_time = timezone.now()
                new_progress = data.get('progress', self.instance.progress)
                if new_progress >= 100 and current_time > self.instance.endTime:
                    raise serializers.ValidationError("Cannot mark the task as completed after its end time.")
        return data



