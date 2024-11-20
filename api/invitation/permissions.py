from rest_framework.permissions import BasePermission

class IsReceiver(BasePermission):
    """
    Lớp quyền để xác minh nếu người dùng yêu cầu là người nhận lời mời.
    
    Quyền này được sử dụng để đảm bảo rằng chỉ người nhận lời mời
    mới có thể thực hiện các hành động nhất định (như chấp nhận/từ chối lời mời).
    """
    def has_object_permission(self, request, view, obj):
        return obj.receiver == request.user
