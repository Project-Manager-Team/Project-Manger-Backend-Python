from rest_framework import serializers
from ..models import Project


class ProjectSerializer(serializers.ModelSerializer):
    # add null = True to the fields that are not required
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'time_start',
                  'time_end', 'type', 'manager', 'parent_id']
        
    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id is None:
            parent = Project.objects.get(owner=self.context['request'].user, type="personal")
        else:
            parent = Project.objects.get(id=parent_id)
        validated_data['parent'] = parent
        return super().create(validated_data)
