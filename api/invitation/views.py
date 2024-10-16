from ..models import Invitation
from .serializers import InvitationSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user, status=False)
    
            
    
