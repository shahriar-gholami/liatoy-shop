
from django import forms
from django.utils import timezone
from django.forms import modelformset_factory
from .models import *
from ckeditor.widgets import CKEditorWidget
from django.core import validators



class AuthenticationCodeForm(forms.Form):
    code = forms.IntegerField()

class OwnerLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=11)

class StoreForm(forms.Form):
    country = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    city = forms.CharField(required=False)
    instagram = forms.CharField(required=False)
    address = forms.CharField(required=False)
    about = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)

class IndexTitleUpdateForm(forms.Form):
    index_title = forms.CharField(required=False)

class SearchForm(forms.Form):
    search = forms.CharField()

class EnamadUpdateForm(forms.Form):
    enamad = forms.CharField(required=False)

class DeliveryForm(forms.Form):
    name =forms.CharField(max_length=250, required=False)
    price = forms.IntegerField()

class TagForm(forms.Form):
    name =forms.CharField(max_length=250, required=False)
    slug = forms.CharField(max_length=250, required=False)
    is_special = forms.BooleanField(required=False)

class CategoryForm(forms.Form):
    name = forms.CharField(max_length=250)
    is_sub = forms.BooleanField(required=False)
    parent = forms.CharField()
   
class CommentForm(forms.Form):
    email = forms.EmailField()
    body = forms.CharField()
     
class FilterProductsForm(forms.Form):
    category = forms.CharField(required=False)
    price_range = forms.CharField(required=False)
    brand = forms.CharField(required=False)

class CartEditForm(forms.Form):
    count = forms.IntegerField()

class PurchaseForm(forms.Form):
    size = forms.CharField(required=False)
    count = forms.IntegerField()

class RequestNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=11, validators=[validators.RegexValidator(r'^\d{11}$', 'شماره تلفن باید 11 رقمی و بدون حروف باشد.')])

class CouponApplyForm(forms.Form):
	code = forms.CharField()

class DeliveryApplyForm(forms.Form):
	delivery = forms.CharField()

class CouponForm(forms.Form):
    code = forms.CharField()
    discount = forms.IntegerField()
    from_time = forms.CharField()
    to_time = forms.CharField()

class ContactUsForm(forms.Form):
    name = forms.CharField()
    familly_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    subject = forms.CharField()
    message_text = forms.CharField(widget=CKEditorWidget())

class CustomerForm(forms.Form):
      full_name = forms.CharField()
      email = forms.EmailField()
      city = forms.CharField()
      zip_code = forms.CharField()
      address = forms.CharField()

class SubscriptionForm(forms.Form):
    email = forms.EmailField()

class CheckoutForm(forms.Form):
    name = forms.CharField(required = False)
    familly_name = forms.CharField(required = False)
    phone_number = forms.CharField(required = False)
    email = forms.EmailField(required = False)
    state = forms.CharField(required = False)
    city = forms.CharField(required = False)
    zip_code = forms.CharField(required = False)
    address = forms.CharField(required = False)

class FeatureFilterForm(forms.Form):
    def __init__(self, choices):
        self.choices = choices
        self.options = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
    
class AddingProductFromDigiForm(forms.Form):
    dkp_code = forms.CharField()
    category = forms.CharField()

class CategorySelectForm(forms.Form):
    category_select = forms.CharField()

class MerchantCodeForm(forms.Form):
    merchant_code = forms.CharField()

class RecieverDetailsForm(forms.Form):
    name = forms.CharField(required = False)
    familly_name = forms.CharField(required = False)
    phone_number = forms.CharField(required = False)
    email = forms.EmailField(required = False)
    state = forms.CharField(required = False)
    city = forms.CharField(required = False)
    zip_code = forms.CharField(required = False)
    address = forms.CharField(required = False)

class OrderDeliveryOptionsForm(forms.Form):
    delivery_method = forms.CharField()






    