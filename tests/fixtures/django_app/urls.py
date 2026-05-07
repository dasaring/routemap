from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('users/', views.UserListView, name='user-list'),
    path('users/<int:pk>/', views.UserDetailView, name='user-detail'),
    path('auth/login/', views.LoginView, name='login'),
    path('auth/logout/', views.LogoutView, name='logout'),
    re_path(r'^legacy/items/$', views.LegacyItemView, name='legacy-items'),
    path('api/', include(router.urls)),
]
