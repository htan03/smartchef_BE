from django.urls import path
from .views import MonAnListView, MonAnByLoaiView

urlpatterns = [
    path('mon-an/', MonAnListView.as_view()),

    path('mon-an/<str:loai_mon>/', MonAnByLoaiView.as_view()),
]