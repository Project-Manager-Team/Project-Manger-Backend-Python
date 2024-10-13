from rest_framework import viewsets
from ..models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import serializers


class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Tất cả các child và user
        parent = self.request.query_params.get("parent")
        root = self.queryset.get(type="personal", owner=user)
        manage_project = self.queryset.filter(manager=user)

        if parent is not None:
            all_child_project = root.get_descendants()
            for project in manage_project:
                all_child_project |= project.get_descendants(include_self=True)
            return all_child_project.filter(parent=parent)
        return root.get_children() | manage_project

    def perform_create(self, serializer):
        user = self.request.user
        parent = self.request.data.get("parent")
        root = self.queryset.get(type="personal", owner=user)
        descendants = root.get_descendants()
        if parent is not None:
            if descendants.filter(id=parent).exists():
                return serializer.save(owner=user, parent=descendants.get(id=parent))
            raise serializers.ValidationError("parent is not exists")
        raise serializers.ValidationError('parent: This field is required.')
