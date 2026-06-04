from django.urls import path
from . import views

urlpatterns = [
    # 首页：展示列表
    path('', views.ProductListView.as_view(), name='product_list'),
    # 详情页：例如 /product/1/
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]