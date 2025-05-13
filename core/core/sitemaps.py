from django.contrib.sitemaps import Sitemap
from shop.models import Store, Product, Category, BlogPost, ProductImage, CategoryImage, Tag

class StoreSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Store.objects.all()

    def lastmod(self, obj):
        return obj.created

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created

class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Category.objects.all()

class TagSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.created_date

class BlogPostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return BlogPost.objects.all()

    def lastmod(self, obj):
        return obj.created_date

class ProductImageSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ProductImage.objects.all()

    def lastmod(self, obj):
        return obj.created

class CategoryImageSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return CategoryImage.objects.all()

    def lastmod(self, obj):
        return obj.created