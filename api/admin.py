from django.contrib import admin
from .models import UserProfile, Project, Invitation, Permissions

# Đăng ký các models vào trang admin của Django
admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Invitation)
admin.site.register(Permissions)
