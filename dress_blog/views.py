#-*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import Http404
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import View, ListView, DateDetailView, RedirectView
from django.views.generic.dates import _date_from_string, _date_lookup_for_field

from tagging.models import Tag, TaggedItem

from dress_blog.models import Config, Post, Diary, DiaryDetail

page_size = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10)

def index(request):
    return render("dress_blog/index_4col.html", context_instance=RequestContext(request))


class PostDetailView(DateDetailView):
    def get_object(self, *args, **kwargs):
        qs = super(DateDetailView, self).get_object(*args, **kwargs)
        qs.visits = F('visits') + 1
        qs.save()
        return qs


class PostListView(ListView):
    """
    Paginated timeline

    Template: ``dress_blog/post_list.html``
    Context:
        object_list
            List of posts.
    """
    model = Post
    template_name = "dress_blog/post_list.html"

    def get_paginate_by(self, queryset):
        return Config.get_current().stories_in_index

    def get_queryset(self):
        posts = Post.objects.for_app_models(
            "dress_blog.story", "dress_blog.quote").order_by("-pub_date")
        return posts


class TagDetailView(ListView):
    """
    Paginated tag list

    Template: ``dress_blog/tag_detail.html``
    Context:
        object_list
            List of tags.
    """
    model = Tag
    slug_field = "name"
    template_name = "dress_blog/tag_detail.html"

    def get_paginate_by(self, queryset):
        return page_size

    def get_queryset(self):
        return TaggedItem.objects.filter(
            tag__name__iexact=self.kwargs.get("slug", "")).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)
        try:
            context["object"] = Tag.objects.get(name=self.kwargs.get("slug", ""))
        except Tag.DoesNotExist:
            raise Http404(_("Tag '%s' does not exist" % self.kwargs.get("slug", "")))
        return context


class DiaryDetailView(DateDetailView):
    """
    Paginated tag list

    Template: ``dress_blog/diary_detail.html``
    Context:
        object_list
            List of tags.
    """
    model = Diary

    def get_allow_empty(self):
        return False

    def get_object(self, queryset=None):
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        self.date = _date_from_string(year, self.get_year_format(),
                                      month, self.get_month_format(),
                                      day, self.get_day_format())
        
        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()

        if not self.get_allow_future() and self.date > datetime.date.today():
            raise Http404(_(u"Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
            })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        date_field = self.get_date_field()
        field = qs.model._meta.get_field(date_field)
        lookup = _date_lookup_for_field(field, self.date)
        qs = qs.filter(**lookup)
        for diarydetail in qs:
            for entry in diarydetail.detail.published():
                entry.visits = F('visits') + 1
                entry.save()
        return qs.get()

    def get_context_data(self, **kwargs):
        context = super(DiaryDetailView, self).get_context_data(**kwargs)
        context.update({
            'day': self.date,
            'previous_day': self.get_previous_day(self.date),
            'next_day': self.get_next_day(self.date),
        })
        return context
    

class DiaryRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        diary_entries = Diary.objects.published().order_by("-pub_date")
        if len(diary_entries) == 0:
            return reverse("blog-index")
        else:
            return diary_entries[0].get_absolute_url()
            
