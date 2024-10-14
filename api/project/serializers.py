from rest_framework import serializers
from ..models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'time_start',
                  'time_end', 'type', 'manager', 'parent_id']
