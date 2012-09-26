#-*- coding: utf-8 -*-

# based on django-basic-apps by Kevin Fricovsky
# https://github.com/montylounge/django-basic-apps
# originally basic/blog/templatetags/blog.py

from django import template
from django.conf import settings
from django.db import models

import re

Story = models.get_model('dress_blog', 'story')
BlogRoll = models.get_model('dress_blog', 'blogroll')

register = template.Library()


class LatestStories(template.Node):
    def __init__(self, limit, var_name):
        try:
            self.limit = int(limit)
        except:
            self.limit = template.Variable(limit)
        self.var_name = var_name

    def render(self, context):
        if not isinstance(self.limit, int):
            self.limit = int( self.limit.resolve(context) )
            
        stories = Story.objects.published()[:self.limit]
        if stories:
            context[self.var_name] = stories
        return ''

@register.tag
def get_latest_stories(parser, token):
    """
    Gets any number of latest stories and stores them in a variable.

    Syntax::

        {% get_latest_stories [limit] as [var_name] %}

    Example usage::

        {% get_latest_stories 10 as latest_story_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return LatestStories(format_string, var_name)


class DraftStories(template.Node):
    def __init__(self, limit, var_name):
        try:
            self.limit = int(limit)
        except:
            self.limit = template.Variable(limit)
        self.var_name = var_name

    def render(self, context):
        if not isinstance(self.limit, int):
            self.limit = int( self.limit.resolve(context) )

        user = template.Variable("user").resolve(context)
            
        stories = Story.objects.drafts(user)[:self.limit]
        if stories:
            context[self.var_name] = stories
        return ''

@register.tag
def get_draft_stories(parser, token):
    """
    Gets any number of draft stories and stores them in a variable.

    Syntax::

        {% get_draft_stories [limit] as [var_name] %}

    Example usage::

        {% get_draft_stories 10 as draft_story_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return DraftStories(format_string, var_name)


@register.filter
def get_links(value):
    """
    Extracts links from a ``Story`` body and returns a list.

    Template Syntax::
    
    {{ story.body|markdown:"safe"|get_links }}
    
    """
    try:
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(value)
        return soup.findAll('a')
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in 'get_links' filter: BeautifulSoup isn't installed."
        pass
    return value


class BlogRolls(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        blogrolls = BlogRoll.objects.all()
        context[self.var_name] = blogrolls
        return ''

@register.tag
def get_blogroll(parser, token):
    """
    Gets all blogroll links.

    Syntax::

        {% get_blogroll as [var_name] %}

    Example usage::

        {% get_blogroll as blogroll_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogRolls(var_name)
