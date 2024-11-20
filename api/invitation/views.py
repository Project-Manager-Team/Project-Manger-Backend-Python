from ..models import Invitation
from .serializers import InvitationSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsReceiver
from ..permissions.models import Permissions


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet để quản lý các lời mời dự án.
    
    Cung cấp các thao tác CRUD cho model Invitation với 
    kiểm tra quyền và xác thực phù hợp.
    """
    queryset = Invitation.objects.select_related('receiver', 'sender', 'project').all()
    serializer_class = InvitationSerializer
    
    def get_queryset(self):
        """
        Trả về danh sách lời mời được lọc cho người dùng yêu cầu.
        
        Chỉ trả về các lời mời mà người dùng yêu cầu là người nhận.
        """
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        """
        Tạo lời mời mới sau khi kiểm tra quyền.
        
        Xác minh rằng người dùng có quyền tạo lời mời cho dự án
        (là chủ sở hữu hoặc có quyền canAddMember).
        
        Raises:
            PermissionDenied: Nếu người dùng không có quyền cần thiết
        """
        project = serializer.validated_data.get('project')
        user = self.request.user
        
        if not (project.owner == user or 
                Permissions.objects.filter(
                    project=project, 
                    user=user,
                    canAddMember=True 
                ).exists()):
            raise PermissionDenied("You don't have permission to create invitations for this project.")
        
        return serializer.save(sender=user, status=None)
    
    def perform_update(self, serializer):
        """
        Cập nhật lời mời và xử lý việc chấp nhận.
        
        Nếu lời mời được chấp nhận (status=True), thêm người nhận
        vào danh sách quản lý dự án.
        """
        if serializer.validated_data.get('status') == True:
            invitation = serializer.instance
            invitation.project.managers.add(invitation.receiver)
            invitation.project.save()
        return serializer.save(sender=self.request.user)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsReceiver()]
        return [IsAuthenticated()]




