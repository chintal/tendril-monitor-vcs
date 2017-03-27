=============
Usage Example
=============

Basic Usage Example
-------------------

.. literalinclude:: ../deploy/runserver.py


Self-contained Usage : Deploy using twistd and systemd
------------------------------------------------------

Twisted ``.tac`` file:

.. literalinclude:: ../deploy/vcs_monitor.tac

Systemd ``.service`` file:

.. literalinclude:: ../deploy/tendril_vcs_monitor.service
s
