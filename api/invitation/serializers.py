from ..models import Invitation
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Invitation
from django.shortcuts import get_object_or_404

class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Invitation.
    
    Xử lý chuyển đổi giữa các thể hiện Invitation và biểu diễn JSON,
    bao gồm xử lý trường username tùy chỉnh và logic chấp nhận lời mời.
    """
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'title', 'content', 'status', 'duration','project', 'username']
    
    def create(self, validated_data):
        """
        Tạo một thể hiện lời mời mới.
        
        Xử lý trường username để tìm người dùng nhận trước khi tạo lời mời.
        
        Args:
            validated_data: Dictionary chứa dữ liệu đã được xác thực để tạo lời mời
            
        Returns:
            Thể hiện Invitation đã được tạo
        """
        username = validated_data.pop('username')
        receiver = validated_data.get('receiver') or get_object_or_404(
            User.objects.only('id').filter(username=username),
            username=username
        )
        validated_data['receiver'] = receiver
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Cập nhật thể hiện lời mời.
        
        Xử lý trường hợp chấp nhận lời mời bằng cách thêm người nhận
        vào danh sách quản lý dự án khi status được đặt thành True.
        """
        status = validated_data.get('status')
        if status is True:
            instance.project.managers.add(instance.receiver)
        return super().update(instance, validated_data)


