# -*- coding: utf-8 -*-
import random

class 策略运行器:
    @staticmethod
    def 运行(策略信息, 行情数据):
        if 策略信息.get("演示") or not 策略信息.get("类"):
            return random.choice(["buy", "sell", "hold"])
        try:
            实例 = 策略信息["类"](策略信息["名称"], 策略信息["品种"], 10000)
            k线 = {"close": 行情数据.价格, "high": 行情数据.最高, "low": 行情数据.最低, "open": 行情数据.开盘}
            return 实例.处理行情(k线)
        except:
            return "hold"
