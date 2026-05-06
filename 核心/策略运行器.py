# -*- coding: utf-8 -*-
class 策略运行器:
    @staticmethod
    def 运行(策略信息, 行情数据):
        try:
            实例 = 策略信息["类"](策略信息["名称"], 策略信息["品种"], 10000)
            return 实例.处理行情({'close': 行情数据.价格})
        except:
            return 'hold'
