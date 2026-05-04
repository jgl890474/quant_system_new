# -*- coding: utf-8 -*-
"""期货策略模块"""

from .期货趋势策略 import FuturesTrendStrategy
from .期货均值回归 import FuturesMeanReversionStrategy
from .期货ATR import FuturesATRStrategy

__all__ = [
    'FuturesTrendStrategy',
    'FuturesMeanReversionStrategy',
    'FuturesATRStrategy',
]