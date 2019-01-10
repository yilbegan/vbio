# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot
from vbio.servers import LongPoolClient

# Токен должен иметь доступ к управлению группой!
api = vk_requests.create_api(service_token='<токен группы>')

bot = VkBot(api=api)
long_pool = LongPoolClient(bot)


@bot.callback_message_handler()
def hello_world(m):
    m.answer(message='Привет мир!')


if __name__ == '__main__':
    long_pool.run()
