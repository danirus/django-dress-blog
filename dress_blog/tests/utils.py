# -*- coding: utf-8 -*-

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
