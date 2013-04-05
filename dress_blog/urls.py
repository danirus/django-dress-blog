#-*- coding: utf-8 -*-

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[0:2] < (1, 3):
    from django.conf.urls.defaults import include, patterns, url
else:
    from django.conf.urls import include, patterns, url

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.comments.feeds import LatestCommentFeed
from django.views.generic import DetailView, ListView, TemplateView

from tagging.models import Tag
from django_comments_xtd.models import XtdComment

from dress_blog import views
from dress_blog.models import BlogRoll
from dress_blog.feeds import (LatestPostsFeed, LatestStoriesFeed, 
                              LatestQuotesFeed, LatestDiaryDetailsFeed, PostsByTag)
from dress_blog.sitemaps import PostsSitemap


page_size = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10)
ui_columns = getattr(settings, "DRESS_BLOG_UI_COLUMNS", 3)
search_url_active = getattr(settings, "DRESS_BLOG_SEARCH_URL_ACTIVE", True)

urlpatterns = patterns("",
    url(r"^stories/", include("dress_blog.story_urls")),
    url(r"^diary/",   include("dress_blog.diary_urls")),
    url(r"^quotes/",  include("dress_blog.quote_urls")),

    url(r"^blogroll$",
        ListView.as_view(
            model=BlogRoll, 
            queryset=BlogRoll.objects.all().order_by('sort_order'),
            template_name="dress_blog/blogroll.html", 
            paginate_by=2*page_size),
        name="blog-blogroll"),

    url(r"^tags$",
        TemplateView.as_view(template_name="dress_blog/tag_list.html"),
        name="blog-tag-list"),

    url(r"^tags/(?P<slug>.{1,50})$",
        views.TagDetailView.as_view(),
        name="blog-tag-detail"),

    url(r"^comments$", 
        ListView.as_view(
            queryset=XtdComment.objects.for_app_models("dress_blog.story", 
                                                       "dress_blog.quote",
                                                       "dress_blog.diarydetail"), 
            template_name="dress_blog/comment_list.html",
            paginate_by=page_size),
        name="blog-comment-list"),

    # url(r'^post/(\d+)/(.+)/$', 'django.contrib.contenttypes.views.shortcut', name='post-url-redirect'),

    url(r'^feeds/posts/$', LatestPostsFeed(), name='latest-posts-feed'),
    url(r'^feeds/stories/$', LatestStoriesFeed(), name='latest-stories-feed'),
    url(r'^feeds/quotes/$', LatestQuotesFeed(), name='latest-quotes-feed'),
    url(r'^feeds/diary/$', LatestDiaryDetailsFeed(), name='latest-diary-feed'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),
    url(r"^feeds/tag/(?P<slug>.{1,50})$", PostsByTag(), name='posts-tagged-as'),

    url(r"^unpublished-on/$", views.show_unpublished, name="blog-unpublished-on"),
    url(r"^unpublished-off/$", views.hide_unpublished, name="blog-unpublished-off"),
)

#-- sitemaps ------------------------------------------------------------------
# if django-dress-blog is hooked at '/', activate the following code, otherwise
# add the PostsSitemap class to your '/' URLConf
# sitemaps = {
#     'posts': PostsSitemap,
# }

# urlpatterns += patterns("django.contrib.sitemaps.views",
#     url(r'^sitemap\.xml$',                 'index',   {'sitemaps': sitemaps}),
#     url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
# )
#------------------------------------------------------------------------------

#-- search --------------------------------------------------------------------
# set DRESS_BLOG_SEARCH_URL_ACTIVE=False to avoid this hook

if search_url_active:
    from haystack.forms import SearchForm
    from haystack.views import SearchView, search_view_factory

    urlpatterns += patterns("",
        url(r'^search$', 
            search_view_factory(view_class=SearchView, 
                                form_class=SearchForm,
                                results_per_page=page_size), 
            name='haystack-search'),
    )
#------------------------------------------------------------------------------

if ui_columns == 4:
    urlpatterns += patterns("",
        url(r"^$", views.index,                  name="blog-index"),
    )
else:
    urlpatterns += patterns("",
        url(r"^$", views.MixedPostListView.as_view(), name="blog-index"),
    )
