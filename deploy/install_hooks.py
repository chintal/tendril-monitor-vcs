#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2017 Chintalagiri Shashank
#
# This file is part of tendril-monitor-vcs.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Install post commit hooks on all known repositories.
"""

import os
from checkoutmanager import config
from checkoutmanager.runner import CONFIGFILE_NAME

try:
    from tendril.utils.config import SVN_SERVER_ROOT
    from tendril.utils.config import SVN_ROOT
except ImportError:
    # TODO Deal with this issue.
    SVN_SERVER_ROOT = '/home/svnrepo'
    SVN_ROOT = '/home/tendril/quazar/svn'

from vcs_monitor import hook_post_commit


def get_repopath(wcpath):
    # TODO Figure out what to do if a subfolder of a repository is to be used
    wcpath = os.path.relpath(wcpath, SVN_ROOT)
    return os.path.join(SVN_SERVER_ROOT, wcpath)


if __name__ == '__main__':
    hp_pc_svn = hook_post_commit.__file__
    conf = config.Config(os.path.expanduser(CONFIGFILE_NAME))
    for dirinfo in conf.directories(group=None):
        if dirinfo.vcs == 'svn':
            wc = dirinfo.directory
            repodir = get_repopath(wc)
            hook_path = os.path.join(repodir, 'hooks', 'post-commit')
            if os.path.exists(hook_path):
                if os.path.islink(hook_path):
                    os.remove(hook_path)
                else:
                    os.rename(hook_path, hook_path + '.bak')
            os.symlink(hp_pc_svn, hook_path)
