# -*- encoding: utf-8 -*-

import re
import random

from vbio.types import CONTENT_TYPES, VkMessage, VkEvent
from vbio.logging import init_logger
from typing import Callable

__all__ = ('VkBot',)


class VkBot:
    """
    :param api: Обертка для апи, поддерживаются реализации из
        модулей vk, vk_requests, vk_api и другие с
        сигнатурой api.method_group.method_name(**params)

    :param ignore_errors: Игнорирование ошибок.
    :type ignore_errors: bool

    """
    
    def __init__(self, api, ignore_errors: bool = True):
        self.ignore_errors = ignore_errors
        self.api = api

        self.callback_message_handlers = []
        self.callback_request_handlers = []
        self.message_register_next_step = {}

        self.logger = init_logger()

    @staticmethod
    def _build_handler_dict(f: Callable, **filters) -> dict:
        return {
            'function': f,
            'filters': filters
        }

    @staticmethod
    def _test_filter(f: str, value, msg: VkMessage) -> bool:
        if value is None:
            return True

        test_cases = {
            'regexp': lambda m: re.fullmatch(value, msg.text),
            'func': lambda m: value(m),
            'text': lambda m: m.text == value,
            'content_type': lambda m: set(value).issubset({
                ct for ct in CONTENT_TYPES if CONTENT_TYPES[ct](m)
            }),
            'payload': lambda m: m.payload == value,
            'command': lambda m: m.command == value
        }

        return test_cases.get(f, lambda m: False)(msg)

    def process_message(self, msg: dict):
        """ Обработка сообщения

        :param msg: Объект сообщения.
        :type msg: dict
        """

        msg = VkMessage(msg, self)
        if msg.from_id in self.message_register_next_step:
            self.message_register_next_step[msg['from_id']](msg)
            self.message_register_next_step.pop(msg['from_id'])

        else:
            for handler in self.callback_message_handlers:
                for fil in handler['filters']:
                    if handler['filters'][fil] is None:
                        pass

                    elif not self._test_filter(fil, handler['filters'][fil], msg):
                        break
                else:
                    handler['function'](msg)
                    break

    def process_event(self, req: dict):
        """ Обработка других событий

        :param req: Объект события
        :type req: dict
        """

        req = VkEvent(req)
        for handler in self.callback_request_handlers:
            if handler['filters']['func'] is None:
                pass

            elif not handler['filters']['func'](req):
                continue

            handler['function'](req)
            break

    def add_message_handler(self, handler_dict: dict):
        """
        :param handler_dict: Словарь обработчика
            handler_dict['filters']: Словарь фильтров
            handler_dict['function']: Функция которая будет обрабатывать
                                      сообщение если оно удовлетворяет
                                      условиям фильтров.
        :type handler_dict: dict
        """
        self.callback_message_handlers.append(handler_dict)

    def add_event_handler(self, handler_dict: dict):
        """
        :param handler_dict: Словарь обработчика
            handler_dict['filters']: Словарь фильтров
            handler_dict['function']: Callable который будет обрабатывать
                                      событие если оно удовлетворяет
                                      условиям фильтров.
        :type handler_dict: dict
        """
        self.callback_request_handlers.append(handler_dict)

    def message_handler(self, regexp: str = None, content_type: list = None, func: Callable = None,
                        text: str = None, command: str = None, payload: dict = None):
        """ Подписка Callable на события сообщений

        Фильтры:
        :param regexp: Callable будет вызываться, если текст сообщения
            удовлетворяет регулярному выражению. Например,
            @bot.callback_message_handler(regexp=r'\d+')
            ...

            будет вызываться если текст сообщения является числом.
        :type regexp: str

        :param content_type: Callable будет вызываться, если сообщение
            содержит все типы вложений из переданного списка.
            Типы вложений:
                text: Сообщение содержит текст
                geo: Сообщение содержат геометку
                fwd_messages: Сообщение содержит пересланные сообщения
                graffiti: Сообщение содержит граффити
                Также поддерживаются прочие типы медиавложений,
                см. https://vk.com/dev/objects/attachments_m
            Например,
            @bot.callback_message_handler(content_type=['audio', 'text'])
            ...

            будет вызываться если сообщение содержит текст И аудиозапись.
        :type content_type: list

        :param func: Callable будет вызываться, если переданный Callable
            вернет True. Сигнатура: foo(m: VkMessage) -> bool.
            Например,
            @bot.callback_message_handler(func=lambda m: m.from_id == 1)
            ...

            будет вызываться если сообщение отправил vk.com/id1
        :type func: Callable

        :param text: Callable будет вызываться, если текст сообщения равен
            переданному.
            Например,
            @bot.callback_message_handler(text='hello')
            ...

            будет вызываться если текст сообщения равен 'hello'
        :type text: str

        :param command: Callable будет вызываться, если поле 'command' из
            полезной нагрузки сообщения равен переданному.
            Например,
            @bot.callback_message_handler(command='start')
            ...

            будет вызываться если пользователь нажал кнопку Начать.
        :type command: str

        :param payload: Callable будет вызываться, если полезная нагрузка
            сообщения равна данной.
            Например,
            @bot.callback_message_handler(payload={'command': 'start'})
            ...

            будет вызываться аналогично с предыдущим примером.
        :type payload: dict

        :return: Декоратор
        """
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, regexp=regexp, content_type=content_type,
                                                    func=func, text=text, command=command,
                                                    payload=payload)
            self.add_message_handler(handler_dict)

        return decorator

    def callback_event_handler(self, func: Callable[[VkEvent], None] = None):
        """ Декортатор

        :param func: Callable будет вызываться, если переданный Callable
            вернет True.
        :type func: Callable

        :return: Декоратор
        """
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, func=func)
            self.add_event_handler(handler_dict)

        return decorator

    def answer_message(self, msg: VkMessage, **kwargs):
        """ Ответ на сообщение

        :param msg: Объект сообщения
        :type msg: VkMessage

        :param kwargs: Агрументы
        :type kwargs: dict
        """
        if 'random_id' not in kwargs:
            kwargs['random_id'] = random.randint(-2147483648, 2147483647)

        return self.api.messages.send(peer_id=msg.peer_id, **kwargs)

    def get_user(self, msg: VkMessage, **kwargs):
        """ Получение информации о пользователе по сообщению

        :param msg: Объект сообщения
        :type msg: VkMessage

        :param kwargs: Агрументы
        :type kwargs: dict
        """
        return self.api.users.get(user_ids=msg.from_id, **kwargs)[0]

    def broadcast(self, peers: list, ignore_errors: bool = True, **kwargs) -> list:
        """ Массовая рассылка

        :param peers: Список peer_id чатов для рассылки
        :type peers: list

        :param ignore_errors: Игнорировать ошибки
        :type ignore_errors: bool

        :param kwargs: Агрументы
        :type kwargs: dict

        :return: Список ID отправленных сообщений
        """
        if 'random_id' not in kwargs:
            kwargs['random_id'] = random.randint(-2147483648, 2147483647)

        message_ids = []
        for peer in peers:
            try:
                message_ids.append(self.api.messages.send(peer_id=peer, **kwargs))
            except Exception as ex:
                if not ignore_errors:
                    raise ex
                message_ids.append(None)
        return message_ids

    def register_next_step(self, msg: VkMessage, func: Callable[[VkMessage], None]):
        """ Следующее сообщение будет обработано данным Callable

        :param msg: Объект сообщения
        :param msg: VkMessage

        :param func: Обработчик
        :type func: Callable[[VkMessage], None]

        """
        self.message_register_next_step[msg['from_id']] = func
