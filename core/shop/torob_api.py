import math
from html import unescape
from urllib.parse import urlparse, unquote

from django.conf import settings
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework.views import APIView
from .torob_auth import TorobJWTAuthentication


from .models import Product, ProductImage, Variety


TOROB_API_VERSION = "torob_api_v3"
TOROB_PAGE_SIZE = 100


def clean_text(value, max_len=None):
    """
    تبدیل RichText/HTML به متن ساده برای خروجی ترب
    """
    if value is None:
        return None

    text = strip_tags(str(value))
    text = unescape(text)
    text = " ".join(text.split())


    if max_len:
        text = text[:max_len]

    return text


def absolute_url(request, url):
    if not url:
        return None

    if url.startswith("http://") or url.startswith("https://"):
        return url

    site_url = getattr(settings, "SITE_URL", None)

    if site_url:
        return site_url.rstrip("/") + "/" + url.lstrip("/")

    return request.build_absolute_uri(url)



def datetime_to_iso(dt):
    """
    تبدیل تاریخ به ISO8601 دارای timezone
    """
    if not dt:
        return None

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    dt = timezone.localtime(dt)
    return dt.isoformat()


def extract_slug_from_url(page_url):
    """
    استخراج slug محصول از URL کامل.
    مثال:
    https://liatoy.com/products/some-slug/
    خروجی:
    some-slug
    """
    parsed = urlparse(page_url)
    path = parsed.path.strip("/")

    if not path:
        return None

    parts = path.split("/")

    if not parts:
        return None

    slug = parts[-1]
    return unquote(slug)


def get_current_price(product):
    """
    قیمت فعلی محصول برای ترب
    """
    if (
        product.off_active
        and product.sales_price is not None
        and int(product.sales_price) > 0
    ):
        return int(product.sales_price)

    return int(product.price or 0)


def get_old_price(product):
    """
    قیمت قبل تخفیف
    """
    if (
        product.off_active
        and product.sales_price is not None
        and int(product.sales_price) > 0
        and int(product.sales_price) < int(product.price or 0)
    ):
        return int(product.price)

    return None


def product_is_available(product):
    """
    موجودی بر اساس تنوع‌ها.
    اگر حداقل یک Variety با stock بالای صفر داشته باشد، محصول موجود است.
    """
    varieties = getattr(product, "prefetched_varieties", None)

    if varieties is not None:
        return any(v.stock > 0 for v in varieties)

    return Variety.objects.filter(product=product, stock__gt=0).exists()


def get_category_name(product):
    """
    دریافت اولین دسته‌بندی محصول
    """
    categories = list(product.category.all())

    if not categories:
        return None

    return clean_text(categories[0].name, 200)


def get_image_links(request, product):
    """
    دریافت تصاویر محصول.
    اولین تصویر طبق ordering مدل ProductImage همان تصویر اصلی در نظر گرفته می‌شود.
    """
    images = getattr(product, "prefetched_images", None)

    if images is None:
        images = ProductImage.objects.filter(product=product).order_by("created")

    links = []

    for image_obj in images:
        if image_obj.image:
            image_url = image_obj.image.url.split("?")[0]
            full_url = absolute_url(request, image_url)
            if full_url:
                links.append(full_url[:1000])

    # اگر محصول تصویر نداشت، از get_main_image استفاده می‌کنیم
    if not links:
        try:
            main_image = product.get_main_image()
            full_url = absolute_url(request, main_image)
            if full_url:
                links.append(full_url[:1000])
        except Exception:
            pass

    return links


def get_spec(product):
    """
    ویژگی‌های محصول برای ترب.
    فعلاً از اطلاعات موجود مدل استفاده می‌کنیم.
    اگر بعداً ویژگی‌ها ساختارمند شدند، این بخش را بهتر می‌کنیم.
    """
    spec = {}

    if product.brand:
        spec["برند"] = clean_text(product.brand.name, 200) if hasattr(product.brand, "name") else str(product.brand)

    if product.age:
        spec["گروه سنی"] = clean_text(product.age.name, 200) if hasattr(product.age, "name") else str(product.age)

    spec["کالای اصلی"] = "بله" if product.is_original else "خیر"

    features_text = clean_text(product.features, 500)
    if features_text:
        spec["ویژگی‌ها"] = features_text

    return spec


def serialize_product(request, product):
    """
    تبدیل Product جنگو به فرمت مورد انتظار Torob API v3
    """

    page_url = absolute_url(request, product.get_absolute_url())

    return {
        "page_unique": f"product_{product.id}",
        "page_url": page_url[:1500] if page_url else "",
        "product_group_id": str(product.id),
        "title": clean_text(product.name, 500) or "",
        "subtitle": clean_text(product.seo_title, 500),
        "current_price": get_current_price(product),
        "old_price": get_old_price(product),
        "availability": product_is_available(product),
        "category_name": get_category_name(product),
        "image_links": get_image_links(request, product),
        "spec": get_spec(product),
        "guarantee": None,
        "short_desc": clean_text(product.short_description, 500),
        "date_added": datetime_to_iso(product.created),
        "date_updated": datetime_to_iso(product.updated),
    }


