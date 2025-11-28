from django.shortcuts import render
from rest_framework import generics
from .models import MonAn
from .serializers import MonAnSerializer
# Create your views here.

# Lấy tất cả món ăn
class MonAnListView(generics.ListAPIView):
    queryset = MonAn.objects.all().order_by('maMonAn')
    serializer_class = MonAnSerializer


# Lấy món ăn theo loại (sáng, trưa, tối)
class MonAnByLoaiView(generics.ListAPIView):
    serializer_class = MonAnSerializer

    def get_queryset(self):
        # loai_mon là string từ url gửi sang <str:loai_mon>
        loai_can_tim = self.kwargs['loai_mon'] 
        
        # Lọc dữ liệu trong Database (loai = sang or loai = trua or loai = toi)
        return MonAn.objects.filter(loai=loai_can_tim)