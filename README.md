# Vk Bot I/O [![PyPI](https://img.shields.io/pypi/v/vbio.svg)](https://pypi.org/project/vbio/)
**vbio** - Python модуль для написания скриптов, использующих Bots API для социальной сети Вконтакте (vk.com)
* [Документация](https://vbio.readthedocs.io/en/latest/)
* [Примеры использования](./examples) (python3)
## Hello world
```python
# Можно использовать другие обертки для API.
# Например vk_api.
import vk_requests

from vbio import VkBot
from vbio.servers import LongPoolClient
    
api = vk_requests.create_api(service_token='<токен группы>')
bot = VkBot(api)
server = LongPoolClient(bot)
    
    
@bot.message_handler()
def hello_world(m):
    m.answer(message='Привет мир!')
    
    
if __name__ == '__main__':
    server.run()
```

## Установка
```
# pip3 install vbio
```
С цветным выводом в консоль:
```
# pip3 install vbio[color]
```
С поддержкой webhook:
```
# pip3 install vbio[webhook]
```