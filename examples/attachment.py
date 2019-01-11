# -*- coding: utf-8 -*-

import vk_requests

from vbio import VkBot
from vbio.servers import LongPoolClient

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(api=api)
server = LongPoolClient(bot)


@bot.callback_message_handler()
def photo(m):
    # Ищем фото
    for attachment in m.attachments:
        if attachment.type == 'photo':
            break
    else:
        m.answer(message='Приложи фото!')
        return

    # Получение атрибутов аналогично сообщению:
    owner_1 = attachment.owner
    # или
    owner_2 = attachment['owner']

    assert owner_1 == owner_2

    # Размер есть только у фото
    size = attachment.size

    # Преобразовать в формат <тип><владелец>_<id>_<access_key>
    as_attachment = attachment.to_attachment

    # Скачать (не все типы вложений можно скачать)
    raw = attachment.download()

    # Также можно:
    #
    # attachment.download(open('photo.jpg', 'wb'))
    #
    # out = io.BytesIO()
    # attachment.download(out)
    # out.seek(0)

    m.answer(
        message='attachment.owner: {}\n'
                'attachment["owner"]: {}\n'
                'size: {}\n'
                'as_attachment: {}\n'
                'raw_len: {}\n'.format(
                            owner_1, owner_2, size, as_attachment, len(raw)
                            ),
        attachment=as_attachment
    )


if __name__ == '__main__':
    server.run()
