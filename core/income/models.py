from django.db import models
from shop.models import Order, OrderStatus
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jdatetime
from django_jalali.db import models as jmodels
from datetime import datetime



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

    @property
    def shamsi_payment_date(self):
        if self.pay_date:
            return self.pay_date.strftime('%Y/%m/%d')
        return None 

    class Meta:
        verbose_name = 'هزینه‌ها'
        verbose_name_plural = 'هزینه‌ها'

class Month(models.Model):
    name = models.CharField(max_length=255)
    month_num = models.IntegerField(default=1)
    year_num = models.IntegerField(default=1405)

    def get_total_earnings(self):
        """جمع کل فروش (درآمد) ماه"""
        orders = self.get_orders()
        # فرض بر این است که متد get_final_payment یک دیکشنری برمی‌گرداند که کلید raw یا مبلغ عددی دارد
        # اگر ندارد، باید بر اساس فیلد قیمت در مدل Order جمع بزنید
        total = sum(order.get_final_payment()["unformated"] for order in orders)
        return total

    def get_total_payments(self):
        """جمع کل هزینه‌های ماه"""
        payments = self.get_payments()
        return sum(p.amount for p in payments)

    def get_net_profit(self):
        """محاسبه سود یا ضرر نهایی"""
        return self.get_total_earnings() - self.get_total_payments()

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
    
    class Meta:
        verbose_name = 'حساب‌های ماهانه'
        verbose_name_plural = 'حساب‌های ماهانه'
