Django-dress-blog
=================

By Daniel Rus Morales <http://danir.us/>

* http://pypi.python.org/pypi/django-dress-blog/
* http://github.com/danirus/django-dress-blog/

Yet another Django pluggable blogging app that features:

1. Three different type of posts: Stories, Quotes and Diary Entries.
2. Choose between either 3 or 4 columns layout format.
3. Default theme based on `twitter-bootstrap <http://twitter.github.com/bootstrap/>`_.
4. Create new themes without modifying existing code.
5. Posts may be in Draft/Public status, and published in the future.
6. Posts categorized with tags, with `django-tagging <http://code.google.com/p/django-tagging/>`_.
7. Independent paginated list of Stories, Quotes and Comments.
8. Comments managed with `django-comments-xtd <http://packages.python.org/django-comments-xtd/>`_.
9. Support for inline media with `django-inline-media <http://packages.python.org/django-inline-media/>`_.
10. Blogroll, Multiple Authors, Search capabilities with `django-haystack <http://packages.python.org/django-haystack/>`_, and more.

Documentation work in progress, so far the list of features and a screenshot:

* `Read The Docs`_
* `Python Packages Site`_

.. _`Read The Docs`: http://readthedocs.org/docs/django-dress-blog/
.. _`Python Packages Site`: http://packages.python.org/django-dress-blog/

Install the app and run the example site to see it in action:

1. Create a VirtualEnv for the app
2. Git clone: `git clone git://github.com/danirus/django-dress-blog.git`
3. Cd into `django-dress-blog` and install requirements: `pip install requirements`
4. To have search functionality up & running:
    * Install Xapian >= 1.2, and
    * Copy: `cp ../src/xapian-haystack/xapian_backend.py ../src/django-haystack/haystack/backends/`
5. If you don't want to have search at the moment just edit `django-dress-blog/example/demo/settings.py` and comment out `"haystack"` in `INSTALLED_APPS`
6. Cd into `django-dress-blog/example/demo`
7. Run `python manage.py collectstatic`, and answer yeah!
8. Run `python manage.py syncdb --noinput` (user: admin, pwd: admin)
9. If you have installed xapian, build the search index:
    * `python manage.py rebuild_index`
10. Run `python manage.py localhost` and hit http://localhost:8000

Remember, it's a beta yet!
