# Vk Bot I/O [![PyPI](https://img.shields.io/pypi/v/vbio.svg)](https://pypi.org/project/vbio/)
**vbio** - Python модуль для написания скриптов, использующих Callback API для социальной сети Вконтакте (vk.com)
* [Документация](https://vbio.readthedocs.io/en/latest/)

## Hello world
```python
import vk_requests  # Можно использовать другие обертки для API,
		    # например vk_api.
from vbio import VkBot
from vbio.servers import FlaskServer

api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(secret='<секретный ключ>', 
            confirmation='<строка, которую должен вернуть сервер>',
            api=api)
server = FlaskServer(bot, port=80)


@bot.callback_message_handler()
def hello_world(m):
    m.answer(message='Привет мир!')


if __name__ == '__main__':
    server.run()
```

## Установка
```
pip3 install vbio
```
или
```
pip3 install --user vbio
```
