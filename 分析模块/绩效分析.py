import numpy as np

class 绩效分析:
    @staticmethod
    def 计算夏普比率(收益率序列):
        if len(收益率序列) == 0 or收益率序列.std() == 0:
            return 0
        return np.sqrt(252) * 收益率序列.mean() / 收益率序列.std()
    
    @staticmethod
    def 计算最大回撤(权益曲线):
        if len(权益曲线) == 0:
            return 0
        累计最高 = np.maximum.accumulate(权益曲线)
        回撤 = (权益曲线 - 累计最高) / 累计最高
        return float(回撤.min())