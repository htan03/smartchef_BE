# thucdon/admin.py
from django.contrib import admin
from .models import MonAn

@admin.register(MonAn)
class MonAnAdmin(admin.ModelAdmin):
    # 1. HIỂN THỊ
    list_display = ('maMonAn', 'tenMonAn', 'hinh_anh_preview', 'loai', 'thoiGian', 'calo')
    
    # 2. TÌM KIẾM (theo tên và mô tả)
    search_fields = ('tenMonAn', 'moTa')
    
    # 3. BỘ LỌC (bên phải)
    list_filter = ('loai', 'thoiGian')
    
    # 4. PHÂN TRANG (Mỗi trang 10 món)
    list_per_page = 10

    # 5. FORM NHẬP LIỆU
    fieldsets = (
        ('Thông tin chính', {
            'fields': ('tenMonAn', 'loai', 'hinhAnh', 'moTa')
        }),
        ('Chi tiết dinh dưỡng & Cách nấu', {
            'fields': ('chiTiet', 'thoiGian', 'calo', 'dsNguyenLieu')
        }),
    )
    
    # Cho phép click vào ảnh để xem full size
    readonly_fields = ('hinh_anh_preview',)