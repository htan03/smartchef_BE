from django.urls import path
from .views import MonAnListView, MonAnByLoaiView, goi_y_mon_an, RegisterView, UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', UserProfileView.as_view(), name='user_profile'),

    path('mon-an/', MonAnListView.as_view()),

    path('mon-an/goi-y/', goi_y_mon_an),

    path('mon-an/<str:loai_mon>/', MonAnByLoaiView.as_view()),
]