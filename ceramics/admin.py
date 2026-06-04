from django.contrib import admin
from .models import Category, Product

# 注册分类模型
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    # 当你在后台输入分类名称时，自动拼音/英文填充 slug 字段
    prepopulated_fields = {'slug': ('name',)}

# 注册产品模型
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 后台列表页面显示哪些列
    list_display = ('name', 'category', 'is_active', 'created_at')
    # 右侧增加过滤器
    list_filter = ('category', 'is_active')
    # 增加搜索框
    search_fields = ('name', 'short_description')
    # 点击哪些字段可以进入编辑页面
    list_display_links = ('name',)