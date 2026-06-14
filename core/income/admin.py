from django.contrib import admin
from .models import Month
from django.utils.html import format_html # Import this for HTML formatting

from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch


class MonthAdmin(admin.ModelAdmin):
    list_display = ('name', 'month_num', 'year_num', 'get_profit_display')
    fields = ('name', 'month_num', 'year_num', 'financial_summary', 'orders_display', 'payments_display')
    readonly_fields = ('financial_summary', 'orders_display', 'payments_display')

    def financial_summary(self, obj):
        earnings = obj.get_total_earnings()
        expenses = obj.get_total_payments()
        profit = obj.get_net_profit()
        
        # تعیین رنگ برای سود یا ضرر
        profit_color = "#28a745" if profit >= 0 else "#dc3545"
        profit_text = "سود نهایی" if profit >= 0 else "ضرر نهایی"

        html = f"""
        <div style="display: flex; gap: 20px; background: #fdfdfd; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
            <div style="flex: 1; text-align: center;">
                <div style="color: #666; font-size: 0.9em;">جمع فروش (درآمد)</div>
                <div style="font-size: 1.4em; font-weight: bold; color: #212529;">{earnings:,} <small>تومان</small></div>
            </div>
            <div style="flex: 1; text-align: center; border-right: 1px solid #eee; border-left: 1px solid #eee;">
                <div style="color: #666; font-size: 0.9em;">جمع هزینه‌ها</div>
                <div style="font-size: 1.4em; font-weight: bold; color: #dc3545;">{expenses:,} <small>تومان</small></div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="color: #666; font-size: 0.9em;">{profit_text}</div>
                <div style="font-size: 1.4em; font-weight: bold; color: {profit_color};">{abs(profit):,} <small>تومان</small></div>
            </div>
        </div>
        """
        return format_html(html)

    financial_summary.short_description = 'خلاصه وضعیت مالی ماه'

    # نمایش سود در لیست اصلی ادمین
    def get_profit_display(self, obj):
        profit = obj.get_net_profit()
        color = "green" if profit >= 0 else "red"
        label = "سود" if profit >= 0 else "ضرر"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}: {} تومان</span>',
            color,
            label,
            f'{abs(profit):,}'
        )

    get_profit_display.short_description = 'سود/ضرر ماه'


    # ... متد orders_display قبلی شما ...
    def orders_display(self, obj):
        orders = obj.get_orders()
        if orders.exists():
            order_links = []
            total_orders = 0
            for order in orders:
                try:
                    # استخراج مبلغ عددی برای محاسبه جمع کل (اگر در متد get_final_payment موجود باشد)
                    # total_orders += order.get_final_payment()['amount'] 
                    order_url = reverse('admin:%s_%s_change' % (order._meta.app_label, order._meta.model_name), args=[order.pk])
                    order_links.append(f'<a href="{order_url}">{order.customer.full_name} - {order.get_final_payment()["formated"]} تومان - {order.shamsi_created_date}</a>')
                except NoReverseMatch:
                    order_links.append(str(order))
            return format_html('<br>'.join(order_links))
        return "سفارشی ثبت نشده"

    def payments_display(self, obj):
        # دریافت هزینه‌ها با بهینه‌سازی دیتابیس (select_related)
        payments = obj.get_payments().select_related('paid_by')
        
        if not payments.exists():
            return "هزینه‌ای یافت نشد"

        # دسته‌بندی هزینه‌ها بر اساس شخص
        owner_groups = {}
        for p in payments:
            owner_name = p.paid_by.name
            if owner_name not in owner_groups:
                owner_groups[owner_name] = {'list': [], 'total': 0}
            owner_groups[owner_name]['list'].append(p)
            owner_groups[owner_name]['total'] += p.amount

        # ساخت خروجی HTML
        html_output = []
        grand_total = 0 # جمع کل هزینه‌های ماه

        for owner_name, data in owner_groups.items():
            # تیتر برای هر شخص
            html_output.append(f'<div style="background: #f8f8f8; padding: 5px; margin-top: 10px; border-right: 5px solid #79aec8;"><b>مدیر: {owner_name}</b></div>')
            
            # لیست هزینه‌های آن شخص
            for p in data['list']:
                try:
                    p_url = reverse('admin:%s_%s_change' % (p._meta.app_label, p._meta.model_name), args=[p.pk])
                    html_output.append(
                        f' - <a href="{p_url}">{p.title}: {p.amount:,} تومان</a> <span style="color: #999; font-size: 0.8em;">({p.shamsi_payment_date})</span>'
                    )
                except NoReverseMatch:
                    html_output.append(f' - {p.title}: {p.amount:,} تومان')

            # جمع کل برای این شخص
            html_output.append(f'<div style="color: #264b5d; font-weight: bold; margin-bottom: 5px;">جمع هزینه‌های {owner_name}: {data["total"]:,} تومان</div>')
            grand_total += data['total']


        return format_html('<br>'.join(html_output))

    payments_display.short_description = 'هزینه‌ها به تفکیک شخص'

admin.site.register(Month, MonthAdmin)


# ثبت مدل Owner
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',) # اضافه کردن قابلیت جستجو بر اساس نام مدیر


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('title', 'paid_by', 'amount')
    list_filter = ('paid_by', 'pay_date') # اضافه کردن فیلتر بر اساس مدیر و تاریخ
    search_fields = ('title', 'paid_by__name') # جستجو بر اساس عنوان هزینه و نام مدیر

