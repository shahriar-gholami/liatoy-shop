from django.shortcuts import render, redirect
from django.views import View
from django.template.loader import render_to_string

from django.http import HttpResponse


from .sitemaps import ProductImageSitemap

def custom_sitemap(request):
    products = ProductImageSitemap().items()
    for p in products:
        p.images = ProductImageSitemap().get_images(p)
    xml = render_to_string("shop/sitemap_with_images.xml", {"products": products, "request": request})
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /products/featured/",
        "Disallow: /add-to-favorites/",
        "Disallow: /owner/",
        "Disallow: /edit-home/",
        "Disallow: /customer/",
        "Disallow: /delivery/",
        "Host: liatoy.com",
        "Sitemap: https://liatoy/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")






