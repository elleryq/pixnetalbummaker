#!/usr/bin/env python
# encoding: utf-8
"""
Modified from trunkly.py

Created by Yan-ren Tsai on 2011-05-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import httplib2
from urllib import urlencode
from google.appengine.api.memcache import Client
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import platform
    
if platform.python_version() >= '2.6.0':
    import json
else:
    import simplejson as json

PIXNET_API_HTTP='http://emma.pixnet.cc'
         
HTTP_METHOD = ["GET", "POST", "PUT", "DELETE"]
                                                
mem = Client()

class Pixnet:
    def __init__(self):
        pass

    def cmd(self, args):
        def execute(parameters=None, method="GET"):
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

            body = None
            param_encoded = urlencode(parameters)
            if len(param_encoded):
                url += '/'

            if method == "POST":
                body = param_encoded
                # headers['Content-Type'] = 'application/x-www-form-urlencoded'
            elif method == "GET":
                if len(param_encoded):
                    url += '?' + param_encoded

                print 'url is %s ' % url
                # print 'body is %s ' % body
            http = httplib2.Http(mem)
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
