from django.shortcuts import render, redirect
from django.views import View

from django.http import HttpResponse

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






