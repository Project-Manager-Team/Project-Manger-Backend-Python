from rest_framework import generics
from .serializers import UserSerializer
from ..models import Project

class UserRegister(generics.CreateAPIView):
    serializer_class = UserSerializer
    # create a root project 

    def perform_create(self, serializer):
        user = serializer.save()
        Project.objects.create(owner=user, title="Root", type="personal")
        return user
    

    