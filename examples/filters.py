# -*- coding: utf-8 -*-

import vk_requests
import re

from vbio import VkBot, LongPollClient

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(api=api)
handler = LongPollClient(bot)


# Будет вызываться только если текст сообщения подходит
# под регулярное выражение. Также можно использовать строку, если вам
# не нужно использовать флаги.
# В поле m.regex_ будет сохранён groupdict.
@bot.message_handler(regexp=re.compile('сумма (?P<first>[0-9]+) (?P<second>[0-9]+)', re.IGNORECASE))
def regexp(m):
    # USR: сумма 2 2
    # BOT: 2 + 2 = 4
    m.answer(message='{} + {} = {}'.format(
        m.regexp_['first'], m.regexp_['second'],
        int(m.regexp_['first']) + int(m.regexp_['second'])
    ))


# Будет вызываться если сообщения содержит все
# типы вложений из переданного списка
@bot.message_handler(content_type=['photo', 'text'])
def content_type(m):
    m.answer(message='Вы отправили фото и текст!')


# Будет вызываться если функция func вернет True
@bot.message_handler(func=lambda m: m.text.lower() == m.text.lower()[::-1])
def func(m):
    m.answer(message='Вы ввели палиндром!')


# Вызывается, если поле "command" из m.payload сообщения равна
# command
@bot.message_handler(command='start')
def command(m):
    m.answer(message='Вы нажали кнопку "Начать"!')


# Если True, то вызывается только если сообщение отправлено в конференции,
# иначе только если из личных сообщений
@bot.message_handler(from_chat=True)
def payload(m):
    m.answer(message='Вы отправили это сообщение из чата #%i' % (m.peer_id,))


# Кстати, можно комбинировать несколько фильтров.
# Например эта команда будет работать только в ЛС бота.
# А ещё она не будет регистронезависимой!
@bot.message_handler(regexp=r'умнож(ь|ить) (?P<first>[0-9]+) (?P<second>[0-9]+)', from_chat=False)
def mul(m):
    m.answer(
        message='{first} * {second} = {}'.format(
            int(m.regexp_['first']) * int(m.regexp_['second']),
            **m.regexp_
        )
    )


# Будет вызываться если в чат вошёл новый пользователь.
def greet(m):
    m.answer(
        message='В чате теперь новый пользователь!'
    )


# Можно задавать и так
bot.message_handler(action='chat_invite_user')(greet)
bot.message_handler(action='chat_invite_user_by_link')(greet)


if __name__ == '__main__':
    handler.run()
