# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import sys


def init_logger():
    logger = logging.getLogger('vbio')
    logger.setLevel(logging.INFO)

    try:
        import colorama
        colorama.init()
        fmt = '{y}*{r} {m}[%(asctime)s]{r} {y}%(levelname)s:{r} %(message)s'.format(
            y=colorama.Fore.YELLOW,
            m=colorama.Fore.MAGENTA,
            r=colorama.Fore.RESET
        )

    except ImportError:
        fmt = '* [%(asctime)s] %(levelname)s: %(message)s'

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(
        logging.Formatter(fmt, datefmt='%Y/%b/%d %H:%M:%S'))

    logger.addHandler(stream)
    return logger
