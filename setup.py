from setuptools import setup, find_packages

setup(
    name = "django-dress-blog",
    version = "0.1a",
    packages = find_packages(),
    include_package_data = True,
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
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
