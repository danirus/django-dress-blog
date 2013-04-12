#-*- coding: utf-8 -*-

import datetime
import os
import sys

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase

from dress_blog.models import Post, Story, Quote, DiaryDetail
from dress_blog.tests.utils import fix_content_types

class PostManagerTestCase(DjangoTestCase):
    fixtures = ["sample_users", "sample_posts",]
    author = None

    def setUp(self):
        self.author = User.objects.get(username="admin")
        fix_content_types()

    def test_sample_fixture_content(self):
        self.assert_(Story.objects.drafts().count()==2)
        self.assert_(Story.objects.reviews(author=self.author).count()==2)
        self.assert_(Story.objects.published().count()==7)
        self.assert_(Quote.objects.drafts().count()==1)
        self.assert_(Quote.objects.reviews(author=self.author).count()==0)
        self.assert_(Quote.objects.published().count()==6)
        self.assert_(DiaryDetail.objects.drafts().count()==0)
        self.assert_(DiaryDetail.objects.reviews(author=self.author).count()==0)
        self.assert_(DiaryDetail.objects.published().count()==4)

    def test_drafts_are_ordered(self):
        drafts = Post.objects.drafts()
        for idx in xrange(len(drafts)-1):
            self.assert_( drafts[idx].mod_date > drafts[idx+1].mod_date )

    def test_drafts_with_user(self):
        self.assert_(Story.objects.drafts(author=self.author).count()==1)
        drafts = Post.objects.drafts(author=self.author)
        for idx in xrange(len(drafts)-1):
            self.assert_( drafts[idx].mod_date > drafts[idx+1].mod_date )

    def test_reviews_without_permissions(self):
        new_user = User.objects.create_user('tempuser')
        self.assert_(Story.objects.reviews(author=new_user)==[])

    def test_reviews_are_ordered(self):
        stories = Story.objects.reviews(author=self.author)
        self.assert_(stories.count()==2)
        for idx in xrange(len(stories)-1):
            self.assert_( stories[idx].mod_date > stories[idx+1].mod_date )

    def test_upcoming(self):
        self.assert_(Post.objects.upcoming().count()==0)
        story = Story.objects.published()[0]
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        story.pub_date = tomorrow
        story.save()
        self.assert_(Post.objects.upcoming().count()==1) 
        # story's author is alice, self.author is admin
        self.assert_(Post.objects.upcoming(author=self.author).count()==0)
        
    def test_for_app_models(self):
        # for_app_models retrieves posts with status 'Public' or 3
        stories = Post.objects.for_app_models('dress_blog.story')
        self.assert_(stories.count() == Story.objects.published().count())
