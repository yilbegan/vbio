# -*- encoding: utf-8 -*-

from flask import Flask, request, abort
from vbio.bot import VkBot
from vbio.types import VkBotServer
from datetime import datetime

import traceback

__all__ = ('FlaskServer',)


class FlaskServer(VkBotServer):

    def __init__(self, bot: VkBot, host: str = '0.0.0.0', port: int = 5000):
        self.bot = bot
        self.host = host
        self.port = port
        self.app = None

    def run(self):
        self.app = Flask(__name__)

        @self.app.route('/', methods=['POST'])
        def message_handler():
            data = request.json

            if data is None:
                return abort(400)

            if data.get('secret', '') != self.bot.secret:
                return abort(403)

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
                    if self.bot.logger is not None:
                        self.bot.logger.error(
                            f'[X] {datetime.now().strftime("%d/%m/%y %H:%M:%S")} Error \n{traceback.format_exc()}\n'
                            f'caused during handling request: \n{data}\n-------------'
                        )
                    if not self.bot.ignore_errors:
                        raise e

            return 'ok'

        self.app.run(self.host, self.port, debug=False)
