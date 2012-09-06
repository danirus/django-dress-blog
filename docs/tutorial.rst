.. _ref-tutorial:

========
Tutorial
========

Django-dress-blog is a blogging app that allows authors post stories, quotes and diary entries.

Motivation
==========

Django-dress-blog is a blogging app inspired by `Kevin Fricovsky's django-mingus <https://github.com/montylounge/django-mingus>`_ that offers authors three different type of posts: **stories** to write their own content, **quotes** to cite other people's content, and the **diary** to micro-post on anything in a quick fashion. 

Django-dress-blog is suitable for start-ups and other collaborative projects, may show posts' author, and it comes with a fully functional theme based on `twitter-bootstrap <http://twitter.github.com/bootstrap/>`_ and support for extra themes.

Its search functionality make use of `django-haystack <http://haystacksearch.org/>`_, which supports up to four different search engines. The default installation uses `xapian-haystack <https://github.com/notanumber/xapian-haystack/>`_.

Using Django-dress-blog authors categorize content by tagging, what produces a `Folksonomy <http://en.wikipedia.org/wiki/Folksonomy>`_, allowing categorization on the go rather than enforcing category creation in advance.

Installation
============

Installing Django-dress-blog is as simple as checking out the sources and adding the path to your project or ``PYTHONPATH``.

Use git, pip or easy_install to check out Django-dress-blog from Github_ or get a release from PyPI_:

  1. Use **git** to clone the repository, and then install the package (read more about git_):

    * ``git clone git://github.com/danirus/django-dress-blog.git`` and

    * ``python setup.py install``

  2. Or use **pip** (read more about pip_):

    * Do ``pip install django-dress-blog``, or

    * Edit your project's ``requirements`` file and append either the Github_ URL or the package name ``django-dress-blog``, and then do ``pip install -r requirements``.

  3. Or use **easy_install** (read more about easy_install_): 

    * Do ``easy_install django-dress-blog``


.. _Github: http://github.com/danirus/django-dress-blog
.. _PyPI: http://pypi.python.org/
.. _pip: http://www.pip-installer.org/
.. _easy_install: http://packages.python.org/distribute/easy_install.html
.. _git: http://git-scm.com/

Configuration
=============

It is assumed you have pip_ installed and virtualenv_. Although virtualenv_ is not a requirement, just a healthy recommendation. Configuration comprehends the following steps:

.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html

1. Install the dependencies listed in the ``requirements`` file::

    pip install -r requirements

2. Add the following entries to ``INSTALLED_APPS`` in your ``settings.py`` file::

    'django.contrib.staticfiles', 
    'django.contrib.comments',
    'django_comments_xtd', 
    'django_markup', 
    'inline_media', 
    'flatblocks', 
    'sorl.thumbnail', 
    'tagging', 
    'request', 
    'dress_blog', 
    'haystack',

3. Some of the new installed apps requires extra configuration. Edit your ``settings.py`` file again and append the next entries:

    * For the comments app::

        COMMENTS_APP = 'django_comments_xtd'
	COMMENTS_XTD_CONFIRM_EMAIL = True
	COMMENTS_XTD_SALT = 'es-war-einmal-una-bella-princesa-in-a-beautiful-castle'

    * For Django-tagging::

        FORCE_LOWERCASE_TAGS = True

    * For sorl.thumbnail::

        THUMBNAIL_BACKEND = 'inline_media.sorl_backends.AutoFormatBackend'
        THUMBNAIL_FORMAT = 'JPEG'

    * For request::

        REQUEST_IGNORE_AJAX = True
	REQUEST_IGNORE_USERNAME = ["admin"]
	REQUEST_IGNORE_PATHS = (r'^admin/', r'^favicon.ico')
	REQUEST_TRAFFIC_MODULES = (
            'request.traffic.UniqueVisitor',
            'request.traffic.UniqueVisit',
            'request.traffic.Hit',
            'request.traffic.Search',
        )

    * For Django-haystack, when using the Xapian search engine::

        HAYSTACK_CONNECTIONS = {
            'default': {
                'ENGINE': 'haystack.backends.xapian_backend.XapianEngine',
                'PATH': os.path.join(os.path.dirname(__file__), 'xapian_index'),
            },
        }

    * For Django-dress-blog::

        DRESS_BLOG_PAGINATE_BY = 10
	DRESS_BLOG_UI_COLUMNS = 3
	DRESS_BLOG_THEMES_PATH = os.path.join(STATIC_ROOT, 'dress_blog/themes')


4. To use the XapianEngine backend with Haystack you have to copy the ``xapian_backend.py`` file from the xapian_haystack directory into django-haystack's backends directory. Go to your VirtualEnv ``src/`` directory and copy the file::

    cp xapian-haystack/xapian_backend.py django-haystack/haystack/backends/

5. Add a new context processor to ``TEMPLATE_CONTEXT_PROCESSORS`` in your ``settings.py`` file::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
	'dress_blog.context_processors.config',
    )

6. Edit your ``urls.py`` file and add the following entries::

    url(r'^blog/',            include('dress_blog.urls')),
    url(r"^comments/",        include("django_comments_xtd.urls")),

7. Collect static files provided with Django-dress-blog::

    python manage.py collectstatic


8. Build the Xapian search index in a regular basis to track new content added to your blog by running the following command::

    python manage.py rebuild_index

9. Create database data structures::

    python manage.py syncdb

10. Run you project dev web server and hit your project's dress-blog URL <http://localhost:8000/blog>_::

    python manage.py runserver
