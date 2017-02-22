import sys
from setuptools import setup, find_packages
from setuptools.command.test import test


def run_tests(*args):
    from dress_blog.tests import run_tests
    errors = run_tests()
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


test.run_tests = run_tests


setup(
    name="django-dress-blog",
    version="0.3.0",
    packages=find_packages(),
    keywords="django apps",
    license="MIT",
    description=("Django blogging app with stories, quotes, diary, "
                 "comments and tags."),
    long_description=("Yet another Django blogging app with stories, quotes, "
                      "diary, comments and tags. "),
    author="Daniel Rus Morales",
    author_email="inbox@danir.us",
    maintainer="Daniel Rus Morales",
    maintainer_email="mbox@danir.us",
    url="http://pypi.python.org/pypi/django-dress-blog/",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
    include_package_data=True,
    test_suite="dummy"
)
