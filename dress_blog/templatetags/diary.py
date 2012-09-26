#-*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.db import models
from django.utils.timezone import now

import re

Diary = models.get_model('dress_blog', 'diary')
DiaryDetail = models.get_model('dress_blog', 'diarydetail')

register = template.Library()


class LatestDiaryDays(template.Node):
    def __init__(self, limit, var_name):
        try:
            self.limit = int(limit)
        except:
            self.limit = template.Variable(limit)
        self.var_name = var_name

    def render(self, context):
        if not isinstance(self.limit, int):
            self.limit = int( self.limit.resolve(context) )

        entries = Diary.objects.published().order_by("-pub_date").filter(detail__isnull=False).distinct()[:self.limit]
        if entries:
            context[self.var_name] = entries
        return ''

@register.tag
def get_latest_diary_days(parser, token):
    """
    Gets any number of latest daily diary instances and stores them in a variable.

    Syntax::

        {% get_latest_diary_days [days] as [var_name] %}

    Example usage::

        {% get_latest_diary_days 2 as latest_in_diary %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return LatestDiaryDays(format_string, var_name)


class LatestDiaryEntries(template.Node):
    def __init__(self, limit, var_name):
        try:
            self.limit = int(limit)
        except:
            self.limit = template.Variable(limit)
        self.var_name = var_name

    def render(self, context):
        if not isinstance(self.limit, int):
            self.limit = int( self.limit.resolve(context) )

        entries = DiaryDetail.objects.published().order_by("-pub_date")[:self.limit]
        if entries:
            context[self.var_name] = entries
        return ''

@register.tag
def get_latest_diary_entries(parser, token):
    """
    Gets any number of latest diary entries and stores them in a variable.

    Syntax::

        {% get_latest_diary_entries [days] as [var_name] %}

    Example usage::

        {% get_latest_diary_entries 2 as latest_in_diary %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    limit, var_name = m.groups()
    return LatestDiaryEntries(limit, var_name)


class DetailForDay(template.Node):
    def __init__(self, diary_object, var_name):
        self.diary_object = template.Variable(diary_object)
        self.var_name = var_name

    def render(self, context):
        diary_object = self.diary_object.resolve(context)

        if context["request"].session.get("unpublished_on", False):
            qs = diary_object.detail.filter(status__in=[1,2]).exclude(
                ~models.Q(author=context["request"].user), status=1)
        else:
            qs = diary_object.detail.filter(status=2, pub_date__lte=now())

        entries = qs.order_by("-pub_date")
        if entries:
            context[self.var_name] = entries
        return ''

@register.tag
def get_detail_for_day(parser, token):
    """
    Gets diary detail objects for a diary object.

    Syntax::

        {% get_detail_for_day [diary_object] as [var_name] %}

    Example usage::

        {% get_detail_for_day object as detail_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(\w+) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    diary_object, var_name = m.groups()
    return DetailForDay(diary_object, var_name)
