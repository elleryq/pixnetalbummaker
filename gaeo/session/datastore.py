#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import pickle
import logging
import datetime

from google.appengine.ext import db

from gaeo import session

SESSION_DURATION = datetime.timedelta(hours=1)


class SessionStore(db.Model):

    id = db.StringProperty()
    value = db.BlobProperty()
    expires = db.DateTimeProperty()

    @classmethod
    def clear(cls):
        lst = cls.gql('WHERE expires < :1',
                      datetime.datetime.now()).fetch(1000)
        for item in lst:
            item.delete()


class DatastoreSession(session.Session):

    """ session that uses the datastore """

    def __init__(
        self,
        hnd,
        name='gaeo_session',
        timeout=60 * 60,
        ):
        super(DatastoreSession, self).__init__(hnd, name, timeout)

        SessionStore.clear()

        # check from cookie

        if name in hnd.request.cookies:
            self._id = hnd.request.cookies[name]
            res = SessionStore.gql('WHERE id = :1', self._id).get()
            if res:
                self._store = res
                session_data = self._store.value
                if session_data:
                    self.update(pickle.loads(session_data))
            else:
                self._create_store(self._id)
        else:

                # not in the cookie, set it

            cookie = '%s=%s' % (name, self._id)
            hnd.response.headers.add_header('Set-Cookie', cookie)
            self._create_store(self._id)

    def put(self):
        if not self._invalidated and self._store:
            self._store.value = pickle.dumps(self.copy())
            self._store.expires = datetime.datetime.now()\
                 + SESSION_DURATION
            self._store.put()

    def invalidate(self):
        """Invalidates the session data"""

        self._hnd.response.headers.add_header('Set-Cookie',
                '%s=; expires=Thu, 1-Jan-1970 00:00:00 GMT;'
                 % self._name)
        self._store.delete()
        self._store = None
        self.clear()
        self._invalidated = True

    def _create_store(self, id):
        self._store = SessionStore(id=id, value=pickle.dumps(dict()),
                                   expires=datetime.datetime.now()
                                    + SESSION_DURATION)
        self._store.put()
        self._id = id


