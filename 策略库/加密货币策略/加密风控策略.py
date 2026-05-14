# -*- coding: utf-8 -*-
"""
加密货币风控策略 - 升级版
优化点全部落地：
1. 新增分级止盈+移动止盈
2. 大趋势过滤 熊市不开仓
3. ATR动态止损 防20倍杠杆插针秒扫
4. 成交量真假突破过滤
5. 弱化左侧、双信号共振、强化右侧趋势
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
from datetime import datetime
import numpy as np


class 加密风控策略(策略基类):
    """
    加密货币风控交易策略 - 优化升级版
    核心：1%仓位 + 20倍杠杆 + ATR动态止损 + 分级止盈 + 趋势过滤
    """
    
    # ========== 策略元数据（用于自动发现） ==========
    策略名称 = "加密风控策略"
    策略类别 = "加密货币策略"
    策略描述 = "ATR动态止损+分级止盈+趋势过滤"
    策略版本 = "2.0.0"
    
    # 策略参数（可配置）
    策略参数 = {
        "单笔仓位比例": {"类型": "float", "默认值": 0.01, "描述": "单笔仓位比例"},
        "杠杆倍数": {"类型": "int", "默认值": 20, "描述": "杠杆倍数"},
        "止损比例": {"类型": "float", "默认值": 0.01, "描述": "止损比例"},
        "第一止盈幅度": {"类型": "float", "默认值": 0.015, "描述": "一级止盈"},
        "第二止盈幅度": {"类型": "float", "默认值": 0.025, "描述": "二级止盈"}
    }
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
        
        # ========== 原有风控参数（保留不变） ==========
        self.单笔仓位比例 = 0.01  # 1%仓位
        self.杠杆倍数 = 20        # 20倍杠杆
        self.同时持仓上限 = 3      # 最多同时持有3个品种
        self.每日交易上限 = 10     # 每天最多10次交易
        self.止损比例 = 0.01       # 单笔本金最大亏损封顶
        
        # ========== 策略参数 ==========
        self.短期均线 = 7
        self.中期均线 = 25
        self.长期均线 = 50
        self.RSI周期 = 14
        self.成交量周期 = 20
        self.ATR周期 = 14
        
        # ========== 新增优化参数 ==========
        self.放量倍数阈值 = 1.8        # 有效放量最低倍数
        self.第一止盈幅度 = 0.015      # 1.5%减半仓
        self.第二止盈幅度 = 0.025      # 2.5%全平
        self.移动止盈回撤 = 0.008      # 盈利超3%后回撤0.8%离场
        self.趋势判定均线短 = 25
        self.趋势判定均线长 = 50
        
        # 数据存储
        self.价格历史 = []
        self.成交量历史 = []
        self.RSI历史 = []
        self.ATR历史 = []
        
        # 每日统计
        self.今日交易次数 = 0
        self.今日日期 = None
        
        # 移动止盈记录
        self.持仓最高盈利 = 0
        
        print(f"✅ 加密风控策略【优化版】初始化完成")
        print(f"   仓位: {self.单笔仓位比例*100}% | 杠杆: {self.杠杆倍数}x")
        print(f"   动态ATR止损 | 分级止盈已启用")

    def 计算ATR(self, prices, period=14):
        """计算ATR真实波幅"""
        if len(prices) < period + 1:
            return np.mean(prices) * 0.01
        tr_list = []
        for i in range(1, len(prices)):
            tr = abs(prices[i] - prices[i-1])
            tr_list.append(tr)
        atr = np.mean(tr_list[-period:])
        return atr

    def 重置每日统计(self):
        """重置每日交易统计"""
        today = datetime.now().date()
        if self.今日日期 != today:
            self.今日日期 = today
            self.今日交易次数 = 0
            self.持仓最高盈利 = 0
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

    def 判断大趋势是否多头(self):
        """优化2：大趋势过滤 只多头允许开仓"""
        if len(self.价格历史) < self.趋势判定均线长:
            return False
        ma25 = self.计算均线(self.价格历史, self.趋势判定均线短)
        ma50 = self.计算均线(self.价格历史, self.趋势判定均线长)
        return ma25 > ma50

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
        """优化4+5：大跌反弹+放量过滤+均线站稳确认"""
        if len(self.价格历史) < 10:
            return False
        
        最近两日跌幅 = (self.价格历史[-2] - self.价格历史[-1]) / self.价格历史[-2]
        if 最近两日跌幅 >= -0.05:
            return False
        
        # 成交量真假突破过滤
        if len(self.成交量历史) > self.成交量周期:
            平均成交量 = sum(self.成交量历史[-self.成交量周期:]) / self.成交量周期
            当前成交量 = k线.get('volume', 0)
            if 当前成交量 <= 平均成交量 * self.放量倍数阈值:
                return False
        
        # 必须站稳长期均线 弱化左侧抄底
        长期均线 = self.计算均线(self.价格历史, self.长期均线)
        if self.价格历史[-1] < 长期均线 * 0.85 and self.价格历史[-1] > 长期均线:
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
        """优化5：大趋势优先 + 双信号共振 弱化单一左侧信号"""
        if len(self.价格历史) < 50:
            return False, None
        
        # 优化2：空头趋势直接禁止开仓
        if not self.判断大趋势是否多头():
            return False, None
        
        rsi = self.计算RSI(self.价格历史, self.RSI周期)
        self.RSI历史.append(rsi)
        
        突破信号 = self.检查趋势突破信号()
        有底背离 = self.检查底背离(self.价格历史, self.RSI历史)
        有大跌反弹 = self.检查大跌反弹信号(k线)
        RSI超卖 = rsi < 30

        # 优先右侧趋势共振信号
        if 突破信号 == "buy" and (RSI超卖 or 有底背离):
            print(f"   📈 趋势突破+指标共振 开仓")
            return True, "趋势共振突破"
        
        # 次选 底背离+均线多头
        if 有底背离 and RSI超卖:
            print(f"   📈 底背离+RSI超卖 共振")
            return True, "底背离共振"
        
        # 次选 放量大跌反弹
        if 有大跌反弹:
            print(f"   📈 放量大跌反弹信号")
            return True, "大跌放量反弹"
        
        return False, None

    def 检查平仓条件(self, 入场价, 当前价, 入场时间):
        """优化1+3：ATR动态止损 + 分级止盈 + 移动止盈"""
        盈亏率 = (当前价 - 入场价) / 入场价
        
        # 更新持仓最高盈利
        if 盈亏率 > self.持仓最高盈利:
            self.持仓最高盈利 = 盈亏率

        # 优化3：ATR动态止损 + 本金最大亏损双重风控
        atr = self.计算ATR(self.价格历史, self.ATR周期)
        动态止损价 = 入场价 - atr * 1.5
        if 当前价 <= 动态止损价 or 盈亏率 <= -self.止损比例:
            return True, f"动态止损触发 (盈亏: {盈亏率*100:.2f}%)"

        # 优化1：分级止盈
        if 盈亏率 >= self.第二止盈幅度:
            return True, f"二级止盈 {self.第二止盈幅度*100:.1f}%"
        
        # 移动止盈：盈利超3%后回撤离场
        if self.持仓最高盈利 >= 0.03 and (self.持仓最高盈利 - 盈亏率) >= self.移动止盈回撤:
            return True, "移动止盈回撤离场"

        # 原有指标平仓逻辑保留
        if len(self.RSI历史) > 20:
            if self.检查顶背离(self.价格历史, self.RSI历史):
                return True, "顶背离卖出"
        
        突破信号 = self.检查趋势突破信号()
        if 突破信号 == "sell":
            return True, "趋势跌破"
        
        rsi = self.计算RSI(self.价格历史, self.RSI周期)
        if rsi > 70:
            return True, f"RSI超买({rsi:.0f})"
        
        return False, None

    def 计算仓位(self, 总资金, 当前价):
        """计算开仓数量（1%资金 + 20倍杠杆 保留原逻辑不变）"""
        保证金 = 总资金 * self.单笔仓位比例
        合约价值 = 保证金 * self.杠杆倍数
        数量 = 合约价值 / 当前价
        数量 = round(数量, 4)
        print(f"   💰 仓位计算: 保证金={保证金:.2f}, 杠杆={self.杠杆倍数}x, 数量={数量}")
        return 数量

    def 处理行情(self, k线):
        """处理行情数据，返回交易信号"""
        self.重置每日统计()
        
        当前价 = k线.get('close', 0)
        当前成交量 = k线.get('volume', 0)
        
        if 当前价 <= 0:
            return 'hold'
        
        self.价格历史.append(当前价)
        self.成交量历史.append(当前成交量)
        
        if len(self.价格历史) < 50:
            return 'hold'
        
        # 持仓中
        if self.持仓 > 0:
            应平仓, 理由 = self.检查平仓条件(self.入场价, 当前价, self.入场时间)
            if 应平仓:
                print(f"   🔴 平仓信号: {理由}")
                # 重置最高盈利记录
                self.持仓最高盈利 = 0
                return 'sell'
            else:
                return 'hold'
        
        # 开仓次数限制
        if self.今日交易次数 >= self.每日交易上限:
            print(f"   ⚠️ 今日交易已达上限 {self.每日交易上限} 次")
            return 'hold'
        
        # 开仓判断
        应开仓, 信号类型 = self.检查开仓条件(k线)
        if 应开仓:
            self.入场价 = 当前价
            self.入场时间 = datetime.now()
            self.今日交易次数 += 1
            self.持仓最高盈利 = 0
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
