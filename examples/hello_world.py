# -*- coding: utf-8 -*-

# Можно использовать другие обертки для API,
# например vk_api.
import vk_requests

from vbio import VkBot
from vbio.servers import LongPoolClient

# Получаем обертку на API
api = vk_requests.create_api(service_token='<токен группы>')

bot = VkBot(api=api)

# LongPool клиент
server = LongPoolClient(bot)


# Задаем функцию которая будет получать сообщения.
# Если фильтры не указаны - будет получать все сообщения.
@bot.message_handler()
def hello_world(m):
    # Отвечаем на сообщение.
    # Аналогично api.messages.send(peer_id=m.from_id, message='Привет мир!')
    # и bot.answer_message(m, message='Привет мир!')
    m.answer(message='Привет мир!')


if __name__ == '__main__':
    # Запускаем сервер
    server.run()
