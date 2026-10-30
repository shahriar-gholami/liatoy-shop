from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum

from .models import Owner, Payment, Month, Withdraw


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("title", "paid_by", "amount", "pay_date", "paid_back")
    list_filter = ("paid_back", "paid_by")


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ("owner", "month", "get_total_amount", "paid_date")
    filter_horizontal = ("payments",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.payments.update(paid_back=True)


from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum

@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "month_orders_count",
        "month_orders_amount",
        "month_items_cost",
        "month_gross_profit",
        "month_gross_profit_percentage",
        "month_side_costs",
        "month_net_profit",
    )
    readonly_fields = (
        "month_orders_count",
        "month_orders_amount",
        "month_items_cost",
        "month_gross_profit",
        "month_gross_profit_percentage",
        "month_side_costs",
        "month_net_profit",
        "monthly_products_report", # <--- فیلد جدید اضافه شد
        "monthly_payments_report",
        "monthly_withdraw_report",
    )

    def month_orders_count(self, obj):
        return obj.get_orders().count()
    month_orders_count.short_description = "تعداد سفارشات ماه"

    def month_orders_amount(self, obj):
        return f"{obj.get_total_earnings():,d} تومان"
    month_orders_amount.short_description = "مبلغ سفارشات ماه"

    def month_items_cost(self, obj):
        return f"{obj.get_total_items_cost():,d} تومان"
    month_items_cost.short_description = "مبلغ تامین کالاها"

    def month_side_costs(self, obj):
            return f"{obj.get_total_other_payments():,d} تومان"
    month_side_costs.short_description = "هزینه‌های جانبی ماه"

    def month_gross_profit(self, obj):
        return f"{obj.get_gross_profit():,d} تومان"
    month_gross_profit.short_description = "سود/زیان ناخالص"

    def month_gross_profit_percentage(self, obj):
        return f"{obj.get_monthly_profit_percentage():.2f}%"
    month_gross_profit_percentage.short_description = "درصد سود روی کالا"

    def month_net_profit(self, obj):
        return f"{obj.get_net_profit():,d} تومان"
    month_net_profit.short_description = "سود/زیان خالص"

    def monthly_products_report(self, obj):
        orders = obj.get_orders().prefetch_related('items__variety__product')
        if not orders.exists():
            return "در این ماه سفارشی ثبت نشده است."

        product_stats = {}

        for order in orders:
            for item in order.items.all():
                variety = item.variety
                if not variety:
                    continue
                
                product = variety.product
                quantity = item.quantity or 1

                # هزینه تامین ثبت‌شده روی آیتم سفارش
                unit_cost = item.cost or 0
                total_cost = unit_cost * quantity
                
                # 💡 قیمت فروش ثبت‌شده در زمان تکمیل سفارش (sell_price)
                if item.sell_price is not None and item.sell_price > 0:
                    unit_sell_price = item.sell_price
                else:
                    # پشتیبانی از سفارش‌های قدیمی که هنوز sell_price نداشتند
                    try:
                        price_str = str(item.get_single_item_price()).replace(',', '')
                        unit_sell_price = int(price_str) if price_str.isdigit() else 0
                    except Exception:
                        unit_sell_price = 0

                total_revenue = unit_sell_price * quantity

                if product.id not in product_stats:
                    product_stats[product.id] = {
                        'name': product.name,
                        'quantity': 0,
                        'total_cost': 0,
                        'total_revenue': 0,
                    }

                product_stats[product.id]['quantity'] += quantity
                product_stats[product.id]['total_cost'] += total_cost
                product_stats[product.id]['total_revenue'] += total_revenue

        if not product_stats:
            return "آیتمی در سفارشات یافت نشد."

        html = '<table style="width:100%; border-collapse:collapse; text-align:right;" border="1" cellpadding="8">'
        html += '<tr style="background-color:#f8f9fa;">'
        html += '<th>نام محصول</th>'
        html += '<th>تعداد فروش</th>'
        html += '<th>هزینه تامین کل</th>'
        html += '<th>فروش کل محصول</th>'
        html += '<th>درصد سود (حاشیه سود)</th>'
        html += '</tr>'

        sorted_stats = sorted(product_stats.values(), key=lambda x: x['quantity'], reverse=True)

        for stats in sorted_stats:
            cost = stats['total_cost']
            revenue = stats['total_revenue']
            profit = revenue - cost
            
            if cost > 0:
                profit_percent = (profit / cost) * 100
                profit_display = f"{profit_percent:.2f}%"
                color = "green" if profit_percent > 0 else "red"
            else:
                profit_display = "۱۰۰٪ (بدون هزینه)"
                color = "green"

            html += (
                f"<tr>"
                f"<td>{stats['name']}</td>"
                f"<td>{stats['quantity']} عدد</td>"
                f"<td>{cost:,d} تومان</td>"
                f"<td>{revenue:,d} تومان</td>"
                f"<td dir='ltr' style='text-align:right; color:{color}; font-weight:bold;'>{profit_display}</td>"
                f"</tr>"
            )

        html += "</table>"
        return format_html(html)

    monthly_products_report.short_description = "گزارش تفکیکی فروش کالاها"


    
    def monthly_payments_report(self, obj):
        # ... (کدهای قبلی شما)
        payments = obj.get_payments()
        if not payments.exists():
            return "هزینه‌ای ثبت نشده است."

        summary = payments.values("paid_by__name", "paid_by__id").annotate(total=Sum("amount"))

        html = '<table style="width:100%; border-collapse:collapse;" border="1" cellpadding="5">'
        html += '<tr style="background-color:#f8f9fa;"><th>مدیر</th><th>مبلغ</th><th>لینک</th></tr>'

        for item in summary:
            url = reverse(
                f'admin:{Payment._meta.app_label}_{Payment._meta.model_name}_changelist'
            ) + f"?paid_by__id__exact={item['paid_by__id']}"

            html += (
                f"<tr>"
                f"<td>{item['paid_by__name']}</td>"
                f"<td>{item['total']:,d} تومان</td>"
                f'<td><a href="{url}">مشاهده</a></td>'
                f"</tr>"
            )

        html += "</table>"
        return format_html(html)
    monthly_payments_report.short_description = "لیست هزینه‌ها به تفکیک فرد"

    def monthly_withdraw_report(self, obj):
        # ... (کدهای قبلی شما)
        withdraws = obj.get_withdraw_list()
        if not withdraws.exists():
            return "تصفیه‌ای ثبت نشده است."

        html = '<table style="width:100%; border-collapse:collapse;" border="1" cellpadding="5">'
        html += '<tr style="background-color:#f8f9fa;"><th>مدیر</th><th>مبلغ</th><th>لینک</th></tr>'

        for w in withdraws:
            url = reverse(
                f'admin:{Withdraw._meta.app_label}_{Withdraw._meta.model_name}_change',
                args=[w.id]
            )
            html += (
                f"<tr>"
                f"<td>{w.owner.name}</td>"
                f"<td>{w.get_total_amount():,d} تومان</td>"
                f'<td><a href="{url}">مشاهده</a></td>'
                f"</tr>"
            )

        html += "</table>"
        return format_html(html)
    monthly_withdraw_report.short_description = "لیست تصفیه‌حساب‌ها به تفکیک فرد"
