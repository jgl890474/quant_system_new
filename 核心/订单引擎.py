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
        
        # 从数据库恢复持仓
        self._恢复持仓()
        
        if 数据库.获取系统参数("初始资金") is None:
            数据库.保存系统参数("初始资金", 初始资金)
    
    def _恢复持仓(self):
        """从数据库恢复持仓"""
        try:
            from .数据模型 import 持仓数据 as 持仓类
            持仓数据 = 数据库.获取所有持仓()
            
            for 品种, 数据 in 持仓数据.items():
                pos = 持仓类(品种, 数据['数量'], 数据['平均成本'])
                pos.已实现盈亏 = 数据.get('已实现盈亏', 0)
                try:
                    from 核心 import 行情获取
                    现价 = 行情获取.获取价格(品种).价格
                    pos.当前价格 = 现价
                except:
                    pos.当前价格 = pos.平均成本
                self.持仓[品种] = pos
                self.已实现盈亏 += pos.已实现盈亏
        except Exception as e:
            print(f"恢复持仓失败: {e}")
    
    def 更新所有持仓价格(self):
        """更新所有持仓的当前价格"""
        try:
            from 核心 import 行情获取
            for 品种, pos in self.持仓.items():
                try:
                    现价 = 行情获取.获取价格(品种).价格
                    pos.当前价格 = 现价
                except:
                    pass
        except:
            pass
    
    def _保存持仓到数据库(self):
        """保存所有持仓到数据库"""
        for 品种, pos in self.持仓.items():
            数据库.保存持仓(品种, pos.数量, pos.平均成本, pos.已实现盈亏)
    
    def 获取占用资金(self):
        """已占用资金 = Σ (数量 × 成本价)"""
        占用 = 0
        for pos in self.持仓.values():
            占用 += pos.数量 * pos.平均成本
        return 占用
    
    def 获取浮动盈亏(self):
        """浮动盈亏 = Σ (数量 × (当前价 - 成本价))"""
        self.更新所有持仓价格()
        浮动 = 0
        for pos in self.持仓.values():
            浮动 += pos.数量 * (pos.当前价格 - pos.平均成本)
        return 浮动
    
    def 获取持仓市值(self):
        """持仓市值 = Σ (数量 × 当前价)"""
        self.更新所有持仓价格()
        市值 = 0
        for pos in self.持仓.values():
            市值 += pos.数量 * pos.当前价格
        return 市值
    
    def 获取可用资金(self):
        """可用资金 = 初始资金 - 占用资金 + 已实现盈亏"""
        return self.初始资金 - self.获取占用资金() + self.已实现盈亏
    
    def 获取总资产(self):
        """总资产 = 可用资金 + 持仓市值"""
        return self.获取可用资金() + self.获取持仓市值()
    
    def 获取总盈亏(self):
        """总盈亏 = 浮动盈亏 + 已实现盈亏"""
        return self.获取浮动盈亏() + self.已实现盈亏
    
    def 买入(self, 品种, 价格, 数量=100):
        """执行买入"""
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
        
        # 计算需要资金
        需要资金 = 价格 * 数量
        
        # 检查可用资金
        可用资金 = self.获取可用资金()
        if 需要资金 > 可用资金:
            st.session_state['错误消息'] = f"❌ 资金不足！需要 ¥{需要资金:,.0f}，可用 ¥{可用资金:,.0f}"
            st.rerun()
            return
        
        # 执行买入
        if 品种 in self.持仓:
            pos = self.持仓[品种]
            总数量 = pos.数量 + 数量
            总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
            pos.数量 = 总数量
            pos.平均成本 = 总成本 / 总数量
            pos.当前价格 = 价格
            print(f"📈 更新持仓: {品种} -> 数量: {总数量}, 成本: {pos.平均成本:.2f}")
        else:
            new_pos = 持仓数据(品种, 数量, 价格)
            new_pos.当前价格 = 价格
            self.持仓[品种] = new_pos
            print(f"📈 新增持仓: {品种} 数量={数量}, 成本={价格:.2f}")
        
        # 扣减可用资金
        self.已实现盈亏 -= 需要资金
        
        self.交易记录.append({
            "时间": 获取当前时间(), 
            "动作": "买入", 
            "品种": 品种, 
            "价格": 价格, 
            "数量": 数量
        })
        
        try:
            数据库.保存交易记录("买入", 品种, 价格, 数量)
            print(f"💾 保存交易记录成功")
        except Exception as e:
            print(f"💾 保存交易记录失败: {e}")
        
        self._保存持仓到数据库()
        
        st.session_state['成功消息'] = f"✅ 买入 {品种} {数量}股 @ {价格:.2f}"
        print(f"✅ 买入成功: {品种} {数量}股 @ {价格:.2f}")
        st.rerun()
    
    def 卖出(self, 品种, 价格, 数量=100):
        """执行卖出"""
        if 品种 not in self.持仓:
            st.session_state['错误消息'] = f"❌ 卖出失败: 没有 {品种} 持仓"
            st.rerun()
            return
        
        if self.持仓[品种].数量 < 数量:
            st.session_state['错误消息'] = f"❌ 卖出失败: {品种} 持仓不足 (持有: {self.持仓[品种].数量}, 请求: {数量})"
            st.rerun()
            return
        
        pos = self.持仓[品种]
        
        # 计算本次盈亏
        盈亏 = (价格 - pos.平均成本) * 数量
        
        # 更新持仓
        pos.数量 -= 数量
        
        # 卖出时增加可用资金
        self.已实现盈亏 += 价格 * 数量
        
        # 记录已实现盈亏
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
            "盈亏": 盈亏
        })
        
        try:
            数据库.保存交易记录("卖出", 品种, 价格, 数量, 盈亏)
        except:
            pass
        
        st.session_state['成功消息'] = f"✅ 卖出 {品种} {数量}股 @ {价格:.2f}, 盈亏: ¥{盈亏:+.2f}"
        st.rerun()
