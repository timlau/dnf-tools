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

from __future__ import print_function

import sys
import os.path
here = sys.path[0]
if here != '/usr/bin':
    # git checkout
    toplevel = os.path.dirname(here)
    sys.path[0] = toplevel

from dnftools import _, logger, ToolBase
from dnf.cli.output import Output

class TestTool(ToolBase):
    name = "Test-tool"  # set in child class
    version = "1.0.0"
    decription = "simple test tool"

    def __init__(self):
        super(TestTool, self).__init__()

    def config(self,parser):
        self.output = Output(self.base) # borrow the dnf cli Output class (not public API)
        """ Add tool specific command line options """
        parser.add_argument("--search", dest="search", \
                           default=None, metavar='[key]',
                           help=_("search for a package marching [key]"))

    def run(self):
        """ Do the real tool action here """
        logger.info('\n%s - %s \n', TestTool.name, TestTool.version)
        if self.args.search:
            logger.info(_("Search for packages matching : %s \n"),self.args.search)
            # setup the dnf cache dir
            self.setup_cache()
            # read the repo config files
            self.base.read_all_repos()
            # Setup the repo download callbacks
            (bar, self.base.ds_callback) = self.output.setup_progress_callbacks()
            self.base.repos.all().set_progress_bar(bar)
            # fill the dnf sack
            self.base.fill_sack()
            # find the packages matching
            query = self.base.sack.query()
            result = query.available().filter(name=self.args.search)
            print()
            self.output.listPkgs(result,_('Packages Found'), 'list')
        else:
            logger.info(_("You must specify something to search for"))
        logger.info("\n")
if __name__ == "__main__":
    tool = TestTool()
