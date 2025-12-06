from django.shortcuts import render
from rest_framework import generics
from .models import MonAn
from .models import YeuThich
from rest_framework import status
from .serializers import MonAnSerializer
from rest_framework.decorators import api_view # Custom API
from rest_framework.response import Response
import unidecode

from django.db.models import Count

from .serializers import UserRegisterSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .serializers import ChangePasswordSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserProfileSerializer

# Create your views here.

# Đăng ký tài khoản
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

# Lấy thông tin user
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated] # Bắt buộc phải có Token mới được xem

    def get(self, request):
        user_hien_tai = request.user 
        
        serializer = UserProfileSerializer(user_hien_tai)
        return Response(serializer.data)


# API đổi mật khẩu
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_pass = serializer.data['old_password']
            new_pass = serializer.data['new_password']

            # KIỂM TRA MẬT KHẨU CŨ
            if not user.check_password(old_pass):
                return Response(
                    {"old_password": ["Mật khẩu cũ không chính xác."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Kiểm tra xem mật khẩu mới có trùng mật khẩu cũ không
            if old_pass == new_pass:
                return Response(
                    {"new_password": ["Mật khẩu mới không được trùng với mật khẩu cũ."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_pass)
            user.save()
            
            return Response({"message": "Đổi mật khẩu thành công!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# API like/unlike
class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mon_an_id):
        user = request.user
        try:
            mon_an = MonAn.objects.get(pk=mon_an_id)
        except MonAn.DoesNotExist:
            return Response({"error": "Món ăn không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra: Có chưa? Nếu chưa thì tạo, có rồi thì lấy ra
        obj, created = YeuThich.objects.get_or_create(nguoi_dung=user, mon_an=mon_an)

        if not created:
            # Nếu đã có (created = False) -> Nghĩa là User muốn BỎ thích -> Xóa
            obj.delete()
            return Response({"status": "unliked", "is_favorite": False})
        else:
            # Nếu vừa tạo mới (created = True) -> Nghĩa là User muốn THÍCH
            return Response({"status": "liked", "is_favorite": True})
        
# API Xem danh sách yêu thích
class MyFavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Lọc những món mà User này đã thích
        mon_an_yeu_thich = MonAn.objects.filter(yeuthich__nguoi_dung=user)
        serializer = MonAnSerializer(mon_an_yeu_thich, many=True, context={'request': request})
        return Response(serializer.data)
    
# API món ăn nổi bật
class TopMonAnView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        top_mon_an = MonAn.objects.annotate(
            so_luot_thich=Count('yeuthich') 
        ).order_by('-so_luot_thich')[:5]
        serializer = MonAnSerializer(top_mon_an, many=True, context={'request': request})
        
        return Response(serializer.data)