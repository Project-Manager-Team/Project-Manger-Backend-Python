from django.contrib.auth.models import User
from .models import *
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate


# Quá trình chạy của LoginSerializer
# 1. Khi chúng ta gửi một request lên server, request này sẽ được xử lý bởi một view
# 2. View sẽ gọi hàm is_valid() của serializer
# 3. Hàm is_valid() sẽ gọi hàm validate() của serializer
# 4. Hàm validate() sẽ kiểm tra xem request có hợp lệ không
# 5. Nếu request không hợp lệ, hàm validate() sẽ raise một exception
# 6. Exception này sẽ được xử lý bởi hàm handle_exception() của view
# 7. Nếu request hợp lệ, hàm validate() sẽ trả về một dictionary chứa dữ liệu đã được xử lý
# 8. Dictionary này sẽ được truyền vào hàm create() của view
# 9. Hàm create() sẽ tạo một object mới và lưu vào database
# 10. Hàm create() sẽ trả về một response chứa object vừa tạo
# 11. Response này sẽ được trả về cho client

# Tại sao validate() cần 2 tham số là self và attrs?
# - self là một instance của LoginSerializer
# - attrs là một dictionary chứa dữ liệu của request


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                'username or password is incorrect')

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')

        if User.objects.filter(username=username):
            raise ValidationError("username is exists")

        user = {
            "username": username,
            "password": password,
            "email": email
        }
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

# serializers là một module của rest_framework, nó giúp chúng ta chuyển đổi dữ liệu từ model sang dạng json và ngược lại
# 1 serializer sẽ tương ứng với một model
# 1 serializer sẽ tạo ra một api endpoint để thao tác với model tương ứng
# 1 serializer sẽ có các phương thức để xử lý các request tương ứng với các phương thức http như GET, POST, PUT, DELETE
# fields in serializer là các trường của model mà chúng ta muốn hiển thị
# fields in serializer sẽ tạo ra các trường trong json response
# fields in serializer sẽ tạo ra các trường trong json request


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'time_start',
                  'time_end', 'type', 'owner', 'manager', 'parent']


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['title', 'context', 'status',
                  'receiver', 'sendersender', 'project']
