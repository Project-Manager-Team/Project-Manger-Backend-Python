from ..models import Invitation
from .serializers import InvitationSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsReceiver


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.select_related('receiver', 'sender', 'project').all()
    serializer_class = InvitationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user, status=None)
    
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




