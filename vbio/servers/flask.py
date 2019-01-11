# -*- encoding: utf-8 -*-

import sys
import logging

from flask import Flask, request, abort
from vbio.bot import VkBot
from vbio.types import VkBotServer

__all__ = ('FlaskServer',)


class FlaskServer(VkBotServer):

    def __init__(self, bot: VkBot, secret: str, confirmation: str, app: Flask = None):

        self.bot = bot
        self.secret = secret
        self.confirmation = confirmation

        self.app = app or Flask(__name__)

    def message_handler(self):
        data = request.json

        if data is None:
            return abort(400)

        if data.get('secret', '') != self.secret:
            self.bot.logger.warning('Invalid secret passed!')
            return abort(403)

        if data.get('type') == 'confirmation':
            self.bot.logger.info('Confirmation sent')
            return self.confirmation

        try:
            if data.get('type') == 'message_new':
                self.bot.process_message(data['object'])
                self.bot.logger.info('Processed message from {}: {}'.format(data['object'].get('from_id'),
                                                                            data['object'].get('text')[:40]))

            else:
                self.bot.process_request(data)
                self.bot.logger.info('Processed request: {}'.format(data.get('type')))

        except Exception as ex:
            self.bot.logger.error('From {}'.format(data.get('type')), exc_info=sys.exc_info())
            if not self.bot.ignore_errors:
                raise ex

        return 'ok'

    def run(self, path: str = '/', *args, **kwargs):
        self.app.route(path, methods=['POST'])(
            self.message_handler
        )

        logging.getLogger('werkzeug').setLevel(logging.FATAL)
        self.bot.logger.info('starting webhook')
        self.app.run(*args, **kwargs)
