#-*- coding: utf-8 -*-

import re

from django import template
from django.contrib.contenttypes.models import ContentType

from dress_blog.models import Post, Story, Quote


register = template.Library()


class StoryArchive(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        dates = Story.objects.published().dates("pub_date", "month", 
                                                order='DESC')
        if dates:
            context[self.var_name] = dates
        return ''

@register.tag
def get_story_archive(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return StoryArchive(var_name)


class QuoteArchive(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        dates = Quote.objects.published().dates("pub_date", "month", 
                                                order='DESC')
        if dates:
            context[self.var_name] = dates
        return ''

@register.tag
def get_quote_archive(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return QuoteArchive(var_name)


def _get_content_types(tagname, tokens):
    content_types = []
    for token in tokens:
        try:
            app, model = token.split('.')
            content_types.append(
                ContentType.objects.get(app_label=app, model=model))
        except ValueError:
            raise TemplateSyntaxError(
                "Argument %s in %r must be in the format 'app.model'" % (
                    token, tagname))
        except ContentType.DoesNotExist:
            raise TemplateSyntaxError(
                "%r tag has non-existant content-type: '%s.%s'" % (
                    tagname, app, model))
    return content_types


class PopularPosts(template.Node):
    def __init__(self, count, as_varname, content_types):
        try:
            self.count = int(count)
        except:
            self.count = Variable(count)
        self.as_varname = as_varname
        self.content_types = content_types

    def render(self, context):
        posts = Post.objects.for_content_types(self.content_types).order_by('-visits')[:self.count]
        if posts and (self.count == 1):
            context[self.as_varname] = posts[0]
        else:
            context[self.as_varname] = posts
        return ''


@register.tag
def get_popular_posts(parser, token):
    """
    Gets the most popular N posts of a given list of app.model and stores them in a variable.

    Syntax::

        {% get_popular_posts [N] as [var_name] for [app].[model] [[app].[model]] %}

    Example usage::

        {% get_popular_posts 10 as popular_post_list for dress_blog.story %}
    """
    tokens = token.contents.split()

    try:
        count = int(tokens[1])
    except ValueError:
        raise TemplateSyntaxError(
            "Second argument in %r tag must be a integer" % tokens[0])

    if tokens[2] != 'as':
        raise TemplateSyntaxError(
            "Third argument in %r tag must be 'as'" % tokens[0])

    as_varname = tokens[3]

    if tokens[4] != 'for':
        raise TemplateSyntaxError(
            "Fifth argument in %r tag must be 'for'" % tokens[0])

    content_types = _get_content_types(tokens[0], tokens[5:])
    return PopularPosts(count, as_varname, content_types)

    
