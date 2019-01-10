# -*- coding: utf-8 -*-

import requests
import traceback

from vbio.bot import VkBot
from vbio.types import VkBotServer
from datetime import datetime

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

                    else:
                        self.bot.process_request(update['object'])
                except Exception as e:
                    if self.bot.logger is not None:
                        self.bot.logger.error(
                            '[X] {} Error \n{}\ncaused during handling event: '
                            '\n{}\n-------------'.format(
                                datetime.now().strftime("%d/%m/%y %H:%M:%S"),
                                traceback.format_exc(),
                                update
                            )
                        )

                    if not self.bot.ignore_errors:
                        raise e
