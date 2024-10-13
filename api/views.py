from rest_framework import status
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Project
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
# cách hoạt động của UserTaskViewSet
# 1. Khi chúng ta gửi một request lên server, request này sẽ được xử lý bởi một view
# 2. View sẽ gọi hàm list() của UserTaskViewSet
# 3. Hàm list() sẽ gọi hàm get_queryset() của UserTaskViewSet
# 4. Hàm get_queryset() sẽ trả về một queryset chứa các object mà chúng ta muốn lấy
# 5. Hàm list() sẽ lấy danh sách các object từ queryset
# 6. Hàm list() sẽ gọi hàm to_representation() của serializer
# 7. Hàm to_representation() sẽ chuyển đổi danh sách các object thành dạng json
# 8. Dạng json này sẽ được trả về cho client
# 9. authentication_classes và permission_classes sẽ kiểm tra xem request có hợp lệ không
# 10. Nếu request không hợp lệ, hàm handle_exception() của view sẽ xử lý exception
# 11. Nếu request hợp lệ, hàm list() sẽ trả về danh sách các object
# 12. Danh sách các object này sẽ được trả về cho client
# 13. Client sẽ nhận được danh sách các object và hiển thị lên trang web

# ModelViewSet Có nhận post không?


# class UserTaskProjectViewSet(viewsets.ModelViewSet):
#     queryset = Project.objects.filter()
#     serializer_class = PersonalTaskProjectSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         print(user)
#         return self.queryset.filter(owner=user)
#     # khi viết perform create thì nó mới nhận post đúng không?
#     # - perform_create() sẽ được gọi khi chúng ta gửi một request POST lên server
#     # - perform_create() sẽ tạo một object mới và lưu vào database
#     # - perform_create() sẽ trả về object vừa tạo
#     # - object vừa tạo sẽ được trả về cho client
#     # - client sẽ nhận được object vừa tạo và hiển thị lên trang web
#     def perform_create(self, serializer):
#         return serializer.save(owner=self.request.user)
#     # Hàm perform_create() nhận một tham số là serializer
#     # - serializer là một instance của PersonalTaskProjectSerializer
#     # - serializer chứa dữ liệu của request
#     # - serializer cũng chứa các hàm validate() và create()
#     # - hàm validate() sẽ kiểm tra xem request có hợp lệ không
#     # - hàm create() sẽ tạo một object mới và lưu vào database
#     # - hàm perform_create() sẽ gọi hàm save() của serializer
#     # - hàm save() của serializer sẽ gọi hàm create() của serializer
#     # - hàm create() của serializer sẽ tạo một object mới và lưu vào database
#     # - hàm create() của serializer sẽ trả về object vừa tạo
#     # - object vừa tạo sẽ được trả về cho hàm perform_create()
#     # - hàm perform_create() sẽ trả về object vừa tạo
#     # - object vừa tạo sẽ được trả về cho client


# Cách hoạt động của LoginView
# 1. Khi chúng ta gửi một request lên server, request này sẽ được xử lý bởi một view
# 2. View sẽ gọi hàm post() của LoginView
# 3. Hàm post() sẽ gọi hàm is_valid() của serializer
# 4. Hàm is_valid() sẽ kiểm tra xem request có hợp lệ không
# 5. Nếu request không hợp lệ, hàm is_valid() sẽ raise một exception
# 6. Exception này sẽ được xử lý bởi hàm handle_exception() của view
# 7. Nếu request hợp lệ, hàm is_valid() sẽ trả về một dictionary chứa dữ liệu đã được xử lý


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# front end xử lý refresh token như thế nào?
# - front end sẽ lưu trữ refresh token vào local storage
# - front end sẽ gửi refresh token lên server để lấy access token
# - front end sẽ gửi access token lên server để xác thực user
# - front end sẽ gửi access token lên server để lấy dữ liệu từ server

# Tôi muốn khi tạo ra 1 user
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        Project.objects.create(
            title=f"{user.username.title()} Project",  # Tiêu đề project
            description="This is a personal project root.",  # Mô tả project
            time_start=None,  # Có thể để None hoặc đặt giá trị mặc định khác
            time_end=None,    # Có thể để None hoặc đặt giá trị mặc định khác
            # Hoặc sử dụng Project.ProjectType.PERSONAL nếu bạn có loại này
            type="personal",
            owner=user,  # Người sở hữu là user vừa đăng ký
            parent=None  # Đây là root project nên parent là None
        )

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


# class InvitationViewSet(viewsets.ModelViewSet):
#     queryset = Invitation.objects.all()
#     serializer_class = InvitationSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(owner=user)

#     def perform_create(self, serializer):
#         return serializer.save(owner=self.request.user)


class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Tất cả các child và user
        parent = self.request.query_params.get("parent")
        root = self.queryset.get(type="personal", owner=user)
        manage_project = self.queryset.filter(manager=user)

        if parent is not None:
            all_child_project = root.get_descendants()
            for project in manage_project:
                all_child_project |= project.get_descendants(include_self=True)
            return all_child_project.filter(parent=parent)
        return root.get_children() | manage_project

    def perform_create(self, serializer):
        user = self.request.user
        # Tất cả các child và user
        parent = self.request.data.get("parent")
        root = self.queryset.get(type="personal", owner=user)
        descendants = root.get_descendants()
        if parent is not None:
            if descendants.filter(id=parent).exists():
                return serializer.save(owner=user, parent=descendants.get(id=parent))
            raise serializers.ValidationError("parent is not exists")
        raise serializers.ValidationError('parent: This field is required.')


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(receiver=user)

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user)
