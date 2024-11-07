from ..models import Invitation
from .serializers import InvitationSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsReceiver
from ..permissions.models import Permissions


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.select_related('receiver', 'sender', 'project').all()
    serializer_class = InvitationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        user = self.request.user
        
        # Kiểm tra xem người dùng có quyền tạo lời mời không
        if not (project.owner == user or 
                Permissions.objects.filter(
                    project=project, 
                    user=user,
                    canAddMember=True  # Sử dụng canAddMember thay vì canInvite
                ).exists()):
            raise PermissionDenied("You don't have permission to create invitations for this project.")
        
        return serializer.save(sender=user, status=None)
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('status') == True:
            invitation = serializer.instance
            invitation.project.managers.add(invitation.receiver)
            invitation.project.save()
        return serializer.save(sender=self.request.user)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsReceiver()]
        return [IsAuthenticated()]




