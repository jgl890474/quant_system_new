# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime


class 订单引擎:
    def __init__(self, 初始资金=100000):
        self.持仓 = {}
        self.交易记录 = []
        self.初始资金 = 初始资金
    
    def 买入(self, 品种, 价格, 数量=1000):
        # 获取风控引擎检查
        if '风控引擎' in st.session_state:
            风控 = st.session_state.风控引擎
            总资金 = self.获取总资产()
            允许, 理由 = 风控.检查新交易(品种, "买入", 数量, 价格, self, 总资金)
            if not 允许:
                st.error(理由)
                return
        
        # 延迟导入避免循环依赖
        from .数据模型 import 持仓数据
        
        if 品种 in self.持仓:
            pos = self.持仓[品种]
            总数量 = pos.数量 + 数量
            总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
            pos.数量 = 总数量
            pos.平均成本 = 总成本 / 总数量
        else:
            self.持仓[品种] = 持仓数据(品种, 数量, 价格)
        
        self.交易记录.append({"时间": datetime.now(), "动作": "买入", "品种": 品种, "价格": 价格, "数量": 数量})
        st.success(f"✅ 买入 {品种} @ {价格:.4f}")
        st.rerun()
    
    def 卖出(self, 品种, 价格, 数量=1000):
        if 品种 in self.持仓 and self.持仓[品种].数量 >= 数量:
            pos = self.持仓[品种]
            盈亏 = (价格 - pos.平均成本) * 数量
            pos.数量 -= 数量
            pos.已实现盈亏 += 盈亏
            
            # 更新风控今日盈亏
            if '风控引擎' in st.session_state:
                st.session_state.风控引擎.更新每日盈亏(盈亏)
            
            if pos.数量 <= 0:
                del self.持仓[品种]
            
            self.交易记录.append({"时间": datetime.now(), "动作": "卖出", "品种": 品种, "价格": 价格, "数量": 数量, "盈亏": 盈亏})
            st.success(f"✅ 卖出 {品种} @ {价格:.4f}, 盈亏: ${盈亏:+.2f}")
            st.rerun()
        else:
            st.error(f"❌ 卖出失败: {品种} 持仓不足")
    
    def 获取总资产(self):
        总值 = self.初始资金
        for pos in self.持仓.values():
            总值 += pos.已实现盈亏
            总值 += pos.数量 * pos.当前价格 - pos.数量 * pos.平均成本
        return 总值
    
    def 获取总盈亏(self):
        return self.获取总资产() - self.初始资金
