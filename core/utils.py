import requests
import json
from shop.models import Store, CashBack, Customer, Coupon
import random 
import jdatetime


def send_otp_code(phone_number, code):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "2frcg7j9tgi8mdb",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "verification-code": code,
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def order_verification(phone_number, order_id):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "ehuynsayt2ku2mh",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "order-id": order_id
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def delivery_inform(phone_number, order_id):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "7ga4cq43fxkpk3w",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "order-id": order_id
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def cashback_inform(phone_number, order_id, discount, code):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "296bmw92irlcjzy",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "order-id": order_id,
        "discount": discount,
        "code": code
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def erase_stock_volume(product):
    product_varieties = product.get_varieties()
    for variety in product_varieties:
        variety.stock = 0
        variety.save()  

def update_slugs(modeladmin, request, queryset):
    for product in queryset:
        product.slug = product.name.replace(' ', '-')
        product.save()
    # نمایش پیام تایید برای کاربر
    modeladmin.message_user(request, "Slugs updated successfully!")

def send_order_verification_sms(modeladmin, request, queryset):
    for order in queryset:
        phone_number = order.customer.phone_number
        order_id = order.id
        order_verification(phone_number, order_id)
    modeladmin.message_user(request, "پیامک تایید سفارش برای سفارشات انتخابی ارسال شد.")
send_order_verification_sms.short_description = "ارسال پیامک تأیید سفارش"

def send_delivery_inform_sms(modeladmin, request, queryset):
    cashbacks = CashBack.objects.filter(is_active=True)
    print(cashbacks)
    for order in queryset:
        cashback = None
        discount = 0
        phone_number = order.customer.phone_number
        order_id = order.id
        if cashbacks:
            cashback = CashBack.objects.filter(order_level=order.customer.orders_num).first()
            if cashback != None:
                discount = (int(order.get_total_price().replace(',',''))*cashback.percent)/100
            elif CashBack.objects.filter(order_level=0).first() != None:
                cashback = CashBack.objects.filter(order_level=0).first()
                discount = (int(order.get_total_price().replace(',',''))*cashback.percent)/100
            if discount != 0:
                discount = int((discount // 1000) * 1000)
                start = jdatetime.date.today()
                end = start.replace(year=start.year + 10)
                new_coupon = Coupon.objects.create(
                    title = 'کش‌بک',
                    code = random.randint(100000,999999),
                    start_date = start,
                    end_date = end,
                    discount = discount,
                    min_cart_volume = discount,
                    is_cashback = True
                ) 
                code = new_coupon.code
                print(phone_number, discount, code)
                cashback_inform(phone_number, order_id, discount, code)
        else:
            delivery_inform(phone_number, order_id)
    modeladmin.message_user(request, "پیامک ارسال سفارش برای سفارشات انتخابی ارسال شد.")
send_delivery_inform_sms.short_description = "ارسال پیامک اطلاع‌رسانی ارسال و پاداش‌"











