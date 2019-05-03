# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot, FlaskServer

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(api=api)
handler = FlaskServer(bot, secret='<секретный ключ>',
                      confirmation='<строка, которую должен вернуть сервер>')


@bot.message_handler()
def hello_world(m):
    m.answer(message='Привет мир!')


if __name__ == '__main__':
    handler.run(port=80)
