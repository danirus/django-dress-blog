from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views import generic

from dress_blog.models import Story
from dress_blog.views import PostDetailView


page_size       = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10)
large_page_size = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10) * 2

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

    # allow viewing upcoming stories
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/draft/$',
        login_required(
            generic.DateDetailView.as_view(
                model=Story, date_field="pub_date", month_format="%b", 
                template_name="blog/story_detail.html", allow_future=True)),
        name='blog-story-detail-draft'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        generic.DayArchiveView.as_view(model=Story, 
                                       date_field="pub_date", 
                                       month_format="%m",
                                       paginate_by=page_size),
        name='blog-story-archive-day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        generic.MonthArchiveView.as_view(model=Story, 
                                         date_field="pub_date", 
                                         month_format="%m",
                                         paginate_by=page_size),
        name='blog-story-archive-month'),

    url(r'^(?P<year>\d{4})/$',
        generic.YearArchiveView.as_view(model=Story, date_field="pub_date",
                                        make_object_list=True,
                                        paginate_by=large_page_size),
        name='blog-story-archive-year'),

    url(r'^page/(?P<page>\w)/$', 
        generic.ListView.as_view(queryset=Story.objects.published(),
                                 template_name="dress_blog/story_list.html",
                                 paginate_by=page_size),
        name='blog-story-list-paginated'),

    url(r'^$', 
        generic.ListView.as_view(queryset=Story.objects.published(),
                                 template_name="dress_blog/story_list.html",
                                 paginate_by=page_size),
        name='blog-story-list'),
)
