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


def build_tree(root):
    tree_dict = model_to_dict(root)
    tree_dict['children'] = [build_tree(child) for child in  root.get_children()] 
    return tree_dict
class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwnerOrIsManger(), IsNotPersonalProject()]
        if self.action == 'create':
            return [IsAuthenticated(), IsOwnerOrIsManger(), IsNotTypePersonal()]
        if self.action == 'update':
            return [IsAuthenticated(), IsOwnerOrIsManger(), IsNotPersonalProject()]
        return [IsAuthenticated()]

    
    def get_queryset(self):
        user = self.request.user
        root = get_object_or_404(self.queryset, owner=user, type="personal")
        all_descendants = root.get_descendants(include_self=True)
        for project in self.queryset.filter(manager=user):
            all_descendants |= project.get_descendants(
                include_self=True)
        return all_descendants

    def perform_create(self, serializer):
        response = serializer.save(owner=self.request.user, manager=None, progress=0)
        update_parent_progress.delay(serializer.validated_data.get('parent_id'))
        return response
    
    def perform_update(self, serializer):
        progress = serializer.validated_data.get('progress')
        if progress is not None:
            update_parent_progress.delay(self.get_object().parent.id)
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        parent_id = instance.parent.id
        if instance.owner == self.request.user:            
            super().perform_destroy(instance)
            update_parent_progress.delay(parent_id)
        else:
            instance.manager = None
            instance.save()
        return None

    @action(detail=False, methods=['GET'])
    def personal(self, request):
        query_set = self.get_queryset()
        root = get_object_or_404(query_set, owner=request.user, type="personal")
        children_and_managed = query_set.filter(Q(parent=root) | Q(manager=request.user) | Q(type="personal"))
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
        print(tree)
        return Response(tree, status=status.HTTP_200_OK)
        
    
    
  