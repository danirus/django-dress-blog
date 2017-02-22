from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic

from dress_blog.conf import settings
from dress_blog.models import Quote
from dress_blog.views import (PostDetailView, PostListView, PostYearArchiveView,
                              PostMonthArchiveView, PostDayArchiveView)


urlpatterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
        r'(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Quote, date_field="pub_date", month_format="%m", 
            template_name="blog/quote_detail.html"
        ),
        name='blog-quote-detail-month-numeric'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        PostDetailView.as_view(
            model=Quote, date_field="pub_date", month_format="%b", 
            template_name="blog/quote_detail.html"),
        name='blog-quote-detail'),

    # allowing access to a quote in draft mode
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/'
        r'(?P<slug>[-\w]+)/draft/$',
        login_required(
            generic.DateDetailView.as_view(
                queryset=Quote.objects.drafts(),
                date_field="pub_date", month_format="%b", 
                template_name="blog/quote_detail.html",
                allow_future=True),
            redirect_field_name=""),
        name='blog-quote-detail-draft'),

    # allowing access to a quote in review status
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/'
        r'(?P<slug>[-\w]+)/review/$',
        login_required(
            permission_required('dress_blog.can_review_posts')(
                generic.DateDetailView.as_view(
                    model=Quote, date_field="pub_date", month_format="%b", 
                    template_name="blog/quote_detail.html", allow_future=True)),
            redirect_field_name=""),
        name='blog-quote-detail-review'),

    # allowing access to an upcoming quote
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/'
        r'(?P<slug>[-\w]+)/upcoming/$',
        login_required(
            generic.DateDetailView.as_view(
                queryset=Quote.objects.upcoming(),
                date_field="pub_date", month_format="%b", 
                template_name="blog/quote_detail.html", allow_future=True),
            redirect_field_name=""),
        name='blog-quote-detail-upcoming'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        PostDayArchiveView.as_view(
            model=Quote, paginate_by=settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-quote-archive-day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        PostMonthArchiveView.as_view(
            model=Quote, paginate_by=settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-quote-archive-month'),

    url(r'^(?P<year>\d{4})/$',
        PostYearArchiveView.as_view(
            model=Quote, paginate_by=2*settings.DRESS_BLOG_PAGINATE_BY),
        name='blog-quote-archive-year'),

    url(r'^$', 
        PostListView.as_view(
            model=Quote, paginate_by=settings.DRESS_BLOG_PAGINATE_BY,
            template_name="dress_blog/quote_list.html"),
        name='blog-quote-list')
]
