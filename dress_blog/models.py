#-*- coding: utf-8 -*-

import os.path

from django.db import models
from django.db.models import permalink, Q
from django.db.models.signals import post_delete
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from django_markup.fields import MarkupField
from django_markup.markup import formatter
from inline_media.fields import TextFieldWithInlines
from inline_media.utils import unescape_inline
from tagging.fields import TagField
from tagging.models import TaggedItem
from tagging.utils import get_tag_list

from dress_blog.conf import settings
from dress_blog.utils import create_cache_key, colloquial_date


STATUS_CHOICES = ((1, _("Draft")), (2, _("Review")), (3, _("Public")),)

UI_COVER_CHOICES = (("3col", _("3 columns")), ("4col", _("4 columns")),)


def themes(path):
    for dirname in os.listdir(path):
        yield (dirname, dirname)


class Config(models.Model):
    """Django-dress-blog configuration"""

    site = models.ForeignKey(Site, unique=True, related_name="+")
    title = models.CharField(max_length=100, 
                             help_text=_("Blog's name or title"))
    theme = models.CharField(max_length=50, default="initial", 
                             help_text=_("Design for the blog"), 
                             choices=themes(settings.DRESS_BLOG_THEMES_PATH))
    posts_in_index = models.IntegerField(default=1, help_text=_(
            "Visible posts in 3-columns layout front page."))
    stories_in_index = models.IntegerField(default=5, help_text=_(
            "Visible stories in 4-columns layout front page."))
    quotes_in_index = models.IntegerField(default=5, help_text=_(
            "Visible quotes in 4-columns layout front page."))
    diary_entries_in_index = models.IntegerField(default=1, help_text=_(
            "Visible days in diary in front page."))
    comments_in_index = models.IntegerField(default=5, help_text=_(
            "Visible comments in front page."))
    email_subscribe_url = models.URLField(_("subscribe via email url"), 
                                          blank=True, null=True)
    show_author = models.BooleanField(default=False, help_text=_(
            "Show author's full name along in posts"))
    ping_google = models.BooleanField(default=False, help_text=_(
            "Notify Google on new submissions"))
    excerpt_length = models.IntegerField(default=500, help_text=_(
            "The character length of the post body field displayed in RSS "
            "and preview templates."))
    meta_author = models.CharField(max_length=255, help_text=_(
            "List of authors or company/organization's name"))
    meta_keywords = models.CharField(max_length=255, help_text=_(
            "List of keywords to help improve quality of search results"))
    meta_description = models.TextField(blank=True, help_text=_(
            "What the blog is about, topics, editorial line..."))
    
    class Meta:
        db_table = "dress_blog_config"
        verbose_name = _("app config")
        verbose_name_plural = _("app config")

    def __unicode__(self):
        return "%s dress-blog config" % self.site.name

    def delete(self, *args, **kwargs):
        if settings.SITE_ID != self.site.id:
            super(Config, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Config, self).save(*args, **kwargs)
        self.site_name = self.site.name
        key = create_cache_key(Config, field="site__id", 
                               field_value=self.site.id)
        cache.set(key, self)

    @staticmethod
    def get_current():
        site = Site.objects.get_current()
        key = create_cache_key(Config, field="site__id", 
                               field_value=site.id)
        config = cache.get(key, None)
        if config is None:
            try:
                config = Config.objects.get(site=site)
                cache.add(key, config)
            except Config.DoesNotExist:
                return None
        return config


