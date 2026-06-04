from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category


# 1. 首页/产品列表页 (带有搜索和分类功能)
class ProductListView(ListView):
    model = Product
    template_name = 'ceramics/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # 1. 默认查询所有已上架的产品
        queryset = Product.objects.filter(is_active=True)

        # 2. 获取浏览器 URL 里的参数
        search_query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')

        # 3. 处理搜索逻辑 (如果用户输入了关键词)
        if search_query:
            # 魔法：__icontains 代表"忽略大小写包含"。
            # Q(...) | Q(...) 代表：只要名字包含关键词，或者描述包含关键词，都搜出来！
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(short_description__icontains=search_query)
            )

        # 4. 处理分类逻辑 (如果用户点击了某个分类)
        if category_slug:
            # category__slug 是 Django ORM 的跨表查询语法
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    # 把分类列表和当前的搜索状态传给前端网页
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取所有分类，传给前端画按钮
        context['categories'] = Category.objects.all()
        # 把当前的分类和搜索词再传回去，为了让按钮保持高亮和搜索框保留文字
        context['current_category'] = self.request.GET.get('category', '')
        context['current_query'] = self.request.GET.get('q', '')
        return context


# 2. 产品详情页
class ProductDetailView(DetailView):
    model = Product
    template_name = 'ceramics/product_detail.html'
    context_object_name = 'product'