from ..models import Invitation
from .serializers import InvitationSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user, status=None)
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('status') == True:
            invitation = serializer.instance
            invitation.project.manager = invitation.receiver
            invitation.project.save()
        return serializer.save(sender=self.request.user)
    
    
            
    
