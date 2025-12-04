from django.shortcuts import render
from rest_framework import generics
from .models import MonAn
from .serializers import MonAnSerializer
from rest_framework.decorators import api_view # Custom API
from rest_framework.response import Response
import unidecode
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

# API gợi ý món ăn theo nguyên liệu
@api_view(['GET'])
def goi_y_mon_an(request):
    """
    API: /api/mon-an/goi-y/?nguyen_lieu=trung,ca chua
    """
    # 1. Lấy input từ URL
    query_string = request.GET.get('nguyen_lieu', '')
    if not query_string:
        return Response([])

    # 2. Chuẩn hóa Input người dùng (Tách phẩy -> Bỏ dấu -> Chữ thường)
    # VD: "Trứng, Hành" -> ['trung', 'hanh']
    user_ingredients = [
        unidecode.unidecode(x.strip().lower()) 
        for x in query_string.split(',') if x.strip()
    ]

    # 3. Lấy tất cả món ăn kèm theo nguyên liệu (prefetch_related để tối ưu SQL)
    all_mon_an = MonAn.objects.prefetch_related('nguyen_lieu').all()
    results = []

    # 4. Thuật toán chấm điểm
    for mon in all_mon_an:
        match_count = 0
        
        # Lấy danh sách nguyên liệu từ quan hệ ManyToMany
        # mon.nguyen_lieu.all() trả về danh sách các object NguyenLieu
        db_ingredients = mon.nguyen_lieu.all()
        
        for ing_obj in db_ingredients:
            # Lấy tên nguyên liệu trong DB và chuẩn hóa
            # ing_obj.tenNguyenLieu lấy từ Model NguyenLieu
            ing_name_norm = unidecode.unidecode(ing_obj.tenNguyenLieu.lower())
            
            # So sánh với danh sách User nhập
            for user_ing in user_ingredients:
                # Dùng "in" để tìm kiếm tương đối (fuzzy match)
                # VD: User nhập "bò" sẽ khớp với "thịt bò", "gân bò"
                if user_ing in ing_name_norm:
                    match_count += 1
                    break 
        
        # 5. Nếu có điểm trùng khớp thì thêm vào kết quả
        if match_count > 0:
            results.append({
                'mon_an': mon,
                'score': match_count
            })

    # 6. Sắp xếp giảm dần theo điểm score
    results.sort(key=lambda x: x['score'], reverse=True)

    # 7. Trả về JSON
    sorted_mon_an = [item['mon_an'] for item in results]
    serializer = MonAnSerializer(sorted_mon_an, many=True, context={'request': request})
    
    return Response(serializer.data)