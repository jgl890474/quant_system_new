# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from 工具 import 数据库

def 获取当前时间():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.已实现盈亏 = 0
        self.持仓 = {}
        self.交易记录 = []
        self.当前策略 = ""
        
        self._恢复持仓()
        if 数据库.获取系统参数("初始资金") is None:
            数据库.保存系统参数("初始资金", 初始资金)
    
    def _恢复持仓(self):
        try:
            from .数据模型 import 持仓数据 as 持仓类
            for 品种, 数据 in 数据库.获取所有持仓().items():
                pos = 持仓类(品种, 数据['数量'], 数据['平均成本'])
                pos.已实现盈亏 = data.get('已实现盈亏', 0)
                try:
                    from 核心 import 行情获取
                    pos.当前价格 = 行情获取.获取价格(品种).价格
                except:
                    pos.当前价格 = pos.平均成本
                self.持仓[品种] = pos
                self.已实现盈亏 += pos.已实现盈亏
        except:
            pass

    def 更新所有持仓价格(self):
        try:
            from 核心 import 行情获取
            for 品种, pos in self.持仓.items():
                try:
                    pos.当前价格 = 行情获取.获取价格(品种).价格
                except:
                    pass
        except:
            pass

    def _保存持仓到数据库(self):
        for 品种, pos in self.持仓.items():
            数据库.保存持仓(品种, pos.数量, pos.平均成本, pos.已实现盈亏)

    def 获取占用资金(self):
        return sum(pos.数量 * pos.平均成本 for pos in self.持仓.values())

    def 获取浮动盈亏(self):
        self.更新所有持仓价格()
        return sum(pos.数量 * (pos.当前价格 - pos.平均成本) for pos in self.持仓.values())

    def 获取持仓市值(self):
        self.更新所有持仓价格()
        return sum(pos.数量 * pos.当前价格 for pos in self.持仓.values())

    def 获取可用资金(self):
        return self.初始资金 - self.获取占用资金() + self.已实现盈亏

    def 获取总资产(self):
        return self.获取可用资金() + self.获取持仓市值()

    def 获取总盈亏(self):
        return self.获取浮动盈亏() + self.已实现盈亏

    def 买入(self, 品种, 价格, 数量=100, 策略名称=""):
        try:
            from .数据模型 import 持仓数据
        except:
            class 持仓数据:
                def __init__(self, 品种, 数量, 平均成本):
                    self.品种 = 品种
                    self.数量 = 数量
                    self.平均成本 = 平均成本
                    self.当前价格 = 平均成本
                    self.已实现盈亏 = 0

        if 策略名称:
            self.当前策略 = 策略名称

        需要资金 = 价格 * 数量
        if 需要资金 > self.获取可用资金():
            st.error(f"资金不足！需要 ¥{需要资金:,.0f}")
            return

        if 品种 in self.持仓:
            pos = self.持仓[品种]
            总数量 = pos.数量 + 数量
            总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
            pos.数量 = 总数量
            pos.平均成本 = 总成本 / 总数量
            pos.当前价格 = 价格
        else:
            new_pos = 持仓数据(品种, 数量, 价格)
            new_pos.当前价格 = 价格
            self.持仓[品种] = new_pos

        self.已实现盈亏 -= 需要资金

        self.交易记录.append({
            "时间": 获取当前时间(),
            "动作": "买入",
            "品种": 品种,
            "价格": 价格,
            "数量": 数量,
            "策略名称": self.当前策略
        })

        try:
            数据库.保存交易记录("买入", 品种, 价格, 数量, 0, self.当前策略)
        except:
            pass

        self._保存持仓到数据库()
        st.success(f"✅ 买入 {品种} {数量}股 @ {价格:.2f}")
        st.rerun()

    def 卖出(self, 品种, 价格, 数量=100, 策略名称=""):
        if 策略名称:
            self.当前策略 = 策略名称

        if 品种 not in self.持仓:
            st.error(f"卖出失败: 没有 {品种} 持仓")
            return

        if self.持仓[品种].数量 < 数量:
            st.error(f"卖出失败: {品种} 持仓不足")
            return

        pos = self.持仓[品种]
        盈亏 = (价格 - pos.平均成本) * 数量
        盈亏率 = (盈亏 / (pos.平均成本 * 数量)) * 100 if pos.平均成本 > 0 else 0

        pos.数量 -= 数量
        self.已实现盈亏 += 价格 * 数量
        pos.已实现盈亏 += 盈亏

        if pos.数量 <= 0:
            del self.持仓[品种]
            try:
                数据库.删除持仓(品种)
            except:
                pass
        else:
            self._保存持仓到数据库()

        self.交易记录.append({
            "时间": 获取当前时间(),
            "动作": "卖出",
            "品种": 品种,
            "价格": 价格,
            "数量": 数量,
            "盈亏": 盈亏,
            "策略名称": self.当前策略
        })

        try:
            数据库.保存交易记录("卖出", 品种, 价格, 数量, 盈亏, self.当前策略)
        except:
            pass

        st.success(f"✅ 卖出 {品种} {数量}股 @ {价格:.2f}, 盈亏: ¥{盈亏:+.2f} ({盈亏率:+.2f}%)")
        st.rerun()
