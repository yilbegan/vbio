# -*- coding: utf-8 -*-

import setuptools
import vbio


setuptools.setup(
    name="vbio",

    version=vbio.__version__,
    author=vbio.__author__,

    description=u'Python модуль для написания скриптов, использующих '
                u'Callback API для социальной сети '
                u'Вконтакте (vk.com)',

    url='https://github.com/yilbegan/vbio',
    license='MIT',

    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    packages=['vbio', 'vbio.servers'],
    install_requires=['requests'],
    extras_require={
        'webhook': ['Flask'],
        'color': ['colorama']
    },

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
