from rest_framework import serializers
from .models import MonAn, NguyenLieu
from django.contrib.auth.models import User

class MonAnSerializer(serializers.ModelSerializer):
    nguyen_lieu = serializers.StringRelatedField(many=True)

    class Meta:
        model = MonAn
        fields = ['maMonAn', 'tenMonAn', 'moTa', 'chiTiet', 'thoiGian', 'calo', 'hinhAnh', 'loai', 'nguyen_lieu']

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True} # Chỉ cho phép ghi, không trả mật khẩu về khi xem info
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']