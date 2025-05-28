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

class ProductImageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return obj.get_absolute_url()

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj)
        image_list = []
        for image in images:
            image_list.append({
                "loc": image.image.url,
                "title": image.alt_name or obj.name,
                "caption": obj.short_description or obj.description[:100]
            })
        return image_list

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

class CategoryImageSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.8

	def items(self):
		return CategoryImage.objects.all()

	def lastmod(self, obj):
		return obj.created