from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import *
from .views import robots_txt
from .views import custom_sitemap


sitemaps = {
    'store': StoreSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog posts': BlogPostSitemap,
    'tags' : TagSitemap,
    'product images': ProductImageSitemap
}

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("shop.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-images.xml', custom_sitemap, name='sitemap_images'),
    # path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
