# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from 工具 import 数据库


class 订单引擎:
    def __init__(self, 初始资金=100000):
        self.持仓 = {}
        self.交易记录 = []
        self.初始资金 = 初始资金
        self.已实现盈亏 = 0
    
    def 获取总资产(self):
        总值 = self.初始资金
        for pos in self.持仓.values():
            总值 += pos.数量 * pos.当前价格 - pos.数量 * pos.平均成本
        return 总值
    
    def 获取总盈亏(self):
        return self.获取总资产() - self.初始资金
    
    def 买入(self, 品种, 价格, 数量=1000):
        from .数据模型 import 持仓数据
        
        # 执行买入
        if 品种 in self.持仓:
            pos = self.持仓[品种]
            总数量 = pos.数量 + 数量
            总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
            pos.数量 = 总数量
            pos.平均成本 = 总成本 / 总数量
        else:
            self.持仓[品种] = 持仓数据(品种, 数量, 价格)
        
        # 记录交易
        self.交易记录.append({"时间": datetime.now(), "动作": "买入", "品种": 品种, "价格": 价格, "数量": 数量})
        
        # 保存到数据库
        try:
            数据库.保存交易记录("买入", 品种, 价格, 数量, 策略名称=st.session_state.get('当前策略', ''))
        except:
            pass
        
        # 使用 session_state 存储成功消息，避免刷新时丢失
        st.session_state['成功消息'] = f"✅ 买入 {品种} @ {价格:.4f}"
        st.rerun()
    
    def 卖出(self, 品种, 价格, 数量=1000):
        if 品种 in self.持仓 and self.持仓[品种].数量 >= 数量:
            pos = self.持仓[品种]
            盈亏 = (价格 - pos.平均成本) * 数量
            pos.数量 -= 数量
            self.已实现盈亏 += 盈亏
            
            if pos.数量 <= 0:
                del self.持仓[品种]
            
            self.交易记录.append({"时间": datetime.now(), "动作": "卖出", "品种": 品种, "价格": 价格, "数量": 数量, "盈亏": 盈亏})
            
            try:
                数据库.保存交易记录("卖出", 品种, 价格, 数量, 盈亏, st.session_state.get('当前策略', ''))
            except:
                pass
            
            st.session_state['成功消息'] = f"✅ 卖出 {品种} @ {价格:.4f}, 盈亏: ${盈亏:+.2f}"
            st.rerun()
        else:
            st.session_state['错误消息'] = f"❌ 卖出失败: {品种} 持仓不足"
            st.rerun()
