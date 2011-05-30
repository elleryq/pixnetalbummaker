#!/usr/bin/env python
# encoding: utf-8
"""
Modified from trunkly.py

Created by Yan-ren Tsai on 2011-05-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import httplib2
from urllib import urlencode
from urllib import quote # = PHP's rawurlencode()
import string, time, math, random
import base64
import hashlib
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import platform

if platform.python_version() >= '2.6.0':
    import json
else:
    import simplejson as json

def uniqid(prefix='', more_entropy=False):
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    if more_entropy:
        valid_chars = list(set(string.hexdigits.lower()))
        entropy_string = ''
        for i in range(0,10,1):
            entropy_string += random.choice(valid_chars)
        uniqid = uniqid + entropy_string
    uniqid = prefix + uniqid
    return uniqid

def hash_hmac( digest_str, data, key, raw_output=False ):
    import hmac
    digest_modules={'sha1': hashlib.sha1, 'md5': hashlib.md5}
    if not digest_modules.has_key( digest_str ):
        digest_str='md5'
    digest_module=digest_modules[digest_str]
    h=hmac.new(key, data, digest_module)
    if raw_output:
        r=h.digest()
    else:
        r=h.hexdigest()
    return r

def parse_str(s):
    try:
        from urlparse import parse_qs # python 2.6
    except ImportError:
        from cgi import parse_qs # python 2.5
    return parse_qs(s)

PIXNET_API_HTTP='http://emma.pixnet.cc'
         
HTTP_METHOD = ["GET", "POST", "PUT", "DELETE"]
                                                
class Pixnet:
    def __init__(self):
        pass

    def cmd(self, args):
        def execute(key=None, parameters=None, method="GET"):
            if not parameters:
                parameters = {}
            
            defaults = {}
            defaults.update(parameters)
            parameters = defaults

            url = PIXNET_API_HTTP

            p = False
            for arg in args:
                if arg.upper() in HTTP_METHOD:
                    method = arg.upper()
                    # print 'method %s' % method
                    continue

                if arg != '' and not p:
                    url += '/%s' % arg
                else:
                    if p:
                        #read parameters
                        if arg not in parameters:
                            raise Exception("Parameter '%s' is required." % arg)
                        url += '/%s' % parameters[arg]
                        del parameters[arg]
                        p = False
                    else:
                        p = True

            if key:
                url += '/%s' % key

            body = None
            param_encoded = urlencode(parameters)
            if len(param_encoded):
                url += '/'

            if method == "POST":
                body = param_encoded
                # headers['Content-Type'] = 'application/x-www-form-urlencoded'
            elif method == "GET":
                if key:
                    url = url[:-1]

                if len(param_encoded):
                    url += '?' + param_encoded

                #print 'url is %s ' % url
                # print 'body is %s ' % body
            http = httplib2.Http()
            resp, content = http.request(url, method=method, body=body)

            if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])
            return json.loads(content)

        return execute

    def __getattr__(self, attr):
        # if attr.startswith('_'):
        # raise Exception("'Trunkly' object has no attribute '_abc_'")
        # if attr.endswith('_'):
        # raise Exception("attr can't end with '_'")
        args = attr.split('_')
        return self.cmd(args)

class PixnetOAuth:
    """ 
    Reference:
    http://code.google.com/p/phppixnetapi/source/browse/trunk/PixAPI.php
    """

    REQUEST_TOKEN_URL='http://emma.pixnet.cc/oauth/request_token'
    ACCESS_TOKEN_URL='http://emma.pixnet.cc/oauth/access_token'
    AUTHORIZATION_URL='http://emma.pixnet.cc/oauth/authorize'

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self._request_callback_url = None
        self._request_expire = None
        self._token = None
        self._secret = None

    def set_token( self, token, secret ):
        self._token = token
        self._secret = secret

    def set_request_callback( self, callback_url ):
        self._request_callback_url = callback_url

    def _get_request_token(self):
        if self._request_expire and time.time()<self._request_expire:
            return

        if self._request_callback_url==None:
            message = self.http(self.REQUEST_TOKEN_URL)
        else:
            message = self.http(self.REQUEST_TOKEN_URL, {
                    'oauth_params': {
                        'oauth_callback': self._request_callback_url
                    } } )
        args = parse_str( message )
        self._token = args['oauth_token'][0]
        self._secret = args['oauth_token_secret'][0]
        self._request_expire = time.time()+float(args['oauth_expires_in'][0])
        self._request_auth_url = "%s?oauth_token=%s" % (
                self.AUTHORIZATION_URL, args['oauth_token'][0] )

    def get_auth_url( self, callback_url=None ):
        if callback_url!=self._request_callback_url:
            self._request_expire=None
            self._request_callback_url = callback_url
        self._get_request_token()
        return self._request_auth_url

    def get_access_token( self, verifier_token ):
        message = self.http( self.ACCESS_TOKEN_URL, {
                'oauth_params': {
                    'oauth_verifier': verifier_token
                } } )
        args = parse_str( message ) # TODO
        self._token = args['oauth_token']
        self._secret = args['oauth_token_secret']
        return (self._token, self._secret)

    def get_request_token_pair(self):
        self._get_request_token()
        return (self._token, self._secret)

    def http( self, url, options={} ):
        # oauth authentication
        oauth_args = {
            'oauth_version': '1.0',
            'oauth_nonce': hashlib.md5( uniqid() ).hexdigest(),
            'oauth_timestamp': int( time.time() ),
            'oauth_consumer_key': self.consumer_key,
            'oauth_signature_method': 'HMAC-SHA1'
        }
        if self._token:
            oauth_args['oauth_token']=self._token
       
        if options.has_key( 'oauth_params' ):
            oauth_args.update( options['oauth_params'] )

        parts = []
        if options.has_key( 'method' ):
            parts.append( options['method'].upper() )
        elif options.has_key( 'post_params' ) or options.has_key( 'files' ):
            parts.append( 'POST' )
        else:
            parts.append( 'GET' )

        if options.has_key( 'get_params' ) and options['get_params']:
            if url.rfind('?')!=-1:
                url = url + '&'
            else:
                url = url + '?'
            url = url + urlencode( options['get_params'] )
        parts.append( quote( url, '' ) )

        if options.has_key( 'get_params' ):
            for key, value in options['get_params'].iteritems():
                if not value:
                    del options['get_params'][key]

        if options.has_key( 'post_params' ):
            for key, value in options['post_params'].iteritems():
                if not value:
                    del options['post_params'][key]

        args = oauth_args.copy()
        if options.has_key( 'post_params' ):
            args.update( options['post_params'] )

        if options.has_key( 'get_params' ):
            args.update( options['get_params'] )

        args_part = []
        for key in sorted( args.keys() ):
            args_part.append( "%s=%s" % (
                        quote(key,''), quote(str(args[key]),'') ) )
        parts.append( quote( '&'.join( args_part ), '' ) )
        base_string='&'.join( parts )
       
        key_parts = [ quote( self.consumer_secret, '' ) ]
        if self._secret:
            key_parts.append( quote(self._secret, '') )
        else:
            key_parts.append( '' )

        key = '&'.join( key_parts )
        oauth_args['oauth_signature']=base64.encodestring( 
            hash_hmac( 'sha1', base_string, key, True) )[:-1]

        oauth_header = 'OAuth '
        first = True
        for k in oauth_args.keys():
            if not k.startswith( 'oauth' ):
                continue
            if not first:
                oauth_header=oauth_header+','
            v = str(oauth_args[k])
            oauth_header=oauth_header+quote(k, '')+'="'+quote(v, '')+'"'
            first=False

        if options.has_key( 'method' ):
            method = options['method'].upper()
        elif options.has_key( 'post_params' ) or options.has_key('files'):
            method = "POST"
        else:
            method = "GET"

        header = {'Authorization': oauth_header }
        body=""
        if options.has_key('post_params'):
            body = urlencode( options['post_params'] )
        if options.has_key('files'):
            raise Exception("Not implemented.")
        http = httplib2.Http()
        resp, content = http.request(
                url, 
                method=method, 
                body=body,
                headers=header )

        if resp['status'] != '200':
            raise Exception("Invalid response %s. body=%s" % (
                        resp['status'],
                        content ) )
        return content

