from django.db import models

# Create your models here.
# 1. 分类模型 (Category)
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    # slug 用于生成好看的 URL，比如 /category/vases/，对分享链接很友好
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL标签")

    class Meta:
        verbose_name = "陶瓷分类"
        verbose_name_plural = "陶瓷分类"

    def __str__(self):
        return self.name


# 2. 产品模型 (Product)
class Product(models.Model):
    # 基本信息
    name = models.CharField(max_length=200, verbose_name="陶瓷名称")

    # 关系：一个分类下有多个产品 (一对多关联)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,  # 如果分类被删了，下面的产品也一并删除
        related_name='products',  # 方便反向查询：category.products.all()
        verbose_name="所属分类"
    )

    # Facebook 专用优化字段
    short_description = models.CharField(
        max_length=255,
        verbose_name="简短描述 (用于Facebook预览)",
        help_text="这段文字会显示在 Facebook 分享卡片的下方，建议控制在 150 字以内。"
    )

    # 详细描述 (网页里显示的详细内容)
    description = models.TextField(verbose_name="详细描述")

    # 媒体文件
    # upload_to 意思是图片会按年月自动分文件夹保存，比如 media/products/2026/06/
    image = models.ImageField(upload_to='products/%Y/%m/', verbose_name="主图(封面)")

    # 视频链接（可选，所以 blank=True）
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="YouTube视频链接",
        help_text="如果你有视频，请填入YouTube链接，留空则不显示视频。"
    )

    # 状态与时间
    is_active = models.BooleanField(default=True, verbose_name="是否上架")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        verbose_name = "陶瓷产品"
        verbose_name_plural = "陶瓷产品"
        ordering = ['-created_at']  # 默认按时间倒序排列，最新的排在最前面

    def __str__(self):
        return self.name