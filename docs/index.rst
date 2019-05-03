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

   # Можно использовать другие обертки для API.
   # Например vk_api.
   import vk_requests

   from vbio import VkBot, LongPollClient

   api = vk_requests.create_api(service_token='<токен группы>')
   bot = VkBot(api)
   handler = LongPollClient(bot)


   @bot.message_handler()
   def hello_world(m):
       m.answer(message='Привет мир!')


   if __name__ == '__main__':
       handler.run()


.. toctree::
   :maxdepth: 2
   :caption: Содержание:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
