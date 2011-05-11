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

"""GAEO model package
"""

import re
from google.appengine.ext import db, search


def pluralize(noun):
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeiou]y$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'


class BaseModel(db.Model):

    """BaseModel is the base class of data model."""

    @classmethod
    def belongs_to(
        cls,
        ref_cls,
        reference_name='',
        collection_name='',
        ):
        """ Declare a many-to-one relationship """

        if ref_cls is None:
            raise Exception('No referenced class')

        ref_name = reference_name or ref_cls.__name__.lower()
        if ref_name not in cls._properties:
            col_name = collection_name\
                 or pluralize(cls.__name__.lower())
            attr = db.ReferenceProperty(ref_cls,
                    collection_name=col_name)
            cls._properties[ref_name] = attr
            attr.__property_config__(cls, ref_name)

    def before_put(self):
        """
        called before put()
        """

        pass

    def after_put(self):
        """
        called after put()
        """

        pass

    def put(self):
        """
        Override the db.Model.put()
        """

        result = self.before_put()
        key = None
        if result is not False:
            key = super(BaseModel, self).put()
            self.after_put()
        return key

    def update_attributes(self, kwd_dict={}, **kwds):
        """Update the specified properties"""

        need_change = False

        # if user passed a dict, merge to kwds (Issue #3)

        if kwd_dict:
            kwd_dict.update(kwds)
            kwds = kwd_dict

        props = self.properties()
        for prop in props.values():
            if prop.name in kwds:
                if not need_change:
                    need_change = True
                prop.__set__(self, kwds[prop.name])

        if need_change:
            self.update()

    def set_attributes(self, kwd_dict={}, **kwds):
        """set the specified properties, but not update"""

        # Issue #3

        if kwd_dict:
            kwd_dict.update(kwds)
            kwds = kwd_dict

        props = self.properties()
        for prop in props.values():
            if prop.name in kwds:
                prop.__set__(self, kwds[prop.name])

    # alias method

    update = put

    def __getattr__(self, name):
        """
        Fix custom fields (e.g., ORM field) bug
        """

        if '_' + name in self.__dict__.keys():
            if isinstance(self.__dict__['_' + name], db.Key):

                # FIXME: import the model class by hand. use name convension here.

                key = self.__dict__['_' + name]
                exec 'from model.%s import %s' % (name,
                        name.capitalize())
                return eval("%s.get('%s')" % (name.capitalize(), key))
        else:
            raise AttributeError, name


class SearchableBaseModel(BaseModel, search.SearchableModel):

    """
    Make a searchable basemodel
    """

    pass


def belongs_to(klz, col_name=''):
    """
    create a many-to-one relation
    """

    if col_name:
        return db.Reference(klz, collection_name=col_name)
    else:
        return db.Reference(klz)


def named_query(order_by=None, **conds):
    """
    Create a named query.
    """

    cond_str = 'WHERE '
    for cond in conds.iterkeys():
        if len(cond_str) > 6:
            cond_str += ' AND '
        cond_str += '%s %s' % (cond, conds[cond])

    if order_by:
        cond_str += ' ORDER BY %s' % order_by

    return property(lambda self: cls.gql(cond_str))


