#-*- coding: utf-8 -*-

from django.conf import settings as _settings

def settings(request):
    return { 'settings': _settings }
