#-*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.apps import apps
from django.utils.timezone import now

import re

Quote = apps.get_model('dress_blog', 'quote')
Story = apps.get_model('dress_blog', 'story')
Diary = apps.get_model('dress_blog', 'diary')
DiaryDetail = apps.get_model('dress_blog', 'diarydetail')
BlogRoll = apps.get_model('dress_blog', 'blogroll')

register = template.Library()

class DressBlogBaseTemplateNode(template.Node):
    def __init__(self, limit, var_name):
        try:
            self.limit = int(limit)
        except:
            self.limit = template.Variable(limit)
        self.var_name = var_name
        
    def get_queryset(self, context):
        return None
    
    def render(self, context):
        if not isinstance(self.limit, int):
            self.limit = int( self.limit.resolve(context) )

        queryset = self.get_queryset(context)
        if queryset:
            context[self.var_name] = queryset
        return ''

def dress_blog_base_tag(parser, token):
    """Generic tag: {% tag_name [limit] as [var_name] %}"""
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" %
                                           token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" %
                                           tag_name)
    format_string, var_name = m.groups()
    return (format_string, var_name)

#------------------------------------------------------------------------
class LatestStories(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        if context["request"].session.get("unpublished_on", False):
            qs = Story.objects.filter(status__in=[1,2,3]).exclude(
                ~models.Q(author=context["request"].user), status=1)
            if not context["request"].user.has_perm("dress_blog.can_review_posts"):
                qs = qs.exclude(~Q(author=context["request"].user), status=2)
        else:
            qs = Story.objects.filter(status=3, pub_date__lte=now())
        return qs[:self.limit]

@register.tag
def get_latest_stories(parser, token):
    return LatestStories(*dress_blog_base_tag(parser, token))

#----------
class DraftStories(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        user = template.Variable("user").resolve(context)            
        return Story.objects.drafts(user)[:self.limit]

@register.tag
def get_draft_stories(parser, token):
    return DraftStories(*dress_blog_base_tag(parser, token))

#----------
class ReviewStories(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        user = template.Variable("user").resolve(context)            
        return Story.objects.reviews(user)[:self.limit]

@register.tag
def get_review_stories(parser, token):
    return ReviewStories(*dress_blog_base_tag(parser, token))

#----------
class LatestQuotes(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        if context["request"].session.get("unpublished_on", False):
            qs = Quote.objects.filter(status__in=[1,2,3]).exclude(
                ~models.Q(author=context["request"].user), status=1)
            if not context["request"].user.has_perm("dress_blog.can_review_posts"):
                qs = qs.exclude(~Q(author=context["request"].user), status=2)
        else:
            qs = Quote.objects.filter(status=3, pub_date__lte=now())
        return qs[:self.limit]

@register.tag
def get_latest_quotes(parser, token):
    return LatestQuotes(*dress_blog_base_tag(parser, token))

#----------
class DraftQuotes(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        user = template.Variable("user").resolve(context)            
        return Quote.objects.drafts(user)[:self.limit]

@register.tag
def get_draft_quotes(parser, token):
    return DraftQuotes(*dress_blog_base_tag(parser, token))

#----------
class ReviewQuotes(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        user = template.Variable("user").resolve(context)            
        return Quote.objects.reviews(user)[:self.limit]

@register.tag
def get_review_quotes(parser, token):
    return ReviewQuotes(*dress_blog_base_tag(parser, token))

#----------
class LatestDiaryDays(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        if context["request"].session.get("unpublished_on", False):
            qs = Diary.objects.all().order_by("-pub_date").filter(
                detail__isnull=False, detail__status__in=[1,2,3]).distinct()
        else:
            qs = Diary.objects.published().order_by("-pub_date").filter(
                detail__isnull=False, detail__status__gt=2).distinct()
        return qs[:self.limit]

@register.tag
def get_latest_diary_days(parser, token):
    return LatestDiaryDays(*dress_blog_base_tag(parser, token))

#----------
class LatestDiaryEntries(DressBlogBaseTemplateNode):
    def get_queryset(self, context):
        return DiaryDetail.objects.published().order_by("-pub_date")[:self.limit]

@register.tag
def get_latest_diary_entries(parser, token):
    return LatestDiaryEntries(*dress_blog_base_tag(parser, token))


#------------------------------------------------------------------------
class DetailForDay(template.Node):
    def __init__(self, diary_object, var_name):
        self.diary_object = template.Variable(diary_object)
        self.var_name = var_name

    def render(self, context):
        diary_object = self.diary_object.resolve(context)

        if context["request"].session.get("unpublished_on", False):
            qs = diary_object.detail.filter(status__in=[1,2,3]).exclude(
                ~models.Q(author=context["request"].user), status=1)
        else:
            qs = diary_object.detail.filter(status=3, pub_date__lte=now())

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
        raise template.TemplateSyntaxError("%s tag requires arguments" %
                                           token.contents.split()[0])
    m = re.search(r'(\w+) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" %
                                           tag_name)
    diary_object, var_name = m.groups()
    return DetailForDay(diary_object, var_name)
