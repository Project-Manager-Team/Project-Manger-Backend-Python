from rest_framework import viewsets
from ..models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import *
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q


class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner(), IsNotPersonalProject()]
        if self.action == 'create':
            return [IsAuthenticated(), IsOwnerOrIsManger()]
        if self.action == 'update':
            return [IsAuthenticated(), IsOwnerOrIsManger(), IsNotPersonalProject()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['GET'])
    def personal(self, request):
        queryset = self.get_queryset().filter(
            Q(owner=self.request.user) | Q(manager=self.request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def child(self, request, pk=None):
        queryset = get_object_or_404(self.get_queryset(), id=pk).get_children()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        root = get_object_or_404(self.queryset, owner=user, type="personal")
        all_descendants = root.get_descendants(include_self=True)
        for project in self.queryset.filter(manager=user):
            all_descendants |= project.get_descendants(
                include_self=True)
        return all_descendants

    def perform_create(self, serializer):
        parent_id = serializer.validated_data.get('parent_id')
        if parent_id is not None:
            parent = get_object_or_404(
                self.get_queryset(), id=parent_id, type='project')
            return serializer.save(owner=self.request.user, parent=parent, manager=None)

        parent = get_object_or_404(self.get_queryset(), type='personal')
        return serializer.save(owner=self.request.user, parent=parent, manager=None)
