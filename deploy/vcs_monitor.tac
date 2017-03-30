

"""

TAC Deployment Example
----------------------

A more usable example.

The important part of this, the part that makes it a .tac file, is
the final root-level section, which sets up the object called
'application' which twistd will look for.

You can run this .tac file directly with ::

    twistd -ny vcs_monitor.tac

"""

# import sys
# from twisted.python import log
# log.startLogging(sys.stdout)

from twisted.application import service
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import LogFile


# this is the core part of any tac file, the creation of the root-level
# application object
application = service.Application("Tendril VCS Monitor")
logfile = LogFile("vcs_monitor.log", "/var/log/tendril")
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)


# attach the service to its parent application
from vcs_monitor import worker
worker.start()