def error_response(message):
    return JsonResponse(
        {"error": message},
        status=400,
        json_dumps_params={"ensure_ascii": False},
    )


def base_products_queryset():
    """
    QuerySet پایه محصولات برای ترب.
    
    اگر بعداً فیلدهایی مثل is_active یا show_in_torob اضافه کردی،
    همین‌جا باید فیلتر شوند.
    """
    return (
        Product.objects
        .all()
        .prefetch_related(
            "category",
            Prefetch(
                "productimage_set",
                queryset=ProductImage.objects.order_by("created"),
                to_attr="prefetched_images",
            ),
            Prefetch(
                "variety_set",
                queryset=Variety.objects.all(),
                to_attr="prefetched_varieties",
            ),
        )
        .select_related("brand", "age")
    )


class TorobProductsAPIView(APIView):
    """
    Endpoint:
    POST /torob_api/v3/products
    """

    authentication_classes = [TorobJWTAuthentication]
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, dict) or not data:
            return error_response("request body is empty or invalid")

        keys = set(data.keys())

        allowed_modes = [
            {"page", "sort"},
            {"page_urls"},
            {"page_uniques"},
        ]

        if keys not in allowed_modes:
            return error_response(
                "invalid parameters. request body must contain exactly one of: "
                "{page, sort}, {page_urls}, {page_uniques}"
            )

        if "page" in data and "sort" in data:
            return self.handle_paginated_products(request, data)

        if "page_urls" in data:
            return self.handle_page_urls(request, data)

        if "page_uniques" in data:
            return self.handle_page_uniques(request, data)

        return error_response("invalid request")

    def handle_paginated_products(self, request, data):
        page = data.get("page")
        sort = data.get("sort")

        if not isinstance(page, int):
            return error_response("page parameter must be int")

        if page < 1:
            return error_response("page parameter must start from 1")

        if not isinstance(sort, str):
            return error_response("sort parameter must be string")

        if sort not in ["date_added_desc", "date_updated_desc"]:
            return error_response("sort parameter is invalid")

        qs = base_products_queryset()

        if sort == "date_added_desc":
            qs = qs.order_by("-created", "-id")
        elif sort == "date_updated_desc":
            qs = qs.order_by("-updated", "-id")

        total = qs.count()
        max_pages = max(1, math.ceil(total / TOROB_PAGE_SIZE))

        start = (page - 1) * TOROB_PAGE_SIZE
        end = start + TOROB_PAGE_SIZE

        products = qs[start:end]

        result = {
            "api_version": TOROB_API_VERSION,
            "current_page": page,
            "total": total,
            "max_pages": max_pages,
            "products": [
                serialize_product(request, product)
                for product in products
            ],
        }

        return JsonResponse(
            result,
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )

    def handle_page_urls(self, request, data):
        page_urls = data.get("page_urls")

        if not isinstance(page_urls, list):
            return error_response("page_urls parameter must be list")

        if len(page_urls) == 0:
            return error_response("page_urls parameter must not be empty")

        if not all(isinstance(item, str) for item in page_urls):
            return error_response("all page_urls items must be string")

        slugs = []

        for page_url in page_urls:
            slug = extract_slug_from_url(page_url)
            if slug:
                slugs.append(slug)

        if not slugs:
            products = []
        else:
            products = list(
                base_products_queryset()
                .filter(slug__in=slugs)
                .order_by("-created", "-id")
            )

        result = {
            "api_version": TOROB_API_VERSION,
            "current_page": 1,
            "total": len(products),
            "max_pages": 1,
            "products": [
                serialize_product(request, product)
                for product in products
            ],
        }

        return JsonResponse(
            result,
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )

    def handle_page_uniques(self, request, data):
        page_uniques = data.get("page_uniques")

        if not isinstance(page_uniques, list):
            return error_response("page_uniques parameter must be list")

        if len(page_uniques) == 0:
            return error_response("page_uniques parameter must not be empty")

        if not all(isinstance(item, str) for item in page_uniques):
            return error_response("all page_uniques items must be string")

        product_ids = []

        for page_unique in page_uniques:
            if page_unique.startswith("product_"):
                raw_id = page_unique.replace("product_", "", 1)
            else:
                raw_id = page_unique

            if raw_id.isdigit():
                product_ids.append(int(raw_id))

        if not product_ids:
            products = []
        else:
            products = list(
                base_products_queryset()
                .filter(id__in=product_ids)
                .order_by("-created", "-id")
            )

        result = {
            "api_version": TOROB_API_VERSION,
            "current_page": 1,
            "total": len(products),
            "max_pages": 1,
            "products": [
                serialize_product(request, product)
                for product in products
            ],
        }

        return JsonResponse(
            result,
            status=200,
            json_dumps_params={"ensure_ascii": False},
        )
