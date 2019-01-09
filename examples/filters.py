# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot
from vbio.servers import FlaskServer

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(secret='<секретный ключ>',
            confirmation='<строка, которую должен вернуть сервер>',
            api=api)
server = FlaskServer(bot, port=80)


# Будет вызываться только если текст сообщения подходит
# под регулярное выражение
@bot.callback_message_handler(regexp=r'[0-9]+')
def regexp(m):
    m.answer(message='Вы ввели число!')


# Будет вызываться если сообщения содержит все
# типы вложений из переданного списка
@bot.callback_message_handler(content_type=['photo', 'text'])
def content_type(m):
    m.answer(message='Вы отправили фото и текст!')


# Будет вызываться если функция func вернет True
@bot.callback_message_handler(func=lambda m: m.text == m.text[::-1])
def func(m):
    m.answer(message='Вы ввели палиндром!')


# Вызывается, если текст сообщения равен text
@bot.callback_message_handler(text='помощь')
def text(m):
    m.answer(message='Вы отправили текст "помощь"!')


# Вызывается, если поле "command" из m.payload сообщения равна
# command
@bot.callback_message_handler(command='start')
def command(m):
    m.answer(message='Вы нажали кнопку "Начать"!')


# Вызывается, если m.payload равно payload
@bot.callback_message_handler(payload={'123': 456})
def payload(m):
    m.answer(message='Вы отправили сообщение с payload {"123": 456}')


if __name__ == '__main__':
    server.run()
