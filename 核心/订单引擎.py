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
        
        # 从数据库恢复持仓
        self._恢复持仓()
        
        if 数据库.获取系统参数("初始资金") is None:
            数据库.保存系统参数("初始资金", 初始资金)
        
        # 打印恢复结果
        print(f"📊 订单引擎初始化完成，恢复 {len(self.持仓)} 个持仓")
    
    def _恢复持仓(self):
        """从数据库恢复持仓"""
        try:
            from .数据模型 import 持仓数据 as 持仓类
            
            # 从数据库获取所有持仓
            持仓数据 = 数据库.获取所有持仓()
            
            print(f"📂 从数据库读取到 {len(持仓数据)} 个持仓记录")
            
            for 品种, 数据 in 持仓数据.items():
                pos = 持仓类(品种, 数据['数量'], 数据['平均成本'])
                pos.已实现盈亏 = 数据.get('已实现盈亏', 0)
                
                # 获取实时价格
                try:
                    from 核心 import 行情获取
                    pos.当前价格 = 行情获取.获取价格(品种).价格
                except:
                    pos.当前价格 = pos.平均成本
                
                self.持仓[品种] = pos
                self.已实现盈亏 += pos.已实现盈亏
                print(f"   ✅ 恢复持仓: {品种}, 数量={pos.数量}, 成本={pos.平均成本:.2f}")
                
        except Exception as e:
            print(f"恢复持仓失败: {e}")
    
    def 更新所有持仓价格(self):
        """更新所有持仓的当前价格"""
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
        """保存所有持仓到数据库"""
        for 品种, pos in self.持仓.items():
            数据库.保存持仓(品种, pos.数量, pos.平均成本, pos.已实现盈亏)
        print(f"💾 保存 {len(self.持仓)} 个持仓到数据库")
    
    def 获取占用资金(self):
        """已占用资金 = Σ (数量 × 成本价)"""
        return sum(pos.数量 * pos.平均成本 for pos in self.持仓.values())
    
    def 获取浮动盈亏(self):
        """浮动盈亏 = Σ (数量 × (当前价 - 成本价))"""
        self.更新所有持仓价格()
        return sum(pos.数量 * (pos.当前价格 - pos.平均成本) for pos in self.持仓.values())
    
    def 获取持仓市值(self):
        """持仓市值 = Σ (数量 × 当前价)"""
        self.更新所有持仓价格()
        return sum(pos.数量 * pos.当前价格 for pos in self.持仓.values())
    
    def 获取可用资金(self):
        """可用资金 = 初始资金 - 占用资金 + 已实现盈亏"""
        return self.初始资金 - self.获取占用资金() + self.已实现盈亏
    
    def 获取总资产(self):
        """总资产 = 可用资金 + 持仓市值"""
        return self.获取可用资金() + self.获取持仓市值()
    
    def 获取总盈亏(self):
        """总盈亏 = 浮动盈亏 + 已实现盈亏"""
        return self.获取浮动盈亏() + self.已实现盈亏
    
    def 买入(self, 品种, 价格, 数量=100, 策略名称=""):
        """执行买入"""
        print(f"🔍 [买入] 品种={品种}, 价格={价格}, 数量={数量}, 策略={策略名称}")
        
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
        
        # 计算需要资金
        需要资金 = 价格 * 数量
        可用资金 = self.获取可用资金()
        
        if 需要资金 > 可用资金:
            st.error(f"资金不足！需要 ¥{需要资金:,.0f}，可用 ¥{可用资金:,.0f}")
            return
        
        # 执行买入
        if 品种 in self.持仓:
            pos = self.持仓[品种]
            总数量 = pos.数量 + 数量
            总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
            pos.数量 = 总数量
            pos.平均成本 = 总成本 / 总数量
            pos.当前价格 = 价格
            print(f"📈 更新持仓: {品种}, 新数量={总数量}, 新成本={pos.平均成本:.4f}")
        else:
            new_pos = 持仓数据(品种, 数量, 价格)
            new_pos.当前价格 = 价格
            self.持仓[品种] = new_pos
            print(f"📈 新增持仓: {品种}, 数量={数量}, 成本={价格:.4f}")
        
        # 扣减可用资金
        self.已实现盈亏 -= 需要资金
        
        # 记录交易
        self.交易记录.append({
            "时间": 获取当前时间(),
            "动作": "买入",
            "品种": 品种,
            "价格": 价格,
            "数量": 数量,
            "策略名称": self.当前策略
        })
        
        # 保存到数据库
        数据库.保存交易记录("买入", 品种, 价格, 数量, 0, self.当前策略)
        self._保存持仓到数据库()
        
        st.success(f"✅ 买入 {品种} {数量}股 @ {价格:.2f}")
        st.rerun()
    
    def 卖出(self, 品种, 价格, 数量=100, 策略名称=""):
        """执行卖出"""
        print(f"🔍 [卖出] 品种={品种}, 价格={价格}, 数量={数量}, 策略={策略名称}")
        
        if 策略名称:
            self.当前策略 = 策略名称
        
        if 品种 not in self.持仓:
            st.error(f"卖出失败: 没有 {品种} 持仓")
            return
        
        if self.持仓[品种].数量 < 数量:
            st.error(f"卖出失败: {品种} 持仓不足 (持有: {self.持仓[品种].数量})")
            return
        
        pos = self.持仓[品种]
        
        # 计算盈亏
        盈亏 = (价格 - pos.平均成本) * 数量
        盈亏率 = (盈亏 / (pos.平均成本 * 数量)) * 100 if pos.平均成本 > 0 else 0
        
        # 更新持仓
        pos.数量 -= 数量
        self.已实现盈亏 += 价格 * 数量
        pos.已实现盈亏 += 盈亏
        
        print(f"💰 卖出 {品种}, 盈亏={盈亏:.2f}, 盈亏率={盈亏率:.2f}%")
        
        # 如果持仓清空，删除记录
        if pos.数量 <= 0:
            del self.持仓[品种]
            数据库.删除持仓(品种)
            print(f"🗑️ 删除持仓: {品种}")
        else:
            self._保存持仓到数据库()
        
        # 记录交易
        self.交易记录.append({
            "时间": 获取当前时间(),
            "动作": "卖出",
            "品种": 品种,
            "价格": 价格,
            "数量": 数量,
            "盈亏": 盈亏,
            "策略名称": self.当前策略
        })
        
        # 保存交易记录
        数据库.保存交易记录("卖出", 品种, 价格, 数量, 盈亏, self.当前策略)
        
        st.success(f"✅ 卖出 {品种} {数量}股 @ {价格:.2f}, 盈亏: ¥{盈亏:+.2f} ({盈亏率:+.2f}%)")
        st.rerun()
