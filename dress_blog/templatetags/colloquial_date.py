#-*- coding: utf-8 -*-

from django import template
from django.conf import settings

from dress_blog.utils import colloquial_date


register = template.Library()


@register.filter("colloquial_date", is_safe=False)
def colloquial_date_filter(value, arg=None):
    """
    Formats a date using colloquial words when within last week. 

    value - date or datetime
    arg   - date format in python or django date format
    
    Formats a date using colloquial words when within last week. 
    Otherwise uses settings.DATE_FORMAT
    """
    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    return colloquial_date(value, arg)
