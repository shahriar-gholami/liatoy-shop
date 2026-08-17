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

    def monthly_payments_report(self, obj):
        payments = obj.get_payments()
        if not payments.exists():
            return "هزینه‌ای ثبت نشده است."

        summary = payments.values("paid_by__name", "paid_by__id").annotate(total=Sum("amount"))

        html = '<table style="width:100%; border-collapse:collapse;">'
        html += '<tr><th>مدیر</th><th>مبلغ</th><th>لینک</th></tr>'

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
        withdraws = obj.get_withdraw_list()
        if not withdraws.exists():
            return "تصفیه‌ای ثبت نشده است."

        html = '<table style="width:100%; border-collapse:collapse;">'
        html += '<tr><th>مدیر</th><th>مبلغ</th><th>لینک</th></tr>'

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

