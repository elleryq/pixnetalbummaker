# Create your views here.
from google.appengine.api import conf
from django.template import Context, loader
from django.http import HttpResponse
from django.shortcuts import render_to_response

def index( request ):
    v={}
    app_version, current_config_version, development = conf._inspect_environment()
    v['development']=development
    return render_to_response('home/index.html', v )

