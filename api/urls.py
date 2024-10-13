
from django.urls import path, include
from rest_framework import routers
from . import views
router = routers.DefaultRouter()
# router.register(r'info', views.UserTaskProjectViewSet)
router.register(r'invitation', views.InvitationViewSet)
router.register(r'project', views.PersonalProjectViewSet,
                basename='personal-project')


""" 
hàm router.register() nhận vào 2 tham số:
- tham số thứ nhất là tên của url pattern, nó sẽ được thêm vào url pattern của router   
- tham số thứ hai là viewset, viewset này sẽ xử lý các request tương ứng với url pattern trên
- router.register() sẽ tạo ra 2 url pattern:
    + một url pattern GET để lấy danh sách các object
    + một url pattern POST để tạo một object mới
- url pattern GET sẽ có dạng /<tên_url_pattern>/
- url pattern POST sẽ có dạng /<tên_url_pattern>/
- url pattern GET sẽ lấy danh sách các object
- url pattern POST sẽ tạo một object mới
- url pattern GET sẽ gọi hàm list() của viewset
- url pattern POST sẽ gọi hàm create() của viewset
- viewset phải kế thừa từ viewset.ModelViewSet
- viewset.ModelViewSet đã cung cấp sẵn các hàm xử lý cho các request
"""

urlpatterns = [
    path('', include(router.urls)),
    path("login/", views.LoginView.as_view()),
    path("register/", views.RegisterView.as_view())

]
""" 
    path("users/", include("api.users.urls")), có cần tham số thứ nhất là users không?
    - tham số thứ nhất của hàm include() là url pattern của app users
    - url pattern của app users sẽ được thêm vào url pattern của app api
    - url pattern của app users sẽ có dạng /users/
    - url pattern của app users sẽ bắt đầu từ /users/
 """
