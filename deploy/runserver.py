#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2015 Chintalagiri Shashank
# Released under the MIT license.

"""

Simple Deployment Example
-------------------------

"""

from vcs_monitor import worker
from twisted.internet import reactor

import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    worker.start()
    reactor.run()
