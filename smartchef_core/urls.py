from django.urls import path
from .views import MonAnListView, MonAnByLoaiView, goi_y_mon_an, phan_tich_nguyen_lieu

urlpatterns = [
    path('mon-an/', MonAnListView.as_view()),

    path('mon-an/goi-y/', goi_y_mon_an),

    path('mon-an/<str:loai_mon>/', MonAnByLoaiView.as_view()),

    path('phan-tich-anh/', phan_tich_nguyen_lieu, name='phan_tich_anh'),
]