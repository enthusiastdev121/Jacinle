#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : __init__.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 01/24/2018
#
# This file is part of Jacinle.
# Distributed under terms of the MIT license.


try:
    from .cuda.copy import async_copy_to
    from .functional import *
    from .graph import *
    from .utils import *
    from .train import TrainerEnv
    from .io import *

    from . import data
    from . import nn
    from . import models
    from . import optim
    from . import parallel
    from . import train

except ImportError:
    from jacinle.logging import get_logger
    logger = get_logger(__file__)
    logger.exception('Import error is raised during initializing the jactorch package. Please make sure that the torch '
                     'package is correctly installed')

from jactorch.utils.init import init_main

init_main()

del init_main
