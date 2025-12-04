from django.urls import path
from .views import MonAnListView, MonAnByLoaiView, goi_y_mon_an

urlpatterns = [
    path('mon-an/', MonAnListView.as_view()),

    path('mon-an/goi-y/', goi_y_mon_an),

    path('mon-an/<str:loai_mon>/', MonAnByLoaiView.as_view()),
]