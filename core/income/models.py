from django.db import models
from shop.models import Order, OrderStatus
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jdatetime
from django_jalali.db import models as jmodels
from datetime import datetime
from django.db.models import Q




def date2jalali(g_date):
    return jdatetime.date.fromgregorian(date=g_date) if g_date else None

class Owner(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'مدیران سایت'
        verbose_name_plural = 'مدیران سایت'

class Payment(models.Model):
    title = models.CharField(max_length=255, default='جشنواره فروش', verbose_name="عنوان هزینه")
    paid_by = models.ForeignKey(Owner, on_delete=models.CASCADE)
    pay_date = jmodels.jDateField(verbose_name="تاریخ", null=True, blank=True)
    amount = models.IntegerField(verbose_name="مقدار (تومان)", default=0)
    paid_back = models.BooleanField(default=False)

    @property
    def shamsi_payment_date(self):
        if self.pay_date:
            return self.pay_date.strftime('%Y/%m/%d')
        return None 

    class Meta:
        verbose_name = 'هزینه‌ها'
        verbose_name_plural = 'هزینه‌ها'

    def __str__(self):
        return f'{self.title} توسط {self.paid_by} - {self.amount} تومان'


class Month(models.Model):
    name = models.CharField(max_length=255)
    month_num = models.IntegerField(default=1)
    year_num = models.IntegerField(default=1405)

    def get_withdraw_list(self):
        return Withdraw.objects.filter(month=self)

    def get_monthly_withdraw_amount(self):
        total = sum(withdraw.get_total_amount() for withdraw in self.get_withdraw_list().all())
        return total

    def get_total_earnings(self):
        """جمع کل فروش (درآمد) ماه"""
        orders = self.get_orders()
        # فرض بر این است که متد get_final_payment یک دیکشنری برمی‌گرداند که کلید raw یا مبلغ عددی دارد
        # اگر ندارد، باید بر اساس فیلد قیمت در مدل Order جمع بزنید
        total = sum(order.get_final_payment()["unformated"] for order in orders)
        return total

    def get_total_items_cost(self):
        """جمع کل هزینه تامین کالاها ماه"""
        orders = self.get_orders()
        # فرض بر این است که متد get_final_payment یک دیکشنری برمی‌گرداند که کلید raw یا مبلغ عددی دارد
        # اگر ندارد، باید بر اساس فیلد قیمت در مدل Order جمع بزنید
        total = sum(order.items_cost for order in orders)
        return total

    def get_total_gateway_fee(self):
            """جمع کل هزینه کارمزدهای درگاه پرداخت"""
            orders = self.get_orders()
            # فرض بر این است که متد get_final_payment یک دیکشنری برمی‌گرداند که کلید raw یا مبلغ عددی دارد
            # اگر ندارد، باید بر اساس فیلد قیمت در مدل Order جمع بزنید
            total = sum(order.gateway_fee for order in orders)
            return total

    def get_monthly_profit_percentage(self):
        """
        درصد سود ماهانه نسبت به هزینه تامین:
        ((فروش - هزینه تامین) / هزینه تامین) * 100
        """
        total_earnings = self.get_total_earnings()
        total_items_cost = self.get_total_items_cost()

        if total_items_cost == 0:
            return 0

        profit = total_earnings - total_items_cost
        return (profit / total_items_cost) * 100

    def get_total_payments(self):
        """جمع کل هزینه‌های ماه"""
        payments = self.get_payments() + self.get_total_items_cost()
        return sum(p.amount for p in payments)

    def get_net_profit(self):
        """محاسبه سود یا ضرر نهایی"""
        return self.get_total_earnings() - self.get_total_payments() - self.get_monthly_withdraw_amount()

    def get_orders(self):
        
        start_jalali = jdatetime.date(self.year_num, self.month_num, 1)

        if self.month_num == 12:
            end_jalali = jdatetime.date(self.year_num + 1, 1, 1)
        else:
            end_jalali = jdatetime.date(self.year_num, self.month_num + 1, 1)

        start_gregorian = start_jalali.togregorian()
        end_gregorian = end_jalali.togregorian()

        start_datetime = timezone.make_aware(
            datetime.combine(start_gregorian, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(end_gregorian, datetime.min.time())
        )

        return Order.objects.filter(
            created_date__gte=start_datetime,
            created_date__lt=end_datetime,
            status = OrderStatus.objects.get(latest_status = 'ارسال شده')
        )
    
    def get_payments(self):
        
        start_jalali = jdatetime.date(self.year_num, self.month_num, 1)

        if self.month_num == 12:
            end_jalali = jdatetime.date(self.year_num + 1, 1, 1)
        else:
            end_jalali = jdatetime.date(self.year_num, self.month_num + 1, 1)

        start_gregorian = start_jalali.togregorian()
        end_gregorian = end_jalali.togregorian()

        start_datetime = timezone.make_aware(
            datetime.combine(start_gregorian, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(end_gregorian, datetime.min.time())
        )

        return Payment.objects.filter(
            pay_date__gte=start_datetime,
            pay_date__lt=end_datetime,
        )

    def __str__(self):
        return self.name
    
    def get_gross_profit(self):
        """سود ناخالص: فروش منهای هزینه تامین کالا"""
        return self.get_total_earnings() - self.get_total_items_cost() - self.get_total_gateway_fee()

    def get_total_other_payments(self):
        """جمع کل هزینه‌های جانبی ماه (بدون هزینه تامین کالا)"""
        return sum(p.amount for p in self.get_payments())

    def get_net_profit(self):
        """سود خالص نهایی: سود ناخالص منهای هزینه‌های جانبی"""
        # نکته: تصفیه حساب (Withdraw) هزینه جدید نیست، بلکه پرداختِ هزینه‌های قبلی است.
        # سود واقعی کسب و کار = درآمد - (هزینه کالا + هزینه‌های جانبی)
        return self.get_gross_profit() - self.get_total_other_payments()

    
    class Meta:
        verbose_name = 'حساب‌های ماهانه'
        verbose_name_plural = 'حساب‌های ماهانه'

class Withdraw(models.Model):
    # اضافه کردن limit_choices_to
    payments = models.ManyToManyField(
        Payment, 
        blank=True, 
        limit_choices_to={'paid_back': False}
    )
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    paid_date = models.DateTimeField(auto_now_add=True)

    def get_total_amount(self):
        total = sum(payment.amount for payment in self.payments.all())
        return total

    def __str__(self):
        return f"تصفیه حساب {self.owner} - {self.month}"

    class Meta:
            verbose_name = 'برداشت‌ها'
            verbose_name_plural = 'برداشت‌ها'
