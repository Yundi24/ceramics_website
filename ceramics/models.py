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
        # 拦截判断：如果上传了新图片，并且还没有生成同名的缩略图
        if self.image and not self.thumbnail:
            # 打开原图
            img = Image.open(self.image)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 【操作 A：生成缩略图 (用于 Facebook 和列表)】
            # 复制一份图片对象来做缩略图，避免影响原图
            thumb_img = img.copy()
            thumb_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            thumb_img.save(thumb_io, format='JPEG', quality=80)

            # 获取原文件名
            file_name = os.path.splitext(os.path.basename(self.image.name))[0]

            # 把缩略图存进新字段
            self.thumbnail.save(
                f"{file_name}_thumb.jpg",
                ContentFile(thumb_io.getvalue()),
                save=False
            )

            # 【操作 B：优化高清大图 (防备 16MB 杀手)】
            # 即便是详情页，我们也把它限制在 2500 像素以内，转换为极高质量的 JPG (95%)
            # 这样 16MB 的 PNG 也会变成 1MB 左右的极品高清 JPG，网页加载瞬间提升！
            img.thumbnail((2500, 2500), Image.Resampling.LANCZOS)
            hq_io = BytesIO()
            img.save(hq_io, format='JPEG', quality=95)
            self.image.save(
                f"{file_name}_hq.jpg",
                ContentFile(hq_io.getvalue()),
                save=False
            )

        super().save(*args, **kwargs)