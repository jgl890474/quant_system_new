# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from 工具 import 数据库

def 获取当前时间():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class 订单引擎:
    def __init__(self, 初始资金=100000):
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
                pos.当前价格 = pos.平均成本
                self.持仓[品种] = pos
                self.已实现盈亏 += pos.已实现盈亏
            
            if self.持仓:
                print(f"✅ 从数据库恢复 {len(self.持仓)} 个持仓")
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
    
    def 获取总资产(self):
        """计算总资产 = 初始资金 + 已实现盈亏 + 浮动盈亏"""
        self.更新所有持仓价格()
        
        # 计算浮动盈亏
        浮动盈亏 = 0
        for pos in self.持仓.values():
            浮动盈亏 += pos.数量 * (pos.当前价格 - pos.平均成本)
        
        # 总资产 = 初始资金 + 已实现盈亏 + 浮动盈亏
        总资产 = self.初始资金 + self.已实现盈亏 + 浮动盈亏
        return 总资产
    
    def 获取可用资金(self):
        """可用资金 = 初始资金 + 已实现盈亏 - 已占用资金"""
        已占用资金 = 0
        for pos in self.持仓.values():
            已占用资金 += pos.数量 * pos.平均成本
        return self.初始资金 + self.已实现盈亏 - 已占用资金
    
    def 获取持仓市值(self):
        """持仓市值 = 当前价格 * 数量"""
        市值 = 0
        for pos in self.持仓.values():
            市值 += pos.数量 * pos.当前价格
        return 市值
    
    def 获取总盈亏(self):
        """总盈亏 = 总资产 - 初始资金"""
        return self.获取总资产() - self.初始资金
    
    def 买入(self, 品种, 价格, 数量=1000):
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
        
        # 记录交易
        self.交易记录.append({
            "时间": 获取当前时间(), 
            "动作": "买入", 
            "品种": 品种, 
            "价格": 价格, 
            "数量": 数量
        })
        
        # 保存到数据库
        try:
            数据库.保存交易记录("买入", 品种, 价格, 数量)
        except:
            pass
        self._保存持仓到数据库()
        
        st.session_state['成功消息'] = f"✅ 买入 {品种} @ {价格:.4f}"
        st.rerun()
    
    def 卖出(self, 品种, 价格, 数量=1000):
        """执行卖出"""
        if 品种 in self.持仓 and self.持仓[品种].数量 >= 数量:
            pos = self.持仓[品种]
            盈亏 = (价格 - pos.平均成本) * 数量
            pos.数量 -= 数量
            pos.已实现盈亏 += 盈亏
            self.已实现盈亏 += 盈亏
            
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
            
            st.session_state['成功消息'] = f"✅ 卖出 {品种} @ {价格:.4f}, 盈亏: ${盈亏:+.2f}"
            st.rerun()
        else:
            st.session_state['错误消息'] = f"❌ 卖出失败: {品种} 持仓不足"
            st.rerun()