class PostManager(models.Manager):
    """Returns published posts that are not in the future."""
    
    def drafts(self, author=None):
        if not author:
            return self.get_query_set().filter(
                status=1).order_by("-mod_date")
        else:
            return self.get_query_set().filter(
                status=1, author=author).order_by("-mod_date")

    def reviews(self, author):
        if author.has_perm("dress_blog.can_review_posts"):
            return self.get_query_set().filter(status=2).order_by("-mod_date")
        else:
            return []

    def upcoming(self, author=None):
        if not author:
            return self.get_query_set().filter(
                status=3, pub_date__gt=now()).order_by("-mod_date")
        else:
            return self.get_query_set().filter(
                status=3, author=author, pub_date__gt=now()).order_by("-mod_date")

    def published(self):
        return self.get_query_set().filter(status=3, pub_date__lte=now())

    def for_app_models(self, *args, **kwargs):
        """Return posts for pairs "app.model" given in args"""
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app, 
                                                         model=model))
        return self.for_content_types(content_types, **kwargs)

    def for_content_types(self, content_types, status=[3], author=None):
        if min(status) < 3 and author: # show drafts anf reviews for the author
            qs = self.get_query_set().filter(
                content_type__in=content_types, 
                status__in=status).exclude(~Q(author=author), status=1)
            if not author.has_perm("dress_blog.can_review_posts"):
                return qs.exclude(~Q(author=author), status=2)
            else:
                return qs
        else:
            return self.get_query_set().filter(
                content_type__in=content_types, 
                status__in=status, 
                pub_date__lte=now())


class Post(models.Model):
    """A generic post."""
    content_type   = models.ForeignKey(ContentType,
                                       verbose_name=_('content type'),
                                       related_name="content_type_set_for_%(class)s")
    status         = models.IntegerField(choices=STATUS_CHOICES, default=1)
    author         = models.ForeignKey(User, blank=True, null=True)
    allow_comments = models.BooleanField(default=True)
    pub_date       = models.DateTimeField(_("Publication date"), default=now)
    mod_date       = models.DateTimeField(_("Modification date"), auto_now=True)
    visits         = models.IntegerField(default=0, editable=False)
    objects        = PostManager()
    site           = models.ForeignKey(Site)

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        db_table  = "dress_blog_post"
        ordering  = ("-pub_date",)
        get_latest_by = "pub_date"
        permissions = ((_("can_review_posts"), _("Can review posts")),)

    def save(self, *args, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self)
        self.site_id      = settings.SITE_ID
        super(Post, self).save(*args, **kwargs)
        if self.status == 3: # public
            blog_config = Config.get_current()
            if getattr(blog_config, "ping_google", False):
                try:
                    ping_google()
                except:
                    pass

    @property
    def in_the_future(self):
        return self.pub_date > now()

    def get_absolute_url(self):
        instance = self.content_type.model_class().objects.get(pk=self.id)
        return instance.get_absolute_url()


