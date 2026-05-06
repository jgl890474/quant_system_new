
# -*- coding: utf-8 -*-
import numpy as np

def 计算夏普比率(收益率序列, 无风险利率=0.02):
    return np.mean(收益率序列) / np.std(收益率序列) if np.std(收益率序列) > 0 else 0

def 计算最大回撤(净值序列):
    峰值 = np.maximum.accumulate(净值序列)
    回撤 = (净值序列 - 峰值) / 峰值
    return np.min(回撤)
