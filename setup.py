# -*- coding: utf-8 -*-

import setuptools
import vbio


setuptools.setup(
    name="vbio",
    version=vbio.__version__,
    author=vbio.__author__,
    packages=['vbio', 'vbio.servers']
)
