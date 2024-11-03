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
from rest_framework import status
from .tasks import update_parent_progress
from django.forms.models import model_to_dict
from rest_framework.exceptions import ValidationError  # Added import


def build_tree(root):
    tree_dict = model_to_dict(root)
    tree_dict['children'] = [build_tree(child) for child in  root.get_children().order_by('id')] 
    return tree_dict

class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwnerOrIsManager(), IsNotPersonalProject()]
        if self.action == 'create':
            return [IsAuthenticated(), IsOwnerOrIsManager(), IsNotTypePersonal()]
        if self.action == 'update':
            return [IsAuthenticated(), IsOwnerOrIsManager(), IsNotPersonalProject()]
        return [IsAuthenticated()]

    
    def get_queryset(self):
        user = self.request.user
        root = get_object_or_404(
            self.queryset.select_related('owner').prefetch_related('managers'),
            owner=user, type="personal"
        )
        all_descendants = root.get_descendants(include_self=True).distinct().prefetch_related('managers')
        for project in self.queryset.filter(managers=user).prefetch_related('managers'):
            all_descendants |= project.get_descendants(include_self=True).prefetch_related('managers').distinct()
        return all_descendants.order_by('id').distinct()

    def perform_create(self, serializer):
        try:
            response = serializer.save(owner=self.request.user, progress=0)
            update_parent_progress.delay(serializer.validated_data.get('parentId'))
            return response
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_update(self, serializer):
        try:
            progress = serializer.validated_data.get('progress')
            if progress is not None:
                update_parent_progress.delay(self.get_object().parent.id)
            return super().perform_update(serializer)
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_destroy(self, instance):
        parent_id = instance.parent.id
        if instance.owner == self.request.user:            
            super().perform_destroy(instance)
            update_parent_progress.delay(parent_id)
        else:
            instance.managers.remove(self.request.user)
            instance.save()
        return None

    @action(detail=False, methods=['GET'])
    def personal(self, request):
        query_set = self.get_queryset()
        root = get_object_or_404(query_set.select_related('owner'), owner=request.user, type="personal")
        children_and_managed = query_set.filter(
            Q(parent=root) | Q(managers=request.user) | Q(type="personal")
        ).distinct().prefetch_related('managers')
        serializer = self.get_serializer(children_and_managed, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
    @action(detail=True, methods=['GET'])
    def child(self, request, pk=None):
        queryset = get_object_or_404(self.get_queryset(), id=pk).get_children()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def descendants(self, request, pk=None):
        root = get_object_or_404(self.get_queryset(), id=pk)
        tree = build_tree(root)
        return Response(tree, status=status.HTTP_200_OK)



