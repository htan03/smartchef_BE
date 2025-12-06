from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User
# --- Bảng Nguyên Liệu:
class NguyenLieu(models.Model):
    maNguyenLieu = models.AutoField(primary_key=True, verbose_name="Mã nguyên liệu")
    tenNguyenLieu = models.CharField(max_length=200, unique=True, verbose_name="Tên nguyên liệu")
    
    def __str__(self):
        return self.tenNguyenLieu

    class Meta:
        verbose_name = "Nguyên Liệu (Tags)"
        verbose_name_plural = "Danh sách Nguyên Liệu"


# --- Bảng Món Ăn:
class MonAn(models.Model):
    LOAI_CHOICES = [
        ('sang', 'Bữa sáng'),
        ('trua', 'Bữa trưa'),
        ('toi', 'Bữa tối'),
    ]

    maMonAn = models.AutoField(primary_key=True, verbose_name="Mã món ăn")
    tenMonAn = models.CharField(max_length=255, verbose_name="Tên món ăn")
    moTa = models.TextField(verbose_name="Mô tả ngắn")
    
    chiTiet = models.TextField(verbose_name="Chi tiết công thức (Markdown)")

    thoiGian = models.IntegerField(verbose_name="Thời gian nấu (phút)")
    calo = models.IntegerField(verbose_name="Lượng Calo (kcal)")
    
    # Ảnh món ăn
    hinhAnh = models.ImageField(upload_to='monan/', verbose_name="Ảnh món ăn", blank=True, null=True)
    
    loai = models.CharField(max_length=100, choices=LOAI_CHOICES, verbose_name="Loại bữa ăn")

    # --- LIÊN KẾT TAGS ---
    nguyen_lieu = models.ManyToManyField(
        NguyenLieu, 
        verbose_name="Chọn nguyên liệu",
        related_name='cac_mon_an',
        blank=True
    )

    # Hàm hiển thị ảnh nhỏ trong Admin
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

class YeuThich(models.Model):
    # Ai thích?
    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    # Thích món nào?
    mon_an = models.ForeignKey(MonAn, on_delete=models.CASCADE, verbose_name="Món ăn")
    # Thích lúc nào? (Để sắp xếp món mới thích lên đầu)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Một người chỉ được thích 1 món 1 lần
        unique_together = ('nguoi_dung', 'mon_an')
        verbose_name = "Lượt Yêu Thích"
        verbose_name_plural = "Danh sách Yêu Thích"

    def __str__(self):
        return f"{self.nguoi_dung.username} thích {self.mon_an.tenMonAn}"