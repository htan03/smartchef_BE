import google.generativeai as genai
import os
import json
from PIL import Image
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.shortcuts import render
from rest_framework import generics
from .models import MonAn, NguyenLieu # Import Models
from .serializers import MonAnSerializer
from rest_framework.decorators import api_view # Custom API
from rest_framework.response import Response
import unidecode


# Create your views here.

# KHỞI TẠO GEMINI API
def khoi_tao_gemini():
    """Khởi tạo Gemini API với API Key từ .env"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

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

# API PHÂN TÍCH ẢNH BẰNG GEMINI AI
@api_view(['POST'])
@parser_classes([MultiPartParser])
def phan_tich_nguyen_lieu(request):
    """
    POST /api/phan-tich-anh/
    Body: FormData { image: File }
    
    Luồng:
    1. Nhận ảnh từ Frontend
    2. Gọi Gemini AI phân tích → Trả về JSON nguyên liệu tiếng Việt
    3. Kiểm tra nguyên liệu trong DB, thêm mới nếu chưa có
    4. Tìm món ăn từ danh sách nguyên liệu
    5. Trả về kết quả
    """
    
    # VALIDATE ẢNH 
    if 'image' not in request.FILES:
        print("Không tìm thấy file ảnh trong request.")
        return Response({
            "success": False,
            "message": "Vui lòng chọn ảnh!"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = request.FILES['image']
    
    # Kiểm tra định dạng
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    if image_file.content_type not in allowed_types:
        print(f"Loại file không hợp lệ: {image_file.content_type}")
        return Response({
            "success": False,
            "message": "Chỉ chấp nhận file ảnh JPG/PNG!"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Kiểm tra kích thước (tối đa 5MB)
    if image_file.size > 5 * 1024 * 1024:
        print(f"File ảnh quá lớn: {image_file.size} bytes")
        return Response({
            "success": False,
            "message": "Ảnh quá lớn! Vui lòng chọn ảnh < 5MB"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # BƯỚC 1: MỞ ẢNH BẰNG PIL
        image = Image.open(image_file)
        
        # BƯỚC 2: GỌI GEMINI AI PHÂN TÍCH ẢNH
        print("🤖 Đang gọi Gemini AI...")
        model = khoi_tao_gemini()
        
        # Prompt của bạn
        prompt = """Analyze the provided food ingredient image and extract all edible ingredients that can be used to cook a dish.

**Requirements:**
- Input: Image containing food ingredients
- Focus: Only identify ingredients that can be cooked into a meal
- Ignore: Non-edible items and objects that cannot be used for cooking
- Output format: JSON only, exactly as shown below
- Ingredient names: Must be in Vietnamese language
- Response: ONLY return the JSON, nothing else

**Output Format:**
{"data": ["Nguyên liệu 1", "Nguyên liệu 2", "Nguyên liệu 3"]}
```"""
        
        response = model.generate_content([prompt, image])
        text_response = response.text.strip()
        
        print(f"Gemini AI trả về: {text_response}")
        
        # BƯỚC 3: XỬ LÝ KẾT QUẢ JSON 
        # Loại bỏ markdown code block nếu có ( ... ```)
        if text_response.startswith('```'):
            text_response = text_response.split('```')[1]
            if text_response.startswith('json'):
                text_response = text_response[4:]
            text_response = text_response.strip()
        
        # Parse JSON
        try:
            result_json = json.loads(text_response)
            nguyen_lieu_list = result_json.get('data', [])
        except json.JSONDecodeError:
            return Response({
                "success": False,
                "message": "AI trả về định dạng không hợp lệ!"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Kiểm tra có nguyên liệu không
        if not nguyen_lieu_list or len(nguyen_lieu_list) == 0:
            return Response({
                "success": False,
                "message": "AI không nhận diện được nguyên liệu nào! Vui lòng chụp ảnh rõ hơn."
            })
        
        # BƯỚC 4: KIỂM TRA & THÊM VÀO DATABASE (NẾU CHƯA CÓ)
        nguyen_lieu_ids = []
        nguyen_lieu_moi = []
        nguyen_lieu_data = []
        
        for ten_nguyen_lieu in nguyen_lieu_list:
            if not ten_nguyen_lieu.strip():
                continue
            
            # Tìm trong database (không phân biệt hoa thường)
            nguyen_lieu_obj = NguyenLieu.objects.filter(
                tenNguyenLieu__iexact=ten_nguyen_lieu.strip()
            ).first()
            
            if nguyen_lieu_obj:
                # Đã có trong DB
                nguyen_lieu_ids.append(nguyen_lieu_obj.maNguyenLieu)
                nguyen_lieu_data.append({
                    "id": nguyen_lieu_obj.maNguyenLieu,
                    "ten": nguyen_lieu_obj.tenNguyenLieu,
                    "la_moi": False
                })
            else:
                # CHƯA CÓ thì THÊM MỚI
                nguyen_lieu_moi_obj = NguyenLieu.objects.create(
                    tenNguyenLieu=ten_nguyen_lieu.strip()
                )
                nguyen_lieu_ids.append(nguyen_lieu_moi_obj.maNguyenLieu)
                nguyen_lieu_moi.append(ten_nguyen_lieu.strip())
                nguyen_lieu_data.append({
                    "id": nguyen_lieu_moi_obj.maNguyenLieu,
                    "ten": nguyen_lieu_moi_obj.tenNguyenLieu,
                    "la_moi": True
                })
                
                print(f"Đã thêm nguyên liệu mới: {ten_nguyen_lieu}")
        
        # BƯỚC 5: TÌM MÓN ĂN THEO NGUYÊN LIỆU
        mon_an_db = tim_mon_an_theo_nguyen_lieu(nguyen_lieu_ids)
        
        # BƯỚC 6: TRẢ VỀ KẾT QUẢ 
        return Response({
            "success": True,
            "nguyen_lieu": nguyen_lieu_data,
            "so_nguyen_lieu_moi": len(nguyen_lieu_moi),
            "so_mon_tim_thay": len(mon_an_db),
            "mon_an": MonAnSerializer(mon_an_db, many=True, context={'request': request}).data
        })
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            "success": False,
            "message": f"Lỗi xử lý ảnh: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# HÀM HỖ TRỢ: TÌM MÓN ĂN THEO NGUYÊN LIỆU
def tim_mon_an_theo_nguyen_lieu(nguyen_lieu_ids):
    """Tìm món ăn dựa trên danh sách ID nguyên liệu"""
    all_mon_an = MonAn.objects.prefetch_related('nguyen_lieu').all()
    results = []
    
    for mon in all_mon_an:
        mon_nguyen_lieu_ids = list(
            mon.nguyen_lieu.values_list('maNguyenLieu', flat=True)
        )
        
        # Đếm số nguyên liệu trùng khớp
        match_count = len(set(nguyen_lieu_ids) & set(mon_nguyen_lieu_ids))
        
        if match_count > 0:
            results.append({
                'mon_an': mon,
                'score': match_count
            })
    
    # Sắp xếp theo score giảm dần
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Lấy top 10
    return [item['mon_an'] for item in results[:10]]