class Story(Post):
    """Story model"""

    title           = models.CharField(max_length=200)
    slug            = models.SlugField(unique_for_date="pub_date")
    markup          = MarkupField(default="markdown")
    abstract        = TextFieldWithInlines()
    abstract_markup = models.TextField(editable=True, blank=True, null=True)
    body            = TextFieldWithInlines()
    body_markup     = models.TextField(editable=True, blank=True, null=True)
    tags            = TagField()
    objects         = PostManager()

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")
        db_table  = "dress_blog_stories"
        ordering  = ("-pub_date",)
        get_latest_by = "pub_date"

    def __unicode__(self):
        return u"%s" % self.title

    def save(self, *args, **kwargs):
        self.abstract_markup = mark_safe(
            formatter(self.abstract, filter_name=self.markup))
        self.body_markup = mark_safe(
            formatter(self.body, filter_name=self.markup))
        if self.markup == "restructuredtext":
            self.abstract_markup = unescape_inline(self.abstract_markup)
            self.body_markup = unescape_inline(self.body_markup)
        super(Story, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        kwargs = { "year": self.pub_date.year,
                   "month": self.pub_date.strftime("%b").lower(),
                   "day": self.pub_date.day,
                   "slug": self.slug }

        if self.status == 1:
            return ("blog-story-detail-draft", None, kwargs)
        if self.status == 2:
            return ("blog-story-detail-review", None, kwargs)
        elif self.pub_date > now():
            return ("blog-story-detail-upcoming", None, kwargs)
        else:
            return ("blog-story-detail", None, kwargs)


class DiaryManager(models.Manager):
    """Return published diary entries that are not in the future."""

    def published(self):
        return self.get_query_set().filter(pub_date__lte=now())

class Diary(models.Model):
    pub_date       = models.DateField(default=now)
    objects        = DiaryManager()

    class Meta:
        verbose_name = _("diary entry")
        verbose_name_plural = _("diary entries")
        db_table = "dress_blog_diary"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def __unicode__(self):
        return colloquial_date(self.pub_date, 
                               settings.DRESS_BLOG_DIARY_DATE_FORMAT)

    @permalink
    def get_absolute_url(self):
        return ("blog-diary-detail", None, {
                "year": self.pub_date.year,
                "month": self.pub_date.strftime("%b").lower(),
                "day": self.pub_date.day
        })


class DiaryDetail(Post):
    """Diary Model"""

    diary       = models.ForeignKey(Diary, related_name="detail")
    markup      = MarkupField(default="markdown")
    body        = TextFieldWithInlines()
    body_markup = models.TextField(editable=True, blank=True, null=True)
    tags        = TagField()
    objects     = PostManager()

    class Meta:
        verbose_name = _("diary entry detail")
        verbose_name_plural = _("diary entry detail")
        db_table = "dress_blog_diarydetail"
        ordering = ("-pub_date",)

    def save(self, *args, **kwargs):
        self.body_markup = mark_safe(
            formatter(self.body, filter_name=self.markup))
        super(DiaryDetail, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.pub_date.strftime(ugettext("Diary on %A, %d %B %Y at %H:%Mh"))

    def get_absolute_url(self):
        return self.diary.get_absolute_url()


class Quote(Post):
    """Quote model"""

    title        = models.CharField(max_length=100, blank=False, null=False)
    slug         = models.SlugField(max_length=255, unique=True)
    markup       = MarkupField(default="markdown")
    body         = TextFieldWithInlines()
    body_markup  = models.TextField(editable=True, blank=True, null=True)
    quote_author = models.CharField(blank=False, null=False, max_length=255,
                                    help_text=_("quote's author"))
    url_source   = models.URLField(blank=True, null=True)
    tags         = TagField()
    objects      = PostManager()

    class Meta:
        verbose_name = _("quote")
        verbose_name_plural = _("quotes")
        db_table  = "dress_blog_quotes"
        ordering  = ("-pub_date",)
        get_latest_by = "pub_date"

    def __unicode__(self):
        return u"%s" % self.title

    def save(self, *args, **kwargs):
        self.body_markup = mark_safe(formatter(self.body, 
                                               filter_name=self.markup))
        super(Quote, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        kwargs = { "year": self.pub_date.year,
                   "month": self.pub_date.strftime("%b").lower(),
                   "day": self.pub_date.day,
                   "slug": self.slug }
        if self.status == 1:
            return ("blog-quote-detail-draft", None, kwargs)
        if self.status == 2:
            return ("blog-quote-detail-review", None, kwargs)
        elif self.pub_date > now():
            return ("blog-quote-detail-upcoming", None, kwargs)
        else:
            return ("blog-quote-detail", None, kwargs)


def delete_post_tags(sender, instance, **kwargs):
    try:
        ctype = ContentType.objects.get_for_model(instance)
        tags = get_tag_list(instance.tags)
        TaggedItem._default_manager.filter(content_type__pk=ctype.pk,
                                           object_id=instance.pk,
                                           tag__in=tags).delete()
        for tag in tags:
            if not tag.items.count():
                tag.delete()
    except Exception, e:
        # let 'django.request' logger handle the exception
        raise e

post_delete.connect(delete_post_tags, sender=Story)
post_delete.connect(delete_post_tags, sender=Quote)
post_delete.connect(delete_post_tags, sender=DiaryDetail)


class BlogRoll(models.Model):
    """Blogs you like."""

    name       = models.CharField(max_length=100)
    url        = models.URLField()
    authors    = models.CharField(blank=False, null=False, max_length=1024,
                                  help_text=_("Comma separated list of authors"))
    sort_order = models.PositiveIntegerField(default=1000)

    class Meta:
        ordering = ("sort_order", "name",)
        verbose_name = _("blog roll")
        verbose_name_plural = _("blog roll")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.url

