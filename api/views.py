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





