#-*- coding: utf-8 -*-

import os
from django.conf import settings


# Default number of post entries per page
DRESS_BLOG_PAGINATE_BY = 10

# Default number of columns in the homepage.
# Based on the current theme and templates the 
# only two options are 3 or 4
DRESS_BLOG_UI_COLUMNS = 3

# Set to False when you don't want to disable
# search capabilities. Otherwise proceed to
# setup haystack
DRESS_BLOG_SEARCH_URL_ACTIVE = True

# Base directory to look for themes directories.
DRESS_BLOG_THEMES_PATH = os.path.join(settings.STATIC_ROOT, 
                                      'dress_blog/themes')

# Used to render dates in the diary 
DRESS_BLOG_DIARY_DATE_FORMAT = "l, j F Y"

# Name for the blog authors group. Needed to feed 
# the authors filterin the admin UI.
DRESS_BLOG_AUTHORS_GROUP_NAME = "Blog Authors"

DRESS_BLOG_REVIEWERS_GROUP_NAME = "Blog Reviewers"
