# -*- coding: utf-8 -*-

from vbio.bot import VkBot
from vbio.types import VkBotServer

import cherrypy

__all__ = ('CherryPyServer',)


class CherryPyServer(VkBotServer):

    def __init__(self, bot: VkBot, host: str = '0.0.0.0', port: int = 5000):
        self.bot = bot
        self.host = host
        self.port = port

    def run(self):

        class Handler:

            @classmethod
            @cherrypy.expose
            @cherrypy.tools.json_in()
            def index(cls):
                data = cherrypy.request.json

                if not data:
                    raise cherrypy.HTTPError(status=400)

                if data.get('secret', '') != self.bot.secret:
                    raise cherrypy.HTTPError(status=403)

                if data.get('type') == 'confirmation':
                    return self.bot.confirmation

                elif data.get('type') == 'message_new':
                    try:
                        self.bot.process_message(data['object'])
                    except Exception as e:
                        if not self.bot.ignore_errors:
                            raise e

                else:
                    try:
                        self.bot.process_request(data)
                    except Exception as e:
                        if not self.bot.ignore_errors:
                            raise e

                return 'ok'

        cherrypy.config.update({
            'server.socket_port': self.port,
            'server.socket_host': self.host
        })

        cherrypy.quickstart(Handler(), '/', )