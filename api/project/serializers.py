from rest_framework import serializers
from ..models import Project


class ProjectSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'time_start',
                  'time_end', 'type', 'manager', 'parent_id']
