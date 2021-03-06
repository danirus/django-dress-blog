#-*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from inline_media.admin import AdminTextFieldWithInlinesMixin
from inline_media.widgets import TextareaWithInlines

from dress_blog.models import Config, Post, Story, Diary, DiaryDetail, Quote, BlogRoll


class ConfigAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": (("site", "title"), 
                                    ("show_author", "ping_google"),
                                    "theme",
                                    "email_subscribe_url", 
                                    "excerpt_length", "posts_in_index", 
                                    "stories_in_index", "diary_entries_in_index", 
                                    "quotes_in_index",  "comments_in_index")}),
                 ("META", {"fields": ("meta_author", "meta_description",
                                      "meta_keywords", )}),)

admin.site.register(Config, ConfigAdmin)

class PostAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(PostAdmin, self).formfield_for_dbfield(
            db_field, **kwargs) # get the default field
        
        from django import forms
        from django.contrib.auth import models

        if db_field.name == "author":
            queryset = models.User.objects.all()
            field = forms.ModelChoiceField(queryset=queryset, 
                                           initial=self.current_user.id)

        return field

    def get_form(self, req, obj=None, **kwargs):
        # save the currently logged in user for later
        self.current_user = req.user
        return super(PostAdmin, self).get_form(req, obj, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        if obj.author == request.user:
            return True
        if obj.status == 2 and request.user.has_perm("dress_blog.can_review_posts"):
            return True
        return False
        

class StoryAdmin(AdminTextFieldWithInlinesMixin, PostAdmin):
    list_display  = ("title", "pub_date", "tags", 
                     "author", "status", "visits")
    list_filter   = ("author", "status", "pub_date", "tags")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = ((None, {"fields": ("title", "slug",  
                                    "markup", "abstract", "body",)}),
                 ("Post data", {"fields": (("author", "status"), 
                                           ("allow_comments", "tags"),
                                           ("pub_date",)),}),
                 ("Converted markup", {"classes": ("collapse",),
                                       "fields": ("abstract_markup", 
                                                  "body_markup",),}),)
            
admin.site.register(Story, StoryAdmin)


class DiaryDetailInline(AdminTextFieldWithInlinesMixin, admin.StackedInline):
    model = DiaryDetail
    fieldsets = ((None, {"fields": (("status", "author", "markup", "tags", 
                                     "allow_comments"),
                                    ("body", "pub_date")),}),
                 ("Converted markup", {"classes": ("collapse",),
                                       "fields": ("body_markup",),}),)
    extra = 0
        
    def get_form(self, req, obj=None, **kwargs):
        # save the currently logged in user for later
        self.current_user = req.user
        return super(DiaryAdmin, self).get_form(req, obj, **kwargs)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(DiaryDetailInline, self).formfield_for_dbfield(
            db_field, **kwargs) # get the default field
        
        from django import forms
        from django.contrib.auth import models

        if db_field.name == "author":
            if kwargs.get("request", False):
                current_user = kwargs["request"].user
                queryset = models.User.objects.all()
                field = forms.ModelChoiceField(queryset=queryset, 
                                               initial=current_user.id)
        elif db_field.name == "body":
            field = db_field.formfield(widget=TextareaWithInlines(attrs={'rows':3}))

        return field

class DiaryAdmin(admin.ModelAdmin):
    list_display = ("pub_date", "entries", "visits")
    inlines = [DiaryDetailInline,]
    
    def entries(self, obj):
        return obj.detail.count()

    def visits(self, obj):
        q = obj.detail.all()
        return 0 if not q.count() else q[0].visits

admin.site.register(Diary, DiaryAdmin)


class QuoteAdmin(AdminTextFieldWithInlinesMixin, PostAdmin):
    list_display = ("title", "pub_date", "mod_date", 
                    "author", "status", "visits")
    list_filter  = ("author", "status", "pub_date", "tags")
    search_fields = ("title", "author", "quote_author", "body")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = ((None, {"fields": ("title", "slug", "markup", "body",)}),
                 ("Source data", {"fields": ("quote_author", "url_source")}),
                 ("Post data", {"fields": (("author", "status"), 
                                           ("allow_comments", "tags"),
                                           ("pub_date",)),}),
                 ("Converted markup", {"classes": ("collapse",),
                                       "fields": ("body_markup",),}),)

admin.site.register(Quote, QuoteAdmin)


class BlogRollAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "sort_order", )
    list_editable = ("sort_order",)

admin.site.register(BlogRoll, BlogRollAdmin)
