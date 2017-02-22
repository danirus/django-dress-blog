#-*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F, Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import View, ListView, DateDetailView, RedirectView
from django.views.generic.dates import (_date_from_string, YearArchiveView, 
                                        MonthArchiveView, DayArchiveView)
from django.views.generic.list import MultipleObjectMixin

from constance import config
from taggit.models import Tag

from dress_blog.conf import settings
from dress_blog.models import Post, Story, Quote, Diary, DiaryDetail


def index(request):
    return render("dress_blog/index_4col.html", 
                  context_instance=RequestContext(request))


@login_required(redirect_field_name="")
def show_unpublished(request):
    redirect_to = request.REQUEST.get("next", '/')
    request.session["unpublished_on"] = True
    return HttpResponseRedirect(redirect_to)


@login_required(redirect_field_name="")
def hide_unpublished(request):
    redirect_to = request.REQUEST.get("next", '/')
    request.session["unpublished_on"] = False
    return HttpResponseRedirect(redirect_to)


class PostDetailView(DateDetailView):
    def get_queryset(self):
        return self.model.objects.published()

    def get_object(self, *args, **kwargs):
        qs = super(DateDetailView, self).get_object(*args, **kwargs)
        if qs.status > 2 and not qs.in_the_future:
            qs.visits = F('visits') + 1
            qs.save()
        return qs


class DressBlogViewMixin(MultipleObjectMixin):
    def get_queryset(self):
        if self.request.session.get("unpublished_on", False):
            qs = self.model.objects.filter(status__in=[1,2,3]).exclude(
                ~Q(author=self.request.user), status=1)
            if not self.request.user.has_perm("dress_blog.can_review_posts"):
                qs = qs.exclude(~Q(author=self.request.user), status=2)
        else:
            qs = self.model.objects.filter(status=3, pub_date__lte=now())
        return qs.order_by("-pub_date")


class StoriesTaggedListView(ListView, MultipleObjectMixin):
    model = Story
    
    def get_queryset(self):
        return self.model.objects\
                         .filter(tags__name__in=[self.kwargs.get("slug")],
                                 status=3)\
                         .order_by("-id")


class PostListView(ListView, DressBlogViewMixin):
    pass


class PostDayArchiveView(DayArchiveView, DressBlogViewMixin):
    date_field = "pub_date"
    make_object_list = True
    month_format = "%m"


class PostMonthArchiveView(MonthArchiveView, DressBlogViewMixin):
    date_field = "pub_date"
    make_object_list = True
    month_format = "%m"


class PostYearArchiveView(YearArchiveView, DressBlogViewMixin):
    date_field = "pub_date"
    make_object_list = True


class MixedPostListView(ListView):
    """
    Paginated timeline

    Template: ``dress_blog/post_list.html``
    Context:
        object_list
            List of posts.
    """
    template_name = "dress_blog/post_list.html"

    def get_paginate_by(self, queryset):
        return config.stories_in_index

    def get_queryset(self):
        if self.request.session.get("unpublished_on", False):
            kwargs = {"author": self.request.user, "status": [1,2,3]}
        else:
            kwargs = {"author": None, "status": [3]}
        posts = Post.objects.for_app_models("dress_blog.story", 
                                            "dress_blog.quote", 
                                            **kwargs).order_by("-pub_date")
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
        return settings.DRESS_BLOG_PAGINATE_BY

    def get_queryset(self):
        tag_name = self.kwargs.get("slug", "")
        return Tag.objects.filter(tag__name__iexact=tag_name).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)
        try:
            tag_name = self.kwargs.get("slug", "")
            context["object"] = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist as exc:
            raise Http404(_("Tag '%s' does not exist" % tag_name))
        return context


class DiaryDetailView(DateDetailView):
    model = Diary
    date_field = "pub_date"
    month_format = "%b"
    allow_future = True

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

        if not self.get_allow_future() and self.date > now().date():
            raise Http404(_(u"Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
            })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        date_field = self.get_date_field()
        field = qs.model._meta.get_field(date_field)
        lookup = self._make_single_date_lookup(field)
        qs = qs.filter(**lookup)
        for diarydetail in qs:
            for entry in diarydetail.detail.published():
                entry.visits = F('visits') + 1
                entry.save()
        return qs.get()

    def get_context_data(self, **kwargs):
        context = super(DiaryDetailView, self).get_context_data(**kwargs)
        if self.request.session.get("unpublished_on", False):
            qs = self.object.detail.filter(status__in=[1,2,3]).exclude(
                ~Q(author=self.request.user), status=1)
            if not self.request.user.has_perm("dress_blog.can_review_posts"):
                qs = qs.exclude(~Q(author=self.request.user), status=2)
        else:
            qs = self.object.detail.filter(status=3, pub_date__lte=now())
        context.update({
            'detail_list': qs.order_by("-pub_date"),
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
            
