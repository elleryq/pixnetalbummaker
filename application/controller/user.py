import cgi
from google.appengine.ext import db
from gaeo.controller import BaseController
from pixnetlib import PixnetOAuth

consumer_key = "a3624580e7bd70630f7c660631b95484"
consumer_secret = "8cef9391b9518678e4b7c515f68f425e"
api = PixnetOAuth( consumer_key, consumer_secret )

class UserController(BaseController):
    def authorized(self):
        request_token=None
        request_token_=None
        verifier_token=None
        if self.params.has_key( "oauth_verifier" ):
            verifier_token=self.params['oauth_verifier']
        if not verifier_token:
            self.message="verifier_token is None"
        else:
            access_token, access_token_secret = api.get_access_token(
                    verifier_token )
            self.session['access_token']=access_token
            self.session['access_token_secret']=access_token_secret
            self.session['access_token'].put()
            self.session['access_token_secret'].put()
            self.message="Authorized."

