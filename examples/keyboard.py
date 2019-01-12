# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot
from vbio.servers import LongPoolClient
from vbio.types import VkKeyboardMarkup, VkKeyboardButton, VkColor

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(api=api)
server = LongPoolClient(bot)


@bot.message_handler()
def no_command(m):
    # Разметка клавиатуры
    # stack_size указывает максимальное кол-во кнопок в ряду;
    # используется методом VkKeyboardMarkup.
    keyboard = VkKeyboardMarkup(stack_size=2)

    # Добавить ряд с одной кнопкой
    keyboard.add(VkKeyboardButton(
        label='Нажми меня!',
        color=VkColor.POSITIVE,
        payload={'command': 'first_button'}
    ))

    # Добавить ряд из нескольких кнопок (максимум 4)
    keyboard.row(
        VkKeyboardButton('Кнопка #1 из второго ряда!',
                         color='default',  # Можно использовать как VkColor так и текст
                         payload={'command': 'second_button'}),
        VkKeyboardButton('Кнопка #2 из второго ряда!',
                         color='primary',
                         payload={'command': 'second_button'}),
    )

    # VkKeyboardMarkup.stack() будет добавлять кнопку на текущую строку или
    # автоматически переносить на следующую, если число кнопок на строке достигло
    # лимита stack_size
    for i in range(3):
        b = VkKeyboardButton('Кнопка #3!',
                             color=VkColor.NEGATIVE,
                             payload={'command': 'third_button'})
        keyboard.stack(b)  # Можно добавить кнопку так

    # Чтобы сериализовать клавиатуру вызовите ее снова: keyboard()
    # keyboard работать не будет!
    m.answer(message='Тест клавиатуры!\n'
                     'Payload вашего сообщения: {}'.format(m.payload),
             keyboard=keyboard())


if __name__ == '__main__':
    server.run()
