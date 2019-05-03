# -*- encoding: utf-8 -*-

from vbio.handlers.longpoll import LongPollClient
try:
    from vbio.handlers.flask import FlaskServer
except ImportError:
    pass
