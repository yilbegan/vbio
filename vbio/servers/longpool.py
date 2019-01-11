# -*- coding: utf-8 -*-

import requests
import sys

from vbio.bot import VkBot
from vbio.types import VkBotServer

__all__ = ('LongPoolClient',)


class LongPoolClient(VkBotServer):

    def __init__(self, bot: VkBot, wait: int = 25):
        self.group_id = bot.api.groups.getById()[0]['id']

        self.bot = bot
        self.wait = wait
        self.session = requests.Session()

    def run(self):
        pool = self.bot.api.groups.getLongPollServer(group_id=self.group_id)

        url = pool['server']
        params = {
            'act': 'a_check',
            'wait': self.wait,
            'key': pool['key'],
            'ts': pool['ts'],
        }

        self.bot.logger.info('Pooling started!')

        while True:
            event = self.session.get(
                url=url,
                params=params,
                timeout=self.wait + 10
            ).json()

            params['ts'] = event['ts']

            for update in event['updates']:
                try:
                    if update['type'] == 'message_new':
                        self.bot.process_message(update['object'])
                        self.bot.logger.info('Processed message from {}: {}'.format(update['object'].get('from_id'),
                                                                                    update['object'].get('text')))

                    else:
                        self.bot.process_request(update['object'])
                        self.bot.logger.info('Processed request: {}'.format(update['type']))

                except Exception as e:
                    self.bot.logger.error('From {}'.format(update['type']), exc_info=sys.exc_info())
                    if not self.bot.ignore_errors:
                        raise e
