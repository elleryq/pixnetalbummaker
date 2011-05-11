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

""" GAEO View package """

import os
from gaeo import Config


class BaseView(object):

    def __init__(self, controller, **args):
        self.__config = Config()
        self.__controller = controller

        # detect if the view object has rendered

        self.rendered = False

        # set the template's directory

        self.__tpldir = os.path.join(self.__config.template_dir,
                controller.params['controller'])

    def render(
        self,
        content,
        hdrs={},
        **opts
        ):
        nothing = opts.get('nothing', False)
        if not nothing:
            r = self.__controller.response
            if hdrs:
                for (k, v) in hdrs.items():
                    r.headers[k] = v
            r.out.write(content)

        self.rendered = True


