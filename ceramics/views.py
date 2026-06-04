from django.views.generic import ListView, DetailView
from .models import Product


# 1. 首页/产品列表页
class ProductListView(ListView):
    model = Product
    template_name = 'ceramics/product_list.html'
    context_object_name = 'products'  # 在 HTML 里使用的变量名

    def get_queryset(self):
        # 覆写查询逻辑：只展示 is_active=True (已上架) 的产品
        return Product.objects.filter(is_active=True)


# 2. 产品详情页
class ProductDetailView(DetailView):
    model = Product
    template_name = 'ceramics/product_detail.html'
    context_object_name = 'product'