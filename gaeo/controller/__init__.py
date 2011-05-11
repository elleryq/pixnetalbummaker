#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2008 GAEO Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""GAEO controller package
"""

import new
import os
import re
import logging

from google.appengine.ext.webapp import template

import gaeo
from gaeo.view import BaseView
import errors
import helper


class FlashObject(dict):

    """
    Used to show a flash message.
    """

    def __init__(self, session):
        dict.__init__(self)
        self.__session = session
        self.__init = True
        if session.has_key('flash') and isinstance(session['flash'],
                dict):
            self.update(session['flash'])
            del session['flash']
            session.put()
        self.__init = False

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if not self.__init:
            if not self.__session.has_key('flash'):
                self.__session['flash'] = dict()
            self.__session['flash'][key] = value
            self.__session.put()


class BaseController(object):

    """The BaseController is the base class of action controllers.
        Action controller handles the requests from clients.
    """

    def __init__(self, hnd, params={}):
        self.hnd = hnd
        self.response = hnd.response
        self.request = hnd.request
        self.params = params

        for k in self.request.arguments():
            self.params[k] = self.request.get_all(k)
            if len(self.params[k]) == 1:
                self.params[k] = self.params[k][0]

        self._controller = params['controller']
        self._action = params['action']
        self.has_rendered = False
        self.__config = gaeo.Config()

        self.__tpldir = os.path.join(self.__config.template_dir,
                self._controller)
        self._template_values = {}

        # implement parameter nesting as in rails

        self.params = self.__nested_params(self.params)

        # detect the mobile platform

        self._is_mobile = self.__detect_mobile()

        # alias the cookies

        self.cookies = self.request.cookies

        # create the session

        try:
            store = self.__config.session_store
            exec 'from gaeo.session.%s import %sSession' % (store,
                    store.capitalize())

            self.session = eval('%sSession' % store.capitalize())(hnd,
                    '%s_session' % self.__config.app_name)
            self.flash = FlashObject(self.session)
        except:
            raise errors.ControllerInitError('Initialize Session Error!'
                    )

        # add request method (get, post, head, put, ....)

        env = self.request.environ
        self._request_method = env.get('REQUEST_METHOD').lower()

        # tell if an ajax call (X-Request)

        self._is_xhr = env.has_key('HTTP_X_REQUESTED_WITH')\
             and env.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

        # add helpers

        helpers = dir(helper)
        for h in helpers:
            if not re.match('^__', h):
                self.__dict__[h] = new.instancemethod(eval('helper.%s'
                         % h), self, BaseController)

        # view object

        self.view = BaseView(self)

    def before_action(self):
        pass

    def after_action(self):
        pass

    def invalid_action(self):
        """ If the router went to an invalid action """

        self.hnd.error(404)
        self.render(text='Invalid action')

    def from_json(self, json):
        """ Convert a JSON string to python object """

        from django.utils import simplejson
        return simplejson.loads(json)

    def to_json(self, obj):
        """ Convert a dict/list to JSON. Use simplejson """

        from django.utils import simplejson
        return simplejson.dumps(obj)

    def render(self, *html, **opt):
        hdrs = {}

        content_type = 'text/html; charset=utf-8'

        if html:
            content = ''.join(html).decode('utf-8')
        elif opt:

            # if the expires header is set

            if opt.has_key('expires'):
                hdrs['Expires'] = opt.get('expires')

            if opt.has_key('html'):
                content = opt.get('html').decode('utf-8')
            elif opt.has_key('text'):
                content_type = 'text/plain; charset=utf-8'
                content = str(opt.get('text')).decode('utf-8')
            elif opt.has_key('json'):
                content_type = 'application/json; charset=utf-8'
                content = opt.get('json').decode('utf-8')
            elif opt.has_key('xml'):
                content_type = 'text/xml; charset=utf-8'
                content = opt.get('xml').decode('utf-8')
            elif opt.has_key('script'):
                content_type = 'text/javascript; charset=utf-8'
                content = opt.get('script').decode('utf-8')
            elif opt.has_key('template'):
                context = self.__dict__
                if isinstance(opt.get('values'), dict):
                    context.update(opt.get('values'))

                try:
                    import gettext
                    from gaeo import Config
                    conf = Config()

                    # FIXME: get browser locale or user-specified locale

                    cur_locale = ['en']

                    lang = gettext.translation('%s_%s'
                             % (self._controller, self._action),
                            conf.messages_dir, cur_locale)

                    for item in context.keys():

                        # FIXME: does it make sense?

                        if isinstance(context.get(item), basestring):
                            context[item] = lang.gettext(context[item])
                except:

                    # do nothing if fails in translation

                    pass

                content = template.render(os.path.join(self.__tpldir,
                        opt.get('template') + '.html'), context)
            elif opt.has_key('template_string'):
                context = self.__dict__
                if isinstance(opt.get('values'), dict):
                    context.update(opt.get('values'))
                from django.template import Context, Template
                t = Template(opt.get('template_string').encode('utf-8'))
                c = Context(context)
                content = t.render(c)
            elif opt.has_key('image'):
                # for sending an image content
                import imghdr
                img_type = imghdr.what('ignored_filename',
                        opt.get('image'))
                content_type = 'image/' + img_type
                content = opt.get('image')
            elif opt.has_key('css'):
                # for css rendering
                content_type = 'text/css'
                content = opt.get('css')
            elif opt.has_key('file'):
                content_type = opt.get('content_type', 'application/octet-stream')
                if opt.has_key('filename'):
                    hdrs['Content-Disposition'] = 'attachment; filename=' + opt.get('filename')
                content = opt.get('file')
            else:
                raise errors.ControllerRenderTypeError('Render type error'
                        )

        hdrs['Content-Type'] = content_type
        hdrs.update(opt.get('hdr', {}))

        self.view.render(content, hdrs)
        self.has_rendered = True

    def redirect(self, url, perm=False):
        self.has_rendered = True  # dirty hack, make gaeo don't find the template
        self.hnd.redirect(url, perm)

    def respond_to(self, **blk):
        """ according to self.params['format'] to respond appropriate stuff
        """

        if self.params.has_key('format')\
             and blk.has_key(self.params['format']):
            logging.error(self.params['format'])
            blk[self.params['format']]()

    def __detect_mobile(self):
        h = self.request.headers
        ua = h.get('User-Agent', '').lower()

        # iphone

        if ua.find('iphone') > -1 or ua.find('ipod') > -1:
            self._is_iphone = True
            return True

        # android

        if ua.find('android') > -1:
            self._is_android = True
            return True

        # wap.wml

        ha = h.get('Accept')
        if ha and (ha.find('text/vnd.wap.wml') > -1
                    or ha.find('application/vnd.wap.xhtml+xml') > -1):
            return True

        wap_profile = h.get('X-Wap-Profile')
        profile = h.get('Profile')
        opera_mini = h.get('X-OperaMini-Features')
        ua_pixels = h.get('UA-pixels')

        if wap_profile or profile or opera_mini or ua_pixels:
            return True

        # FIXME: add common user agents

        common_uas = [
            'sony',
            'noki',
            'java',
            'midp',
            'benq',
            'wap-',
            'wapi',
            'mobi',
            'kddi',
            ]

        if ua and ua[0:4] in common_uas:
            return True

        return False

    # Helper methods for parameter nesting as in rails

    def __appender(
        self,
        dict,
        arr,
        val,
        ):
        if len(arr) > 1:
            try:
                dict[arr[0]]
            except KeyError:
                dict[arr[0]] = {}
            return {arr[0]: self.__appender(dict[arr[0]], arr[1:], val)}
        else:
            dict[arr[0]] = val
            return

    def __nested_params(self, prm):
        prm2 = {}
        for param in prm:
            parray = param.replace(']', '').split('[')
            if len(parray) == 1:
                parray = parray[0].split('-')
            self.__appender(prm2, parray, prm[param])
        return prm2


