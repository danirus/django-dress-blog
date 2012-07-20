#-*- coding: utf-8 -*-

from haystack import indexes
from dress_blog.models import Story, Quote, DiaryDetail


class StoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Story

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.published()


class QuoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Quote

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.published()


class DiaryDetailIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return DiaryDetail

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.published()
