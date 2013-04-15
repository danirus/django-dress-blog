#-*- coding: utf-8 -*-

import datetime
import mock
import os
import sys

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase

from dress_blog.models import Config, Post, Story, Quote, DiaryDetail
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

    def test_for_content_types_with_default_kwargs(self):
        # with just a list of content types it returns already published 
        # posts for the given list of content types
        storyct = ContentType.objects.get(app_label='dress_blog', model='story')
        stories = Post.objects.for_content_types([storyct])
        self.assert_(stories.count() == Story.objects.published().count())

    def test_for_content_types_with_status_and_wo_author(self):
        storyct = ContentType.objects.get(app_label='dress_blog', model='story')
        # without author and a given status it returns posts of the given
        # list of content types under the given status
        statuses = [3] # public
        stories = Post.objects.for_content_types([storyct], status=statuses)
        self.assert_(stories.count() == Story.objects.published().count())
        statuses = [2] # reviews
        stories = Post.objects.for_content_types([storyct], status=statuses)
        self.assert_(stories.count() == 2) # 2 stories in review in the fixture
        statuses = [1] # reviews
        stories = Post.objects.for_content_types([storyct], status=statuses)
        self.assert_(stories.count() == 2) # 2 stories in draft in the fixture

    def test_for_content_types_with_author_and_default_status(self):
        storyct = ContentType.objects.get(app_label='dress_blog', model='story')
        # when min status is not < 3 it ignores author
        admin = User.objects.get(username="admin")
        alice = User.objects.get(username="alice")
        statuses = [3] # public
        stories = []
        for user in [admin, alice]:
            qres = Post.objects.for_content_types([storyct], author=user)
            self.assert_(qres.count() == Story.objects.published().count())
            stories.append(len(qres))            
        self.assert_(stories[0] == stories[1])

    def test_for_content_types_with_author_and_min_status_below_three(self):
        # when requesting drafts and/or reviews for a given user, drafts for
        # users other than the given one should be excluded.
        storyct = ContentType.objects.get(app_label='dress_blog', model='story')
        admin = User.objects.get(username="admin")
        stories = Post.objects.for_content_types([storyct], 
                                                 status=[1,2],
                                                 author=admin)
        # stories should not include drafts from a user other than admin
        for story in stories:
            self.assertFalse(story.author!=admin and story.status==1)

    def test_for_content_types_with_author_without_review_permission(self):
        # same as previous but the user has no 'dress_blog.can_review_posts'
        # permission, so results should exclude reviews and drafts for users
        # other than the given, and the given doesn't have no posts, and
        # status is [1,2], so query result must be empty
        new_user = User.objects.create_user('tempuser')
        storyct = ContentType.objects.get(app_label='dress_blog', model='story')
        stories = Post.objects.for_content_types([storyct], 
                                                 status=[1,2],
                                                 author=new_user)
        self.assert_(len(stories) == 0)


class PostClassPermissionsTestCase(DjangoTestCase):
    def test_class_has_permission_can_review_posts(self):
        postct = ContentType.objects.get(app_label='dress_blog', model='post')
        perms = Permission.objects.filter(content_type=postct, 
                                          codename='can_review_posts')
        self.assert_(len(perms))

class PostSaveMethodTestCase(DjangoTestCase):
    fixtures = ["sample_users", "sample_posts",]
    
    def setUp(self):
        config = Config.get_current()
        config.ping_google = True
        config.save()

    @mock.patch('dress_blog.models.ping_google')
    def test_save_ping_google(self, mock_function):
        # change from draft to public and see whether it calls ping_google
        post = Post.objects.drafts()[0]
        post.status = 3
        post.save()
        assert mock_function.called
