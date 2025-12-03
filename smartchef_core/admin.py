from django.contrib import admin
from .models import MonAn, NguyenLieu

class NguyenLieuAdmin(admin.ModelAdmin):
    list_display = ('maNguyenLieu', 'tenNguyenLieu')
    search_fields = ['tenNguyenLieu']

class MonAnAdmin(admin.ModelAdmin):
    list_display = ('tenMonAn', 'loai', 'thoiGian', 'calo', 'hinh_anh_preview')
    search_fields = ('tenMonAn',)
    list_filter = ('loai',)

    filter_horizontal = ('nguyen_lieu',) 

# Đăng ký
admin.site.register(MonAn, MonAnAdmin)
admin.site.register(NguyenLieu, NguyenLieuAdmin)