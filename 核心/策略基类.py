# -*- coding: utf-8 -*-
class 策略基类:
    """策略基类 - 所有策略的父类"""
    
    def __init__(self, 名称, 品种, 初始资金):
        self.名称 = 名称
        self.品种 = 品种
        self.初始资金 = 初始资金
        self.资金 = 初始资金
        self.持仓 = 0
        self.交易记录 = []
        self.价格历史 = []
        self.入场价 = 0
        self.入场时间 = None
        
        # ========== 策略参数（可在策略中心配置） ==========
        self.参数 = {
            "短期均线": 5,
            "长期均线": 20,
            "止损比例": 0.05,
            "止盈比例": 0.10,
            "仓位比例": 0.3,
        }

    def 处理行情(self, k线):
        """处理行情数据，子类需要重写"""
        return 'hold'
    
    def 计算仓位(self, 总资金, 当前价):
        """计算开仓数量，子类可以重写"""
        # 使用仓位比例参数
        仓位比例 = self.获取参数("仓位比例", 0.01)
        数量 = 总资金 * 仓位比例 / 当前价
        return round(数量, 4)
    
    def 获取参数(self, 参数名, 默认值=None):
        """获取策略参数"""
        return self.参数.get(参数名, 默认值)
    
    def 设置参数(self, 参数名, 值):
        """设置策略参数"""
        if 参数名 in self.参数:
            self.参数[参数名] = 值
            return True
        return False
    
    def 批量设置参数(self, 参数更新):
        """批量设置参数"""
        for k, v in 参数更新.items():
            if k in self.参数:
                self.参数[k] = v
        return True
    
    def 检查止损止盈(self, 当前价):
        """检查止损止盈"""
        if self.持仓 == 0 or self.入场价 == 0:
            return 'hold'
        
        盈亏率 = (当前价 - self.入场价) / self.入场价
        止损 = self.获取参数("止损比例", 0.05)
        止盈 = self.获取参数("止盈比例", 0.10)
        
        if 盈亏率 <= -止损:
            return 'sell'
        if 盈亏率 >= 止盈:
            return 'sell'
        return 'hold'
    
    def 获取策略信息(self):
        """获取策略信息"""
        return {
            "名称": self.名称,
            "品种": self.品种,
            "资金": self.资金,
            "持仓": self.持仓,
            "入场价": self.入场价,
            "参数": self.参数
        }
