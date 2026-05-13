# -*- coding: utf-8 -*-
"""
加密货币风控策略 - 基于您提供的交易系统
核心规则：
1. 单笔交易上限：总资金的1%
2. 杠杆：20倍（小仓位高杠杆）
3. 同时持仓：不超过3个
4. 每日交易：不超过10次
5. 止损：单笔1%本金直接止损
6. 盈利提现：系统自动记录，手动提现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
from datetime import datetime
import numpy as np


class 加密风控策略(策略基类):
    """
    加密货币风控交易策略
    核心：1%仓位 + 20倍杠杆 + 严格止损
    """
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
        
        # ========== 风控参数 ==========
        self.单笔仓位比例 = 0.01  # 1%仓位
        self.杠杆倍数 = 20        # 20倍杠杆
        self.同时持仓上限 = 3      # 最多同时持有3个品种
        self.每日交易上限 = 10     # 每天最多10次交易
        self.止损比例 = 0.01       # 1%止损（本金）
        
        # ========== 策略参数 ==========
        self.短期均线 = 7
        self.中期均线 = 25
        self.长期均线 = 50
        self.RSI周期 = 14
        self.成交量周期 = 20
        
        # 数据存储
        self.价格历史 = []
        self.成交量历史 = []
        self.RSI历史 = []
        
        # 每日统计
        self.今日交易次数 = 0
        self.今日日期 = None
        
        print(f"✅ 加密风控策略初始化完成")
        print(f"   品种: {品种}")
        print(f"   仓位: {self.单笔仓位比例*100}% | 杠杆: {self.杠杆倍数}x")
        print(f"   止损: {self.止损比例*100}% | 同时持仓: {self.同时持仓上限}")
    
    def 重置每日统计(self):
        """重置每日交易统计"""
        today = datetime.now().date()
        if self.今日日期 != today:
            self.今日日期 = today
            self.今日交易次数 = 0
            print(f"📅 新的一天，重置交易统计")
    
    def 计算RSI(self, prices, period=14):
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices[-period-1:])
        gain = np.sum(deltas[deltas > 0]) / period
        loss = -np.sum(deltas[deltas < 0]) / period
        
        if loss == 0:
            return 100
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def 计算均线(self, prices, period):
        """计算移动平均线"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    def 检查底背离(self, prices, rsi_values):
        """检查底背离：价格新低，RSI不再新低"""
        if len(prices) < 20 or len(rsi_values) < 20:
            return False
        
        recent_prices = prices[-20:]
        recent_rsi = rsi_values[-20:]
        
        price_min = min(recent_prices)
        price_min_index = recent_prices.index(price_min)
        
        rsi_min = min(recent_rsi)
        rsi_min_index = recent_rsi.index(rsi_min)
        
        if price_min_index > rsi_min_index:
            return True
        return False
    
    def 检查顶背离(self, prices, rsi_values):
        """检查顶背离：价格新高，RSI不再新高"""
        if len(prices) < 20 or len(rsi_values) < 20:
            return False
        
        if prices[-1] > prices[-5] and rsi_values[-1] < rsi_values[-5]:
            return True
        return False
    
    def 检查大跌反弹信号(self, k线):
        """检查下跌接刀信号（左侧抄底）"""
        if len(self.价格历史) < 10:
            return False
        
        最近两日跌幅 = (self.价格历史[-2] - self.价格历史[-1]) / self.价格历史[-2]
        if 最近两日跌幅 >= -0.05:
            return False
        
        if len(self.成交量历史) > self.成交量周期:
            平均成交量 = sum(self.成交量历史[-self.成交量周期:]) / self.成交量周期
            当前成交量 = k线.get('volume', 0)
            if 当前成交量 <= 平均成交量 * 1.5:
                return False
        
        长期均线 = self.计算均线(self.价格历史, self.长期均线)
        if self.价格历史[-1] < 长期均线 * 0.85:
            return True
        
        return False
    
    def 检查趋势突破信号(self):
        """检查趋势突破/跌破信号（右侧确认）"""
        if len(self.价格历史) < self.长期均线:
            return None
        
        当前价 = self.价格历史[-1]
        
        MA7 = self.计算均线(self.价格历史, 7)
        MA25 = self.计算均线(self.价格历史, 25)
        
        if 当前价 < MA7 and 当前价 < MA25:
            return "sell"
        
        if 当前价 > MA7 and 当前价 > MA25 and len(self.价格历史) >= 2 and self.价格历史[-2] <= MA25:
            return "buy"
        
        return None
    
    def 检查开仓条件(self, k线):
        """综合检查开仓条件"""
        if len(self.价格历史) < 50:
            return False, None
        
        rsi = self.计算RSI(self.价格历史, self.RSI周期)
        self.RSI历史.append(rsi)
        
        # 条件1：底背离信号
        if self.检查底背离(self.价格历史, self.RSI历史):
            print(f"   📈 检测到底背离信号")
            return True, "底背离"
        
        # 条件2：大跌反弹信号
        if self.检查大跌反弹信号(k线):
            print(f"   📈 检测到大跌反弹信号")
            return True, "大跌反弹"
        
        # 条件3：趋势突破信号
        突破信号 = self.检查趋势突破信号()
        if 突破信号 == "buy":
            print(f"   📈 检测到趋势突破信号")
            return True, "趋势突破"
        
        # 条件4：RSI超卖（<30）
        if rsi < 30:
            print(f"   📈 RSI超卖: {rsi:.1f}")
            return True, f"RSI超卖({rsi:.0f})"
        
        return False, None
    
    def 检查平仓条件(self, 入场价, 当前价, 入场时间):
        """检查平仓/止损条件"""
        盈亏率 = (当前价 - 入场价) / 入场价
        
        # 条件1：止损
        if 盈亏率 <= -self.止损比例:
            return True, f"止损触发 (盈亏: {盈亏率*100:.2f}%)"
        
        # 条件2：顶背离
        if len(self.RSI历史) > 20:
            if self.检查顶背离(self.价格历史, self.RSI历史):
                return True, "顶背离卖出"
        
        # 条件3：趋势跌破
        突破信号 = self.检查趋势突破信号()
        if 突破信号 == "sell":
            return True, "趋势跌破"
        
        # 条件4：RSI超买（>70）
        rsi = self.计算RSI(self.价格历史, self.RSI周期)
        if rsi > 70:
            return True, f"RSI超买({rsi:.0f})"
        
        return False, None
    
    def 计算仓位(self, 总资金, 当前价):
        """计算开仓数量（1%资金 + 20倍杠杆）"""
        # 1%资金作为保证金
        保证金 = 总资金 * self.单笔仓位比例
        
        # 20倍杠杆下的合约价值
        合约价值 = 保证金 * self.杠杆倍数
        
        # 计算数量
        数量 = 合约价值 / 当前价
        
        # 格式化数量（加密货币保留4位小数）
        数量 = round(数量, 4)
        
        print(f"   💰 仓位计算: 保证金={保证金:.2f}, 杠杆={self.杠杆倍数}x, 数量={数量}")
        
        return 数量
    
    def 处理行情(self, k线):
        """
        处理行情数据，返回交易信号
        返回: 'buy', 'sell', 'hold'
        """
        # 重置每日统计
        self.重置每日统计()
        
        # 记录数据
        当前价 = k线.get('close', 0)
        当前成交量 = k线.get('volume', 0)
        
        if 当前价 <= 0:
            return 'hold'
        
        self.价格历史.append(当前价)
        self.成交量历史.append(当前成交量)
        
        # 数据不足，返回持有
        if len(self.价格历史) < 50:
            return 'hold'
        
        # ========== 持仓管理 ==========
        if self.持仓 > 0:
            # 检查平仓条件
            应平仓, 理由 = self.检查平仓条件(self.入场价, 当前价, self.入场时间)
            if 应平仓:
                print(f"   🔴 平仓信号: {理由}")
                return 'sell'
            else:
                return 'hold'
        
        # ========== 开仓管理 ==========
        # 检查每日交易次数限制
        if self.今日交易次数 >= self.每日交易上限:
            print(f"   ⚠️ 今日交易已达上限 {self.每日交易上限} 次")
            return 'hold'
        
        # 检查开仓条件
        应开仓, 信号类型 = self.检查开仓条件(k线)
        
        if 应开仓:
            # 存储开仓信息
            self.入场价 = 当前价
            self.入场时间 = datetime.now()
            
            self.今日交易次数 += 1
            
            print(f"   🟢 开仓信号: {信号类型}")
            print(f"   📊 入场价: {当前价:.2f}")
            
            return 'buy'
        
        return 'hold'
    
    def 获取策略信息(self):
        """获取策略信息"""
        return {
            "名称": self.名称,
            "品种": self.品种,
            "仓位比例": f"{self.单笔仓位比例*100}%",
            "杠杆倍数": f"{self.杠杆倍数}x",
            "止损比例": f"{self.止损比例*100}%",
            "同时持仓上限": self.同时持仓上限,
            "每日交易上限": self.每日交易上限,
            "当前持仓": self.持仓,
            "今日交易次数": self.今日交易次数
        }
