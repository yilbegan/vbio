Документация vbio
=================

vbio - Python модуль для написания скриптов, использующих Callback API для социальной сети Вконтакте (vk.com)

`Установка через PIP
<https://pythonworld.ru/osnovy/pip.html>`_:

.. code-block:: shell-session

   # pip install --user vbio

или

.. code-block:: shell-session

   # pip install vbio

Hello world!
------------

.. code-block:: python

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

.. toctree::
   :maxdepth: 2
   :caption: Содержание:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
