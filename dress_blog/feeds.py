from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse

from inline_media.parser import inlines
from tagging.models import Tag, TaggedItem

from dress_blog.models import Config, Post, Story, Quote, DiaryDetail


ct_story = ContentType.objects.get(app_label="dress_blog", model="story")
ct_quote = ContentType.objects.get(app_label="dress_blog", model="quote")


class BasePostsFeed(Feed):
    _config = None
    
    @property
    def config(self):
        if self._config is None:
            self._config = Config.get_current()
        return self._config

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
        return '%s posts feed' % self.config.title

    def description(self):
        return '%s latest posts feed' % self.config.title

    def link(self):
        return reverse('blog-index')

    def items(self):
        return Post.objects.published()[:10]


class LatestStoriesFeed(BasePostsFeed):
    def title(self):
        return '%s stories feed' % self.config.title

    def description(self):
        return '%s latest stories feed.' % self.config.title

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
        return (ur'''%s stories tagged as '%s' feed''' %
                (self.config.title, obj.name))

    def description(self, obj):
        return (ur'''%s latest stories tagged as '%s' feed.''' % 
                (self.config.title, obj.name))

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
        qs = TaggedItem.objects.get_by_model(
            Story, obj.name).filter(status=3).order_by("-id")[:10]            
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
        return '%s quotes feed' % self.config.title

    def description(self):
        return '%s latest quotes feed.' % self.config.title

    def link(self):
        return reverse('blog-quote-list')

    def items(self):
        return Quote.objects.published()[:10]


class LatestDiaryDetailsFeed(BasePostsFeed):
    _site = Site.objects.get_current()
    
    def title(self):
        return '%s diary feed' % self.config.title
    
    def description(self):
        return '%s latest diary feed.' % self.config.title

    def link(self):
        return reverse('blog-diary')

    def items(self):
        return DiaryDetail.objects.published()[:10]


class PostsByTag(Feed):
    _config = None
    
    @property
    def config(self):
        if self._config is None:
            self._config = Config.get_current()
        return self._config

    def get_object(self, request, slug):
        if not slug:
            raise ObjectDoesNotExist
        return Tag.objects.get(name__iexact=slug)

    def title(self, obj):
        return (ur'''%s posts tagged as '%s' feed''' % 
                (self.config.title, obj.name))

    def description(self, obj):
        return (ur'''%s latest posts tagged as '%s' feed.''' % 
                (self.config.title, obj.name))

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('blog-tag-detail', None, {"slug": obj.name})

    def feed_url(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('posts-tagged-as', None, {"slug": obj.name})

    def items(self, obj):
        return TaggedItem.objects.filter(
            tag__name__iexact=obj.name,
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
