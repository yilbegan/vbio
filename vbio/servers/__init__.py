# -*- encoding: utf-8 -*-

from vbio.servers.longpool import LongPoolClient
try:
    from vbio.servers.flask import FlaskServer
except ImportError:
    pass
