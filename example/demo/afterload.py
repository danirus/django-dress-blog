#!/usr/bin/env python

import imp
import sys
import os
import os.path

PRJ_PATH = os.path.abspath(os.path.curdir)
PARENT_PRJ_PATH = os.path.abspath(os.path.join(PRJ_PATH, os.pardir))
APP_PATH = os.path.abspath(os.path.join(PARENT_PRJ_PATH, os.pardir))

sys.path.insert(0, APP_PATH)
sys.path.insert(0, PARENT_PRJ_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings
from django.contrib.contenttypes.models import ContentType
from dress_blog.models import Post, Story, Quote, DiaryDetail
from django_comments_xtd.models import XtdComment

def fix_content_types():
    """Fix content type attributes of dress_blog instances.

    Dress_blog models' instances may have wrong content type values
    as a result of loading the fixture. This may happen during the
    schema creation when creating the database for the demo project.
    """
    # fix content type for stories
    story_ct = ContentType.objects.get_for_model(Story)
    for story in Story.objects.all():
        story.content_type = story_ct
        story.save()

    # fix content type for quotes
    quote_ct = ContentType.objects.get_for_model(Quote)
    for quote in Quote.objects.all():
        quote.content_type = quote_ct
        quote.save()

    # fix content type for diarydetail
    diarydetail_ct = ContentType.objects.get_for_model(DiaryDetail)
    for diarydetail in DiaryDetail.objects.all():
        diarydetail.content_type = diarydetail_ct
        diarydetail.save()

    # fix content type for xtdcomments
    for xtdcomment in XtdComment.objects.all():
        if xtdcomment.id in range(1, 11):
            xtdcomment.content_type = diarydetail_ct
        elif xtdcomment.id in [11, 12]:
            xtdcomment.content_type = quote_ct
        elif xtdcomment.id == 13:
            xtdcomment.content_type = story_ct
        xtdcomment.save()
        

if __name__ == '__main__':
    fix_content_types()
    
