from 数据接入模块 import 获取数据
from 风控模块.止损止盈 import 止损止盈

class AI交易引擎:
    """AI自动交易引擎"""
    
    def __init__(self):
        self.持仓 = {}
        self.现金 = 100000
        self.交易记录 = []
        self.当前类目 = "股票"
        self.风控 = None
    
    def 注册策略(self, 策略, 策略名称):
        self.策略名称 = 策略名称
        if "加密" in 策略名称:
            self.当前类目 = "加密货币"
            self.风控 = 止损止盈(止盈=0.08, 止损=0.05)
        else:
            self.当前类目 = "股票"
            self.风控 = 止损止盈(止盈=0.05, 止损=0.03)
    
    def 执行一轮(self):
        """执行一轮AI分析+交易"""
        df = 获取数据(self.当前类目)
        if df.empty:
            return {"action": "hold", "reason": "无数据"}
        
        # 风控检查
        for code in list(self.持仓.keys()):
            row = df[df['代码'] == code]
            if not row.empty:
                平仓, 原因, 价格 = self.风控.检查平仓(self.持仓[code], row.iloc[0]['最新价'])
                if 平仓:
                    self._执行卖出(code, 价格, 原因)
                    return {"action": "sell", "reason": 原因}
        
        # AI选股
        df['评分'] = df['涨跌幅'] * 2 + df['量比'] * 1.5
        best = df.sort_values('评分', ascending=False).iloc[0]
        
        if best['代码'] in self.持仓:
            return {"action": "hold", "reason": "已持有"}
        
        self._执行买入(best['代码'], best['名称'], best['最新价'])
        return {"action": "buy", "name": best['名称'], "reason": "AI推荐"}
    
    def _执行买入(self, 代码, 名称, 价格):
        数量 = int(self.现金 * 0.8 / 价格)
        self.持仓[代码] = {"名称": 名称, "买入价": 价格, "数量": 数量}
        self.现金 -= 数量 * 价格
    
    def _执行卖出(self, 代码, 价格, 原因):
        p = self.持仓[代码]
        self.现金 += p['数量'] * 价格
        del self.持仓[代码]