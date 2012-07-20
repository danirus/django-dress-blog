from django.shortcuts import render_to_response as render
from django.template import RequestContext

from dress_blog.models import Config


def index(request):
    return render("index.html", context_instance=RequestContext(request))
