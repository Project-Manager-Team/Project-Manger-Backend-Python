from rest_framework import generics, viewsets
from .serializers import UserSerializer, ChangePasswordSerializer, UserProfileSerializer
from ..models import Project
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

class UserRegister(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []

    def perform_create(self, serializer):
        user = serializer.save()
        Project.objects.create(owner=user, title="Root", type="personal")
        UserProfile.objects.create(user=user)
        return user

class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='detail')
    def get_user_detail(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='avatar')
    def avatar(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='update-avatar')
    def update_avatar(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
