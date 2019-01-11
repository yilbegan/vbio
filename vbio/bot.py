# -*- encoding: utf-8 -*-

import logging
import re

from vbio.types import CONTENT_TYPES, VkMessage, VkCallbackRequest
from vbio.logging import init_logger
from typing import Callable

__all__ = ('VkBot',)


class VkBot:

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

    def process_request(self, req: dict or list):
        req = VkCallbackRequest(req)
        for handler in self.callback_request_handlers:
            if handler['filters']['func'] is None:
                pass

            elif not handler['filters']['func'](req):
                continue

            handler['function'](req)
            break

    def add_callback_message_handler(self, handler_dict: dict):
        self.callback_message_handlers.append(handler_dict)

    def add_callback_request_handler(self, handler_dict: dict):
        self.callback_request_handlers.append(handler_dict)

    def callback_message_handler(self, regexp: str = None, content_type: list = None, func: Callable = None,
                                 text: str = None, command: str = None, payload: dict = None):
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, regexp=regexp, content_type=content_type,
                                                    func=func, text=text, command=command,
                                                    payload=payload)
            self.add_callback_message_handler(handler_dict)

        return decorator

    def callback_request_handler(self, func: Callable = None):
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, func=func)
            self.add_callback_request_handler(handler_dict)

        return decorator

    def answer_message(self, msg: VkMessage, **kwargs):
        return self.api.messages.send(peer_id=msg.peer_id, **kwargs)

    def get_user(self, msg: VkMessage, **kwargs):
        return self.api.users.get(user_ids=msg.from_id, **kwargs)[0]

    def broadcast(self, peers: list, ignore_errors: bool = True, **kwargs) -> list:
        message_ids = []
        for peer in peers:
            try:
                message_ids.append(self.api.messages.send(peer_id=peer, **kwargs))
            except Exception as ex:
                if not ignore_errors:
                    raise ex
                message_ids.append(None)
        return message_ids

    def register_next_step(self, msg, func):
        self.message_register_next_step[msg['from_id']] = func
