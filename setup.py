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
    install_requirements=['Flask',
                          'CherryPy',
                          'requests']
)
