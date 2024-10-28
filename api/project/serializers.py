from rest_framework import serializers
from ..models import Project
from collections import deque

class ProjectSerializer(serializers.ModelSerializer):
    # add null = True to the fields that are not required
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'time_start', 'time_completed',
                  'time_end', 'type', 'manager_name', 'parent_id', 'progress', 'difficulty_level']
        
    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id is None:
            parent = Project.objects.get(owner=self.context['request'].user, type="personal")
            validated_data['parent_id'] = parent.id
        else:
            parent = Project.objects.get(id=parent_id)
            parent.type = 'project'
            parent.save()
            
        validated_data['parent'] = parent
        
        return super().create(validated_data)



