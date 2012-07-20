python manage.py dumpdata --indent 4 --format json -v 2 \
    sites.Site \
    auth.User \
    dress_blog.Post \
    dress_blog.Story \
    dress_blog.Diary \
    dress_blog.DiaryDetail \
    dress_blog.Quote \
    dress_blog.BlogRoll \
    inline_media.InlineType \
    inline_media.PictureSet \
    inline_media.Picture \
    comments.Comment \
    django_comments_xtd.XtdComment \
    tagging.Tag \
    tagging.TaggedItem > initial_data.json

python manage.py dumpdata --indent 4 --format json -v 2 \
    dress_blog.Config \
    flatblocks.Flatblock > ../../dress_blog/fixtures/initial_data.json