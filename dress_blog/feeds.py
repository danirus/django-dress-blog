from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from constance import config
from django_comments.models import Comment
from inline_media.parser import inlines
from taggit.models import Tag

from dress_blog.models import Post, Story, Quote, DiaryDetail


class BasePostsFeed(Feed):
    def item_pubdate(self, item):
        return item.pub_date

    def item_title(self, item):
        child = getattr(item, item.content_type.model)
        if item.content_type.model in ["story", "quote"]:
            return child.title
        else:
            return u"%s" % child

    def item_link(self, item):
        child = getattr(item, item.content_type.model)
        return child.get_absolute_url()

    def item_description(self, item):
        child = getattr(item, item.content_type.model)
        if hasattr(child, "abstract"):
            return inlines(child.abstract_markup)
        return inlines(child.body_markup)

    def item_author_name(self, item):
        child = getattr(item, item.content_type.model)
        if hasattr(child, "quote_author"):
            return child.quote_author
        return child.author.get_full_name()       


class LatestPostsFeed(BasePostsFeed):
    def title(self):
        return '%s posts feed' % config.title

    def description(self):
        return '%s latest posts feed' % config.title

    def link(self):
        return reverse('blog-index')

    def items(self):
        return Post.objects.published()[:10]


class LatestStoriesFeed(BasePostsFeed):
    def title(self):
        return '%s stories feed' % config.title

    def description(self):
        return '%s latest stories feed.' % config.title

    def link(self):
        return reverse('blog-story-list')

    def items(self):
        return Story.objects.published()[:10]


class LatestStoriesTaggedAsFeed(BasePostsFeed):
    def get_object(self, request, slug):
        if not slug:
            raise ObjectDoesNotExist
        return Tag.objects.get(name__iexact=slug)

    def title(self, obj):
        return ("%s stories tagged as '%s' feed" % (config.title, obj.name))

    def description(self, obj):
        return ("%s latest stories tagged as '%s' feed." %
                (config.title, obj.name))

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('blog-tagged-story-list', None, {'slug': obj.name})

    def feed_url(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('latest-stories-tagged-as-feed', 
                       None, {"slug": obj.name})

    def items(self, obj):
        qs = Story.objects.filter(tags__name__in=obj.name, status=3)\
                          .order_by("-id")[:10]
        return qs

    def item_pubdate(self, item):
        return item.pub_date

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        if item.abstract:
            return inlines(item.abstract_markup)
        return inlines(item.body_markup)

    def item_author_name(self, item):
        return item.author.get_full_name()


class LatestQuotesFeed(BasePostsFeed):
    def title(self):
        return '%s quotes feed' % config.title

    def description(self):
        return '%s latest quotes feed.' % config.title

    def link(self):
        return reverse('blog-quote-list')

    def items(self):
        return Quote.objects.published()[:10]


class LatestDiaryDetailsFeed(BasePostsFeed):    
    def title(self):
        return '%s diary feed' % config.title
    
    def description(self):
        return '%s latest diary feed.' % config.title

    def link(self):
        return reverse('blog-diary')

    def items(self):
        return DiaryDetail.objects.published()[:10]


class PostsByTag(Feed):
    def get_object(self, request, slug):
        if not slug:
            raise ObjectDoesNotExist
        return Tag.objects.get(name__iexact=slug)

    def title(self, obj):
        return ("%s posts tagged as '%s' feed" % (config.title, obj.name))

    def description(self, obj):
        return ("%s latest posts tagged as '%s' feed." % 
                (config.title, obj.name))

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('blog-tag-detail', None, {"slug": obj.name})

    def feed_url(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('posts-tagged-as', None, {"slug": obj.name})

    def items(self, obj):
        ct_story = ContentType.objects.get(app_label="dress_blog",
                                           model="story")
        ct_quote = ContentType.objects.get(app_label="dress_blog",
                                           model="quote")
        return Tag.objects.filter(
            name__iexact=obj.name,
            content_type__in=[ct_story, ct_quote]).order_by("-id")[:10]

    def item_pubdate(self, item):
        return item.object.pub_date

    def item_title(self, item):
        if item.content_type.model in ["story", "quote"]:
            return item.object.title
        else:
            return u"%s" % item.object

    def item_link(self, item):
        return item.object.get_absolute_url()

    def item_description(self, item):
        if item.content_type.model == "story":
            if item.object.abstract:
                return inlines(item.object.abstract_markup)
        return inlines(item.object.body_markup)

    def item_author_name(self, item):
        if item.content_type.model == "quote":
            return item.object.quote_author
        return item.object.author.get_full_name()       
