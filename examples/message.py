# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot
from vbio.servers import FlaskServer

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(secret='<секретный ключ>',
            confirmation='<строка, которую должен вернуть сервер>',
            api=api)
server = FlaskServer(bot, port=80)


@bot.callback_message_handler()
def new_message(m):
    # m - объект сообщения
    # https://vk.com/dev/objects/message

    # Доступ к атрибутам:
    text_1 = m.text
    # или
    text_2 = m['text']
    # или
    text_3 = m.data['text']

    assert text_1 == text_2 == text_3

    # Проверка на наличие атрибута
    if 'text' in m:
        text_in_m = True
    else:
        text_in_m = False

    # Цикл по списку атрибутов
    attributes = []
    for a in m:
        attributes.append(a)

    # Является ли сообщением из чата
    if m.from_chat:
        from_chat = True
    else:
        from_chat = False

    # get как у словарей
    foo = m.get('foo', 'bar')

    # В строку
    string = str(m)

    # Ответить на сообщение
    m.answer(
        message='m.text: {}\n'
                'm["text"]: {}\n'
                'm.data["text"]: {}\n'
                '"text" in m: {}\n'
                'Атрибуты: {}\n'
                'Из чата: {}\n'
                'm.get("foo", "bar"): {}\n'
                'Как строка: {}'.format(
                                        text_1, text_2, text_3, text_in_m,
                                        ' '.join(attributes), from_chat,
                                        foo, string
                                        )
    )

if __name__ == '__main__':
    server.run()
