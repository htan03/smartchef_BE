from django.db import models
from django.utils.html import mark_safe
# Create your models here.

class MonAn(models.Model):
    LOAI_CHOICES = [
        ('sang', 'Bữa sáng'),
        ('trua', 'Bữa trưa'),
        ('toi', 'Bữa tối'),
    ]

    # Django tự tạo id mặc định, nhưng nếu bạn muốn đặt tên là maMonAn:
    maMonAn = models.AutoField(primary_key=True, verbose_name="Mã món ăn")

    # tenMonAn: VARCHAR(255)
    tenMonAn = models.CharField(max_length=255, verbose_name="Tên món ăn")

    # moTa: TEXT
    moTa = models.TextField(verbose_name="Mô tả ngắn")

    # chiTiet: TEXT (Markdown)
    chiTiet = models.TextField(verbose_name="Chi tiết (Markdown)")

    # thoiGian: INTEGER
    thoiGian = models.IntegerField(verbose_name="Thời gian nấu (phút)")

    # calo: INTEGER
    calo = models.IntegerField(verbose_name="Lượng Calo (kcal)")

    # hinhAnh: TEXT (URL ảnh)
    hinhAnh = models.ImageField(upload_to='monan/', verbose_name="Ảnh món ăn", blank=True, null=True)

    # loai: VARCHAR(100)
    loai = models.CharField(max_length=100, choices=LOAI_CHOICES, verbose_name="Loại bữa ăn")

    # dsNguyenLieu: JSONB
    # Cần Django 3.0+ và database là PostgreSQL để dùng tốt nhất
    dsNguyenLieu = models.JSONField(verbose_name="Danh sách ID nguyên liệu", default=list)

    # dsNguyenLieu_hash: VARCHAR(64)
    dsNguyenLieu_hash = models.CharField(max_length=64, verbose_name="Hash nguyên liệu", blank=True, null=True)

    # Hàm hỗ trợ hiển thị ảnh thu nhỏ trong Admin
    def hinh_anh_preview(self):
        if self.hinhAnh:
            return mark_safe(f'<img src="{self.hinhAnh.url}" width="100" style="border-radius: 5px;" />')
        return "Chưa có ảnh"
    
    hinh_anh_preview.short_description = "Xem trước"

    def __str__(self):
        return self.tenMonAn

    class Meta:
        verbose_name = "Món Ăn"
        verbose_name_plural = "Danh sách Món Ăn"