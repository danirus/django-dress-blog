#!/bin/bash

python manage.py syncdb --noinput
python manage.py migrate django_comments_xtd
python manage.py migrate flatblocks
python manage.py migrate inline_media
python manage.py loaddata ../../dress_blog/fixtures/flatblocks.json
python manage.py loaddata ../../dress_blog/fixtures/initial_data.json
python manage.py loaddata ../../dress_blog/fixtures/sample_users.json
python manage.py loaddata ../../dress_blog/fixtures/sample_posts.json
python manage.py loaddata fixtures/comments.json
python manage.py loaddata fixtures/django_comments_xtd.json
python manage.py loaddata fixtures/inline_media.json
python manage.py loaddata fixtures/tagging.json
