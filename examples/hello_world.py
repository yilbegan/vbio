# -*- coding: utf-8 -*-

# Можно использовать другие обертки для API,
# например vk_api.
import vk_requests

from vbio import VkBot
from vbio.servers import FlaskServer

# Получаем обертку на API
api = vk_requests.create_api(service_token='<токен группы>')

bot = VkBot(secret='<секретный ключ>',
            confirmation='<строка, которую должен вернуть сервер>',
            api=api)

# Сервер, который будет обрабатывать запросы
server = FlaskServer(bot, port=80)


# Задаем функцию которая будет получать сообщения.
# Если фильтры не указаны - будет получать все сообщения.
@bot.callback_message_handler()
def hello_world(m):
    # Отвечаем на сообщение.
    # Аналогично api.messages.send(peer_id=m.from_id, message='Привет мир!')
    # и bot.answer_message(m, message='Привет мир!')
    m.answer(message='Привет мир!')


if __name__ == '__main__':
    # Запускаем сервер
    server.run()
