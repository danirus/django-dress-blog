from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[0:2] < (1, 3):
    from django.conf.urls.defaults import patterns, url
else:
    from django.conf.urls import patterns, url

from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic

from dress_blog.conf import settings
from dress_blog.models import Story
from dress_blog.views import (PostDetailView, PostListView, 
                              PostYearArchiveView,
                              StoriesTaggedListView,
                              PostMonthArchiveView, 
                              PostDayArchiveView)


urlpatterns = patterns('',

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Story, date_field="pub_date", month_format="%m", 
            template_name="blog/story_detail.html"),
        name='blog-story-detail-month-numeric'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Story, date_field="pub_date", month_format="%b", 
            template_name="blog/story_detail.html"),
        name='blog-story-detail'),

    # allowing access to a story in draft mode
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/draft/$',
        login_required(
            generic.DateDetailView.as_view(
                queryset=Story.objects.drafts(),
                date_field="pub_date", month_format="%b", 
                template_name="blog/story_detail.html", allow_future=True),
            redirect_field_name=""),
        name='blog-story-detail-draft'),

    # allowing access to a story in review mode
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/review/$',
        login_required(
            permission_required('dress_blog.can_review_posts')(
                generic.DateDetailView.as_view(
                    model=Story, date_field="pub_date", month_format="%b", 
                    template_name="blog/story_detail.html", allow_future=True)
                ),
            redirect_field_name=""),
        name='blog-story-detail-review'),

    # allowing access to an upcoming storie
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/upcoming/$',
        login_required(
            generic.DateDetailView.as_view(
                queryset=Story.objects.upcoming(),
                date_field="pub_date", month_format="%b", 
                template_name="blog/story_detail.html", allow_future=True),
            redirect_field_name=""),
        name='blog-story-detail-upcoming'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        PostDayArchiveView.as_view(
            model=Story, paginate_by=settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-story-archive-day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        PostMonthArchiveView.as_view(
            model=Story, paginate_by=settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-story-archive-month'),

    url(r'^(?P<year>\d{4})/$',
        PostYearArchiveView.as_view(
            model=Story, paginate_by=2*settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-story-archive-year'),

    url(r'^tagged-as/(?P<slug>.{1,50})$', StoriesTaggedListView.as_view(),
        name='blog-tagged-story-list'),

    url(r'^$', PostListView.as_view(
            model=Story, paginate_by=settings.DRESS_BLOG_PAGINATE_BY,
            template_name="dress_blog/story_list.html"), 
        name='blog-story-list'),
)
