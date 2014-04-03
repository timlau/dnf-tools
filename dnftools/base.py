# -*- coding: utf-8 -*-
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from __future__ import absolute_import

import argparse
import logging

import dnf

# needed for setup_cache
import dnf.conf
import dnf.yum.parser
import dnf.const

import gettext

gettext.bindtextdomain('dnftools')
gettext.textdomain('dnftools')
_ = gettext.gettext
P_ = gettext.ngettext
logger = logging.getLogger('dnftools')


class ToolBase(object):
    """ Tool base class, use it as parent class for all tools"""

    name = "<invalid>"  # set in child class
    version = "1.0.0"
    decription = "Tell what the tool does"

    def __init__(self):
        self._base = dnf.Base()
        self.args = None # :api
        self._config()
        self._run()

    @property
    def base(self):  # :api
        """ returns a dnf.Base"""
        return self._base

    def _config(self):
        # do some common setup and call child class configure
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-d', '--debug', action='store_true', \
                                 help=_("run in debug mode"))
        self.parser.add_argument("-c", "--config", dest="conffile", \
                           default=None, metavar='[config file]',
                           help=_("dnf config file location"))
        self.parser.add_argument("--setopt", dest="setopts", default=[], \
                           action="append",
                           help=_("set arbitrary dnf config and repo options"))
        self.config(self.parser)
        self.args = self.parser.parse_args()
        if self.args.debug:
            self.setup_logging(logfmt = "%(asctime)s: %(message)s",loglvl=logging.DEBUG)
            # setup log handler for dnf API
            self.setup_logging(logroot='dnf', logfmt = "%(asctime)s: [%(name)s] - %(message)s",loglvl=logging.DEBUG)
        else:
            self.setup_logging(logroot='dnf', logfmt = "%(message)s",loglvl=logging.INFO)
            self.setup_logging()
        logger.debug("command line : %s " % repr(self.args))
        if self.args.setopts:
            for line in self.args.setopts:
                if '=' in line:
                    option,value = line.split('=')
                    if hasattr(self.base.conf,option):
                        logger.debug(" Setting option: %s = %s" %(option,value))
                        setattr(self.base.conf, option, value)


    def _run(self):
        self.run() # call the child run method

    def setup_logging(self, logroot='dnftools', logfmt='%(message)s', loglvl=logging.INFO):
        ''' Setup Python logging '''
        logger = logging.getLogger(logroot)
        logger.setLevel(loglvl)
        formatter = logging.Formatter(logfmt, "%H:%M:%S")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.propagate = False
        logger.addHandler(handler)

    def setup_cache(self): # :api
        # this should properly go away in the future, when the dnf cache setup, is made better
        self.base.conf.releasever = None # We want the current release
        # This is not public dnf API, but we want the same cache as dnf cli
        suffix = dnf.yum.parser.varReplace(dnf.const.CACHEDIR_SUFFIX, self.base.conf.yumvar)
        cli_cache = dnf.conf.CliCache(self.base.conf.cachedir, suffix)
        self.base.conf.cachedir = cli_cache.cachedir


    def config(self, parser):  # :api
        """
        config method, overload in subclass

        :param parser: ArgumentParser, to add the tools commandline options
        """
        pass

    def run(self):  # :api
        """
        run method, overload in subclass
        """
        pass

