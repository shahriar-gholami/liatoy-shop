from django import template
import html

register = template.Library()

@register.filter
def html_unescape(value):
    """تبدیل &zwnj; و سایر کدهای HTML به کاراکتر واقعی"""
    return html.unescape(value)
