# -*- encoding: utf-8 -*-

import re
import random
import json

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

        self.message_handlers = []
        self.request_handlers = []
        self.middleware = []
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

        def regexp(m):
            if not isinstance(value, str):
                match = value.fullmatch(m.text)
            else:
                match = re.fullmatch(value, m.text)

            if match is None:
                return False

            m.regexp_ = match.groupdict()
            return True

        test_cases = {
            'regexp': regexp,
            'action': lambda m: m.get('action', {}).get('type') == value,
            'func': lambda m: value(m),
            'from_chat': lambda m: m.from_chat is value,
            'command': lambda m: m.command == value,
            'tags': lambda m: value.issubset(m.context.tags),
            'content_type': lambda m: set(value).issubset({
                ct for ct in CONTENT_TYPES if CONTENT_TYPES[ct](m)
            })
        }

        return test_cases.get(f, lambda m: False)(msg)

    def process_message(self, msg: dict):
        """ Обработка сообщения

        :param msg: Объект сообщения.
        :type msg: dict
        """

        msg = VkMessage(msg, self)
        for middleware in self.middleware:
            middleware(msg, msg.context)
            if msg.context.exit:
                return

        if msg.from_id in self.message_register_next_step:
            self.message_register_next_step[msg['from_id']](msg)
            self.message_register_next_step.pop(msg['from_id'])

        else:
            for handler in self.message_handlers:
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
        for handler in self.request_handlers:
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
        self.message_handlers.append(handler_dict)

    def add_event_handler(self, handler_dict: dict):
        """
        :param handler_dict: Словарь обработчика
            handler_dict['filters']: Словарь фильтров
            handler_dict['function']: Callable который будет обрабатывать
                                      событие если оно удовлетворяет
                                      условиям фильтров.
        :type handler_dict: dict
        """
        self.request_handlers.append(handler_dict)

    def register_middleware(self):
        def decorator(handler):
            self.middleware.append(handler)

        return decorator

    def message_handler(self, regexp=None, content_type: list = None, func: Callable = None,
                        command: str = None, from_chat: bool = None, action: str = None,
                        tags: set = None):
        """ Подписка Callable на события сообщений

        Фильтры:
        :param regexp: Callable будет вызываться, если текст сообщения
            удовлетворяет регулярному выражению. Например,
            @bot.message_handler(regexp=r'\\d+')
            ...

            будет вызываться если текст сообщения является числом.
            Кроме того, в поле m.regex_ будет сохранён groupdict.

        :param from_chat: Если True, то Callable будет вызываться только если сообщение
            отправлено в чате, если False, то только если сообщение отправдено в
            личные сообщения бота
        :type from_chat: bool

        :param action: Callable будет вызываться, если action сообщения равен данному.
            Подробнее: https://vk.com/dev/objects/message
            Например,
            @bot.message_handler(action='chat_invite_user')
            ...

            будет вызываться если в чат приглашен новый пользователь.

        :type action: str

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
            @bot.message_handler(content_type=['audio', 'text'])
            ...

            будет вызываться если сообщение содержит текст И аудиозапись.
        :type content_type: list

        :param func: Callable будет вызываться, если переданный Callable
            вернет True. Сигнатура: foo(m: VkMessage) -> bool.
            Например,
            @bot.message_handler(func=lambda m: m.from_id == 1)
            ...

            будет вызываться если сообщение отправил vk.com/id1
        :type func: Callable

        :param command: Callable будет вызываться, если поле 'command' из
            полезной нагрузки сообщения равен переданному.
            Например,
            @bot.message_handler(command='start')
            ...

            будет вызываться если пользователь нажал кнопку Начать.
        :type command: str

        :param tags
        :type tags: set

        :return: Декоратор
        """
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, regexp=regexp, content_type=content_type,
                                                    func=func, command=command, action=action,
                                                    from_chat=from_chat, tags=tags)
            self.add_message_handler(handler_dict)
            return handler

        return decorator

    def event_handler(self, func: Callable[[VkEvent], None] = None):
        """ Декортатор

        :param func: Callable будет вызываться, если переданный Callable
            вернет True.
        :type func: Callable

        :return: Декоратор
        """
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, func=func)
            self.add_event_handler(handler_dict)
            return handler

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
        for chunk in [peers[i:i + 20] for i in range(0, len(peers), 20)]:
            try:
                message_ids.extend(
                    self.api.execute(
                        code='var i = 0;'
                             'var peers = {};'
                             'var message_ids = [];'
                             'while (i < peers.length) {{'
                             'message_ids.push(API.messages.send({} + {{"peer_id": peers[i]}}));'
                             'i = i + 1;'
                             '}};'
                             'return message_ids;'.format(chunk, json.dumps(kwargs, ensure_ascii=False))
                    )
                )
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
