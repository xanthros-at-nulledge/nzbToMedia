# -*- coding: utf-8 -*-
# This file is part of beets.
# Copyright 2016, Blemjhoo Tezoulbr <baobab@heresiarch.info>.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Moves patterns in path formats (suitable for moving articles)."""

from __future__ import division, absolute_import, print_function

import re
from beets.plugins import BeetsPlugin

__author__ = 'baobab@heresiarch.info'
__version__ = '1.1'

PATTERN_THE = u'^[the]{3}\s'
PATTERN_A = u'^[a][n]?\s'
FORMAT = u'{0}, {1}'


class ThePlugin(BeetsPlugin):

    patterns = []

    def __init__(self):
        super(ThePlugin, self).__init__()

        self.template_funcs['the'] = self.the_template_func

        self.config.add({
            'the': True,
            'a': True,
            'format': u'{0}, {1}',
            'strip': False,
            'patterns': [],
        })

        self.patterns = self.config['patterns'].as_str_seq()
        for p in self.patterns:
            if p:
                try:
                    re.compile(p)
                except re.error:
                    self._log.error(u'invalid pattern: {0}', p)
                else:
                    if not (p.startswith('^') or p.endswith('$')):
                        self._log.warn(u'warning: \"{0}\" will not '
                                       u'match string start/end', p)
        if self.config['a']:
            self.patterns = [PATTERN_A] + self.patterns
        if self.config['the']:
            self.patterns = [PATTERN_THE] + self.patterns
        if not self.patterns:
            self._log.warn(u'no patterns defined!')

    def unthe(self, text, pattern):
        """Moves pattern in the path format string or strips it

        text -- text to handle
        pattern -- regexp pattern (case ignore is already on)
        strip -- if True, pattern will be removed
        """
        if text:
            r = re.compile(pattern, flags=re.IGNORECASE)
            try:
                t = r.findall(text)[0]
            except IndexError:
                return text
            else:
                r = re.sub(r, '', text).strip()
                if self.config['strip']:
                    return r
                else:
                    fmt = self.config['format'].get(unicode)
                    return fmt.format(r, t.strip()).strip()
        else:
            return u''

    def the_template_func(self, text):
        if not self.patterns:
            return text
        if text:
            for p in self.patterns:
                r = self.unthe(text, p)
                if r != text:
                    break
            self._log.debug(u'\"{0}\" -> \"{1}\"', text, r)
            return r
        else:
            return u''
