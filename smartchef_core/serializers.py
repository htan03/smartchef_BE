from rest_framework import serializers
from .models import MonAn

class MonAnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonAn
        fields = '__all__' # Lấy tất cả thông tin (Tên, ảnh, giá...) trả về JSON