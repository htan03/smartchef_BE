from rest_framework import serializers
from .models import MonAn, NguyenLieu

class MonAnSerializer(serializers.ModelSerializer):
    nguyen_lieu = serializers.StringRelatedField(many=True)

    class Meta:
        model = MonAn
        fields = ['maMonAn', 'tenMonAn', 'moTa', 'chiTiet', 'thoiGian', 'calo', 'hinhAnh', 'loai', 'nguyen_lieu']