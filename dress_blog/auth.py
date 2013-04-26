#-*- coding: utf-8 -*-

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from dress_blog.conf import settings


def initialize_groups():
    post_ct = ContentType.objects.filter(app_label="dress_blog", model="post")
    can_review = Permission.objects.get(content_type=post_ct, 
                                        codename="can_review_posts")

    # blog authors group
    blog_authors_grp = Group.objects.create(
        name=settings.DRESS_BLOG_AUTHORS_GROUP_NAME)
    for per in Permission.objects.filter(content_type=post_ct):
        if per != can_review:
            blog_authors_grp.permissions.add(per)
    blog_authors_grp.save()

    # blog reviewers group
    blog_reviewers_grp = Group.objects.create(
        name=settings.DRESS_BLOG_REVIEWERS_GROUP_NAME)
    blog_reviewers_grp.permissions.add(can_review)
    blog_reviewers_grp.save()

    return (blog_authors_grp, blog_reviewers_grp)
