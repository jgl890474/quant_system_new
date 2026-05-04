# -*- coding: utf-8 -*-
"""外汇策略模块"""

from .外汇利差策略 import ForexCarryStrategy
from .外汇突破策略 import ForexBreakoutStrategy
from .外汇双均线 import ForexDualMAStrategy

__all__ = [
    'ForexCarryStrategy',
    'ForexBreakoutStrategy',
    'ForexDualMAStrategy',
]