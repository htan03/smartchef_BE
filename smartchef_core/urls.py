from django.urls import path
from .views import MonAnListView, MonAnByLoaiView, goi_y_mon_an, RegisterView, UserProfileView, ToggleFavoriteView, MyFavoritesView, TopMonAnView, ChangePasswordView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Đăng nhập/ đăng ký/ refresh token
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Xem thông tin user
    path('profile/', UserProfileView.as_view(), name='user_profile'),

    # Lấy toàn bộ danh sách món ăn
    path('mon-an/', MonAnListView.as_view()),

    # Gợi ý món ăn dựa vào nguyên liệu
    path('mon-an/goi-y/', goi_y_mon_an),

    # Món ăn yêu thích 
    path('mon-an/top-yeu-thich/', TopMonAnView.as_view()),

    # Lọc món ăn theo loại: sang/trua/chieu
    path('mon-an/<str:loai_mon>/', MonAnByLoaiView.as_view()),

    #Yêu thích món ăn
    path('yeu-thich/toggle/<int:mon_an_id>/', ToggleFavoriteView.as_view()),

    # Xem list yêu thhíc: /api/yeu-thich/my-list/
    path('yeu-thich/my-list/', MyFavoritesView.as_view()),

    # Đổi mật khẩu
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]