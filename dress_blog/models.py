import six

import os.path

from django.db import models
from django.db.models import permalink, Q
from django.db.models.signals import post_delete
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from constance import config
from inline_media.fields import TextFieldWithInlines
from inline_media.utils import unescape_inline
from prosemirror.fields import ProseMirrorField
from taggit.managers import TaggableManager

from dress_blog.conf import settings
from dress_blog.utils import create_cache_key, colloquial_date


STATUS_CHOICES = ((1, _("Draft")), (2, _("Review")), (3, _("Public")),)
    

class PostManager(models.Manager):
    """Returns published posts that are not in the future."""
    
    def drafts(self, author=None):
        if not author:
            return self.get_queryset().filter(
                status=1).order_by("-mod_date")
        else:
            return self.get_queryset().filter(
                status=1, author=author).order_by("-mod_date")

    def reviews(self, author):
        if author.has_perm("dress_blog.can_review_posts"):
            return self.get_queryset().filter(status=2).order_by("-mod_date")
        else:
            return []

    def upcoming(self, author=None):
        if not author:
            return self.get_queryset().filter(
                status=3, pub_date__gt=now()).order_by("-mod_date")
        else:
            return self.get_queryset()\
                       .filter(status=3, author=author, pub_date__gt=now())\
                       .order_by("-mod_date")

    def published(self):
        return self.get_queryset().filter(status=3, pub_date__lte=now())

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
            qs = self.get_queryset()\
                     .filter(content_type__in=content_types, status__in=status)\
                     .exclude(~Q(author=author), status=1)
            if not author.has_perm("dress_blog.can_review_posts"):
                return qs.exclude(~Q(author=author), status=2)
            else:
                return qs
        else:
            return self.get_queryset()\
                       .filter(content_type__in=content_types, 
                               status__in=status, 
                               pub_date__lte=now())


class Post(models.Model):
    """A generic post."""
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'),
        related_name="content_type_set_for_%(class)s")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    author = models.ForeignKey(User, blank=True, null=True)
    allow_comments = models.BooleanField(default=True)
    pub_date = models.DateTimeField(_("Publication date"), default=now)
    mod_date = models.DateTimeField(_("Modification date"), auto_now=True)
    visits = models.IntegerField(default=0, editable=False)
    objects = PostManager()
    sites = models.ManyToManyField(Site)
    
    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        db_table = "dress_blog_post"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"
        permissions = ((_("can_review_posts"), _("Can review posts")),)

    def save(self, *args, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self)
        super(Post, self).save(*args, **kwargs)
        if self.status == 3: # public
            if config.ping_google:
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

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date="pub_date")
    abstract = TextFieldWithInlines()
    body = TextFieldWithInlines()
    tags = TaggableManager(blank=True)
    objects = PostManager()

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")
        db_table = "dress_blog_stories"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def __str__(self):
        return "%s" % self.title

    @permalink
    def get_absolute_url(self):
        kwargs = {"year": self.pub_date.year,
                  "month": self.pub_date.strftime("%b").lower(),
                  "day": self.pub_date.day,
                  "slug": self.slug}

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
        return self.get_queryset().filter(pub_date__lte=now())

class Diary(models.Model):
    pub_date = models.DateField(default=now)
    objects = DiaryManager()

    class Meta:
        verbose_name = _("diary entry")
        verbose_name_plural = _("diary entries")
        db_table = "dress_blog_diary"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def __str__(self):
        return colloquial_date(self.pub_date, 
                               settings.DRESS_BLOG_DIARY_DATE_FORMAT)

    @permalink
    def get_absolute_url(self):
        return ("blog-diary-detail", None,
                {"year": self.pub_date.year,
                 "month": self.pub_date.strftime("%b").lower(),
                 "day": self.pub_date.day})


class DiaryDetail(Post):
    """Diary Model"""
    diary = models.ForeignKey(Diary, related_name="detail")
    body = TextFieldWithInlines()
    tags = TaggableManager(blank=True)
    objects = PostManager()

    class Meta:
        verbose_name = _("diary entry detail")
        verbose_name_plural = _("diary entry detail")
        db_table = "dress_blog_diarydetail"
        ordering = ("-pub_date",)

    def __unicode__(self):
        return self.pub_date\
                   .strftime(ugettext("Diary on %A, %d %B %Y at %H:%Mh"))

    def get_absolute_url(self):
        return self.diary.get_absolute_url()


class Quote(Post):
    """Quote model"""
    title = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=255, unique=True)
    body = TextFieldWithInlines()
    quote_author = models.CharField(blank=False, null=False, max_length=255,
                                    help_text=_("quote's author"))
    url_source = models.URLField(blank=True, null=True)
    tags = TaggableManager(blank=True)
    objects = PostManager()

    class Meta:
        verbose_name = _("quote")
        verbose_name_plural = _("quotes")
        db_table = "dress_blog_quotes"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def __str__(self):
        return u"%s" % self.title

    @permalink
    def get_absolute_url(self):
        kwargs = {"year": self.pub_date.year,
                  "month": self.pub_date.strftime("%b").lower(),
                  "day": self.pub_date.day,
                  "slug": self.slug}
        if self.status == 1:
            return ("blog-quote-detail-draft", None, kwargs)
        if self.status == 2:
            return ("blog-quote-detail-review", None, kwargs)
        elif self.pub_date > now():
            return ("blog-quote-detail-upcoming", None, kwargs)
        else:
            return ("blog-quote-detail", None, kwargs)


def delete_post_tags(sender, instance, **kwargs):
    instance.tags.clear()


post_delete.connect(delete_post_tags, sender=Story)
post_delete.connect(delete_post_tags, sender=Quote)
post_delete.connect(delete_post_tags, sender=DiaryDetail)


class BlogRoll(models.Model):
    """Blogs you like."""

    name = models.CharField(max_length=100)
    url = models.URLField()
    authors = models.CharField(blank=False, null=False, max_length=1024,
                               help_text=_("Comma separated list of authors"))
    sort_order = models.PositiveIntegerField(default=1000)

    class Meta:
        ordering = ("sort_order", "name",)
        verbose_name = _("blog roll")
        verbose_name_plural = _("blog roll")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url

