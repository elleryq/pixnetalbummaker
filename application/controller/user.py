import cgi
from google.appengine.ext import db
from gaeo.controller import BaseController
from pixnetlib import PixnetOAuth

consumer_key = "194f65eab45b79a186f47655376934f5"
consumer_secret = "4b4f6368334e2add978c9231f176479d"
api = PixnetOAuth( consumer_key, consumer_secret )

class UserController(BaseController):
    def authorized(self):
        request_token=None
        request_token_=None
        verifier_token=None
        if self.params.has_key( "request_token" ):
            request_token=self.params['request_token']
        if self.session.has_key( "request_token_" ):
            request_token_=self.session['request_token_']
        if self.params.has_key( "verifier_token" ):
            verifier_token=self.params['verifier_token']
        if not request_token or not request_token_ or not verifier_token:
            return # TODO
        api.set_token( request_token, request_token_+request_token )
        access_token, access_token_secret = api.get_access_token(
                verifier_token )
        self.session['access_token']=access_token
        self.session['access_token_secret']=access_token_secret
        self.session['access_token'].put()
        self.session['access_token_secret'].put()

