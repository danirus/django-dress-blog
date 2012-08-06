from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views import generic

from dress_blog.models import Quote
from dress_blog.views import PostDetailView


page_size       = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10)
large_page_size = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 10) * 2

urlpatterns = patterns('',

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Quote, date_field="pub_date", month_format="%m", 
            template_name="blog/quote_detail.html"),
        name='blog-quote-detail-month-numeric'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Quote, date_field="pub_date", month_format="%b", 
            template_name="blog/quote_detail.html"),
        name='blog-quote-detail'),

    # allow viewing upcoming stories
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/draft/$',
        login_required(
            generic.DateDetailView.as_view(
                model=Quote, date_field="pub_date", month_format="%b", 
                template_name="blog/quote_detail.html", allow_future=True)),
        name='blog-quote-detail-draft'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        generic.DayArchiveView.as_view(model=Quote, 
                                       date_field="pub_date", 
                                       month_format="%m",
                                       paginate_by=page_size),
        name='blog-quote-archive-day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        generic.MonthArchiveView.as_view(model=Quote, 
                                         date_field="pub_date", 
                                         month_format="%m",
                                         paginate_by=page_size),
        name='blog-quote-archive-month'),

    url(r'^(?P<year>\d{4})/$',
        generic.YearArchiveView.as_view(model=Quote, date_field="pub_date", 
                                        make_object_list=True,
                                        paginate_by=large_page_size),
        name='blog-quote-archive-year'),

    url(r'^$', 
        generic.ListView.as_view(
            queryset=Quote.objects.published(),
            template_name="dress_blog/quote_list.html",
            paginate_by=page_size),
        name='blog-quote-list'),
)
