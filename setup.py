from setuptools import setup, find_packages

from setuptools.command.test import test

def run_tests(*args):
    from dress_blog.tests import run_tests
    run_tests()

test.run_tests = run_tests

setup(
    name = "django-dress-blog",
    version = "0.2a",
    packages = find_packages(),
    keywords = "django apps",
    license = "MIT",
    description = "Django blogging app with stories, quotes, diary, comments and tags.",
    long_description = "Yet another Django blogging app with stories, quotes, diary, comments and tags. ",
    author = "Daniel Rus Morales",
    author_email = "inbox@danir.us",
    maintainer = "Daniel Rus Morales",
    maintainer_email = "inbox@danir.us",
    url = "http://pypi.python.org/pypi/django-dress-blog/",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    include_package_data = True,
    test_suite = "dummy",
)
