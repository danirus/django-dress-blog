# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 14:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('dress_blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='site',
        ),
        migrations.AddField(
            model_name='post',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
        ),
    ]
