from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

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
    # 1. 详情页用的高清大图
    image = models.ImageField(upload_to='products/%Y/%m/', verbose_name="高清大图")

    # 2. 用于列表和 Facebook 的缩略图
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/%Y/%m/',
        blank=True, null=True,
        verbose_name="缩略图 (系统自动生成)"
    )

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

    @property
    def embed_video_url(self):
        """自动把普通 YouTube 链接转换为可嵌入的 iframe 链接"""
        if not self.video_url:
            return None

        url = self.video_url
        video_id = ""

        # 处理普通链接 (https://www.youtube.com/watch?v=xxxxxx)
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        # 处理手机端短链接 (https://youtu.be/xxxxxx)
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"

        # 如果不是 YouTube 链接，原样返回
        return url

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new_image = False  # 状态标记

        if self.pk:  # 如果 self.pk 存在，说明这是“修改旧商品”
            try:
                old_product = Product.objects.get(pk=self.pk)
                # 对比：数据库里的旧图 != 前端刚传上来的新图
                if old_product.image != self.image:
                    is_new_image = True
                    # 删除旧图
                    if old_product.image:
                        old_product.image.delete(save=False)
                    if old_product.thumbnail:
                        old_product.thumbnail.delete(save=False)
            except Product.DoesNotExist:
                pass
        else:
            # 如果 self.pk 不存在，说明是“新建商品”，那肯定是新图
            is_new_image = True

        if self.image and is_new_image:
            img = Image.open(self.image)
            if img.mode == "P":
                img = img.convert("RGBA")

            file_name = os.path.splitext(os.path.basename(self.image.name))[0]

            # 操作 A：生成缩略图 (纯 WebP)
            thumb_img = img.copy()
            thumb_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            thumb_img.save(thumb_io, format='WEBP', quality=80)
            self.thumbnail.save(f"{file_name}_thumb.webp", ContentFile(thumb_io.getvalue()), save=False)

            # 操作 B：优化高清大图 (纯 WebP)
            img.thumbnail((2500, 2500), Image.Resampling.LANCZOS)
            hq_io = BytesIO()
            img.save(hq_io, format='WEBP', quality=90)
            self.image.save(f"{file_name}_hq.webp", ContentFile(hq_io.getvalue()), save=False)

        super().save(*args, **kwargs)