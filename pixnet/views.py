# Create your views here.
from django.template import Context, loader
from django.http import HttpResponse
from pixnet.models import Consumer
from django.shortcuts import render_to_response

try:
    from pixnet.pixnetlib import PixnetOAuth
    consumer = Consumer.objects.get(version='1')
    api = PixnetOAuth( consumer.key, consumer.secret )
except:
    api = None

def index( request ):
    output = '<p>%s</p><p>%s</p>' % (consumer.key, consumer.secret)
    return HttpResponse( output )

def authorized(request, oauth_verifier):
    v={}
    verifier_token=None
    if oauth_verifier:
        verifier_token=oauth_verifier
    if not verifier_token:
        v['message']="verifier_token is None"
    else:
        access_token, access_token_secret = api.get_access_token(
                verifier_token )
        request.session['access_token']=access_token
        request.session['access_token_secret']=access_token_secret
        v['message']="Authorized."
    return render_to_response('pixnet/authorized.html', v )

def authorize(request):
    return render_to_response('pixnet/authorize.html', {
            'auth_url': api.get_auth_url()
            } )

