# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 11:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_markup.fields
import inline_media.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogRoll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('authors', models.CharField(help_text='Comma separated list of authors', max_length=1024)),
                ('sort_order', models.PositiveIntegerField(default=1000)),
            ],
            options={
                'verbose_name': 'blog roll',
                'verbose_name_plural': 'blog roll',
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'diary entry',
                'verbose_name_plural': 'diary entries',
                'db_table': 'dress_blog_diary',
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Review'), (3, 'Public')], default=1)),
                ('allow_comments', models.BooleanField(default=True)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Publication date')),
                ('mod_date', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('visits', models.IntegerField(default=0, editable=False)),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
                'db_table': 'dress_blog_post',
                'ordering': ('-pub_date',),
                'permissions': (('can_review_posts', 'Can review posts'),),
                'get_latest_by': 'pub_date',
            },
        ),
        migrations.CreateModel(
            name='DiaryDetail',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dress_blog.Post')),
                ('markup', django_markup.fields.MarkupField(choices=[('none', 'None (no processing)'), ('linebreaks', 'Linebreaks'), ('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText')], default='markdown', max_length=255, verbose_name='markup')),
                ('body', inline_media.fields.TextFieldWithInlines()),
                ('body_markup', models.TextField(blank=True, null=True)),
                ('diary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detail', to='dress_blog.Diary')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'diary entry detail',
                'verbose_name_plural': 'diary entry detail',
                'db_table': 'dress_blog_diarydetail',
                'ordering': ('-pub_date',),
            },
            bases=('dress_blog.post',),
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dress_blog.Post')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('markup', django_markup.fields.MarkupField(choices=[('none', 'None (no processing)'), ('linebreaks', 'Linebreaks'), ('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText')], default='markdown', max_length=255, verbose_name='markup')),
                ('body', inline_media.fields.TextFieldWithInlines()),
                ('body_markup', models.TextField(blank=True, null=True)),
                ('quote_author', models.CharField(help_text="quote's author", max_length=255)),
                ('url_source', models.URLField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'quote',
                'verbose_name_plural': 'quotes',
                'db_table': 'dress_blog_quotes',
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
            },
            bases=('dress_blog.post',),
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dress_blog.Post')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique_for_date='pub_date')),
                ('markup', django_markup.fields.MarkupField(choices=[('none', 'None (no processing)'), ('linebreaks', 'Linebreaks'), ('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText')], default='markdown', max_length=255, verbose_name='markup')),
                ('abstract', inline_media.fields.TextFieldWithInlines()),
                ('abstract_markup', models.TextField(blank=True, null=True)),
                ('body', inline_media.fields.TextFieldWithInlines()),
                ('body_markup', models.TextField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'story',
                'verbose_name_plural': 'stories',
                'db_table': 'dress_blog_stories',
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
            },
            bases=('dress_blog.post',),
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_post', to='contenttypes.ContentType', verbose_name='content type'),
        ),
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
    ]