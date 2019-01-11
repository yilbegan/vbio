# -*- encoding: utf-8 -*-

import requests
import json

from enum import Enum
from copy import deepcopy
from typing import IO

COLORS = frozenset(('default', 'primary', 'negative', 'positive'))
DOWNLOADABLE = frozenset(('photo', 'doc', 'audio'))
CONTENT_TYPES = {
    'text': lambda m: 'text' in m,
    'geo': lambda m: 'geo' in m,
    'fwd_messages': lambda m: 'fwd_messages' in m,
    'emoji': lambda m: 'emoji' in m,
    'photo': lambda m: 'photo' in {a.type for a in m.get('attachments', [])},
    'video': lambda m: 'video' in {a.type for a in m.get('attachments', [])},
    'audio': lambda m: 'audio' in {a.type for a in m.get('attachments', [])},
    'doc': lambda m: 'doc' in {a.type for a in m.get('attachments', [])},
    'link': lambda m: 'link' in {a.type for a in m.get('attachments', [])},
    'market': lambda m: 'market' in {a.type for a in m.get('attachments', [])},
    'market_album': lambda m: 'market_album' in {a.type for a in m.get('attachments', [])},
    'wall': lambda m: 'wall' in {a.type for a in m.get('attachments', [])},
    'wall_reply': lambda m: 'doc' in {a.type for a in m.get('attachments', [])},
    'sticker': lambda m: 'sticker' in {a.type for a in m.get('attachments', [])},
    'gift': lambda m: 'gift' in {a.type for a in m.get('attachments', [])},
    'graffiti': lambda m: 4 in {a['type'] for a in m.get('attachments', []) if a.type == 'doc'}
}


class Dictionaryable:
    def dict(self) -> dict:
        raise NotImplementedError()


class JsonSerializable:
    def json(self) -> str:
        raise NotImplementedError()


class VkBotServer:
    def run(self, *args, **kwargs):
        raise NotImplementedError()


class VkKeyboardMarkup(Dictionaryable, JsonSerializable):

    def __init__(self, onetime: bool = False, stack_size: int = 4):
        self.buttons = []
        self.onetime = onetime
        self.stack_size = stack_size
        self._stack = []

    def add(self, button):
        if self._stack:
            stack = deepcopy(self._stack)
            self._stack = []
            self.row(*stack)

        if isinstance(button, str):
            self.buttons.append([VkKeyboardButton(button)()])

        else:
            self.buttons.append([button()])

    def row(self, *args):
        if self._stack:
            stack = self._stack
            self._stack = []
            self.row(*stack)

        row = []
        for button in args:
            row.append(button())

        self.buttons.append(row)

    def stack(self, *args):
        for button in args:
            self._stack.append(button)
            if len(self._stack) >= self.stack_size:
                stack = self._stack
                self._stack = []
                self.row(*stack)

    def dict(self) -> dict:
        if self._stack:
            stack = deepcopy(self._stack)
            self._stack = []
            self.row(*stack)

        return {
            'one_time': self.onetime,
            'buttons': self.buttons
        }

    def json(self) -> str:
        return json.dumps(self.dict(), ensure_ascii=False)

    def __call__(self) -> str:
        return self.json()

    def __str__(self) -> str:
        return self.json()


class VkColor(Enum):
    DEFAULT = 'default'
    PRIMARY = 'primary'
    NEGATIVE = 'negative'
    POSITIVE = 'positive'


class VkKeyboardButton(Dictionaryable):

    def __init__(self, label: str, color: str or VkColor = 'default', payload: dict = None):
        if payload is None:
            payload = {'command': 'test'}

        if isinstance(color, VkColor):
            color = color.value

        self.label = label
        self.color = color
        self.payload = json.dumps(payload, ensure_ascii=False)

        assert label
        assert color in COLORS
        assert len(payload) <= 255

    def dict(self) -> dict:
        return {
            'color': self.color,
            'action': {
                'type': 'text',
                'payload': self.payload,
                'label': self.label
            }
        }

    def __call__(self) -> dict:
        return self.dict()


class VkMessage:

    def __init__(self, message: dict, bot):
        self.data = message
        self.data['payload'] = json.loads(self.data.get('payload', '{}'))
        if 'attachments' in self.data:
            attachments = []
            for a in self.data['attachments']:
                attachments.append(
                    VkAttachment(a)
                )
            self.data['attachments'] = attachments
        self.bot = bot

    def __getattr__(self, item):
        return self.data[item]

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self) -> str:
        return str(self.data)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self):
        for key in self.data:
            yield key

    @property
    def from_chat(self) -> bool:
        return self.data['from_id'] != self.data['peer_id']

    @property
    def command(self) -> str:
        return self.payload.get('command')

    def answer(self, **kwargs):
        return self.bot.answer_message(self, **kwargs)

    def copy(self) -> dict:
        return deepcopy(self.data)

    def get(self, item, default=None):
        return self.data.get(item, default)


class VkAttachment:

    def __init__(self, attachment: dict):
        self.data = attachment

    def __getattr__(self, item):
        return self.data[item]

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self) -> str:
        return str(self.data)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self):
        for key in self.data:
            yield key

    @property
    def size(self):
        if self.type == 'photo':
            return self[self.type]['width'], self[self.type]['height']
        else:
            raise NotImplementedError()

    @property
    def to_attachment(self) -> str:
        return '{}{}_{}_{}'.format(self.type,
                                   self[self.type]['owner_id'],
                                   self[self.type]['id'],
                                   self[self.type].get('access_key', ''))

    def download(self, out: IO = None) -> bytes or None:
        if self.type not in DOWNLOADABLE:
            raise NotImplementedError()

        if self.type == 'photo':
            url = sorted(
                self.photo['sizes'],
                key=lambda x: x["height"]
            )[-1]['url']
        else:
            url = self[self.type]['url']

        data = requests.get(url).content

        if out:
            out.write(data)

        return data


class VkCallbackRequest:

    def __init__(self, data: dict):
        self.type = data['type']
        self.data = data['object']
        self.group_id = data['group_id']

    def __getattr__(self, item):
        return self.data[item]

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self) -> str:
        return str(self.data)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self):
        for key in self.data:
            yield key
