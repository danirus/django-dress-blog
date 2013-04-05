from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[0:2] < (1, 3):
    from django.conf.urls.defaults import patterns, url
else:
    from django.conf.urls import patterns, url

from django.conf import settings
from django.views import generic

from dress_blog.models import Diary
from dress_blog.views import DiaryDetailView, DiaryRedirectView


page_size = getattr(settings, "DRESS_BLOG_PAGINATE_BY", 28)

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$',
        DiaryDetailView.as_view(), name='blog-diary-detail'),

    url(r'^$', DiaryRedirectView.as_view(permanent=False), name='blog-diary'),
)
