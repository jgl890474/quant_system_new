# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, date
from 核心 import 行情获取

class 风控引擎:
    def __init__(self, 配置=None):
        self.配置 = 配置 or {}
        
        # 风控参数
        self.止损比例 = self.配置.get("止损比例", 0.02)      # 2%
        self.止盈比例 = self.配置.get("止盈比例", 0.04)      # 4%
        self.移动止损开关 = self.配置.get("移动止损开关", True)
        self.移动止损回撤 = self.配置.get("移动止损回撤", 0.02)  # 2%回撤触发
        self.最大单品种仓位比例 = self.配置.get("最大单品种仓位比例", 0.3)
        self.最大总仓位比例 = self.配置.get("最大总仓位比例", 0.8)
        self.每日最大亏损 = self.配置.get("每日最大亏损", 0.05)
        
        # 移动止损记录 {品种: {"最高价": xx, "止损价": xx}}
        self.移动止损记录 = {}
        
        # 每日统计
        self.今日交易日期 = date.today()
        self.今日盈亏 = 0
        self.今日交易次数 = 0
    
    def 设置止损止盈(self, 品种, 入场价, 方向="long"):
        """为持仓设置止损止盈价位"""
        if 方向 == "long":
            止损价 = 入场价 * (1 - self.止损比例)
            止盈价 = 入场价 * (1 + self.止盈比例)
            self.移动止损记录[品种] = {"最高价": 入场价, "止损价": 止损价}
        else:
            止损价 = 入场价 * (1 + self.止损比例)
            止盈价 = 入场价 * (1 - self.止盈比例)
            self.移动止损记录[品种] = {"最低价": 入场价, "止损价": 止损价}
        
        return {"止损价": round(止损价, 4), "止盈价": round(止盈价, 4)}
    
    def 检查移动止损(self, 品种, 当前价, 方向="long"):
        """检查移动止损"""
        if 品种 not in self.移动止损记录:
            return None
        
        record = self.移动止损记录[品种]
        
        if 方向 == "long":
            # 多头：更新最高价
            if 当前价 > record.get("最高价", 当前价):
                record["最高价"] = 当前价
                # 移动止损价 = 最高价 * (1 - 移动止损回撤)
                new_stop = record["最高价"] * (1 - self.移动止损回撤)
                if new_stop > record.get("止损价", new_stop):
                    record["止损价"] = new_stop
                    return {"触发价": record["止损价"], "类型": "移动止损"}
        else:
            # 空头：更新最低价
            if 当前价 < record.get("最低价", 当前价):
                record["最低价"] = 当前价
                new_stop = record["最低价"] * (1 + self.移动止损回撤)
                if new_stop < record.get("止损价", new_stop):
                    record["止损价"] = new_stop
                    return {"触发价": record["止损价"], "类型": "移动止损"}
        
        return None
    
    def 检查止损止盈(self, 品种, 入场价, 当前价, 方向="long"):
        """检查是否触发止损止盈"""
        if 方向 == "long":
            盈亏率 = (当前价 - 入场价) / 入场价
        else:
            盈亏率 = (入场价 - 当前价) / 入场价
        
        # 检查移动止损
        if self.移动止损开关:
            移动结果 = self.检查移动止损(品种, 当前价, 方向)
            if 移动结果 and 当前价 <= 移动结果["触发价"]:
                return {"触发": True, "类型": "移动止损", "盈亏率": 盈亏率}
        
        # 检查止损
        if 盈亏率 <= -self.止损比例:
            return {"触发": True, "类型": "止损", "盈亏率": 盈亏率}
        
        # 检查止盈
        if 盈亏率 >= self.止盈比例:
            return {"触发": True, "类型": "止盈", "盈亏率": 盈亏率}
        
        return {"触发": False, "类型": None, "盈亏率": 盈亏率}
    
    def 监控持仓(self, 引擎):
        """实时监控所有持仓，自动执行止损止盈"""
        触发列表 = []
        
        for 品种, pos in 引擎.持仓.items():
            # 获取当前价格
            try:
                当前价 = 行情获取.获取价格(品种).价格
                pos.当前价格 = 当前价
            except:
                continue
            
            # 检查止损止盈
            结果 = self.检查止损止盈(品种, pos.平均成本, 当前价, "long")
            
            if 结果["触发"]:
                触发列表.append({
                    "品种": 品种,
                    "类型": 结果["类型"],
                    "盈亏率": 结果["盈亏率"],
                    "当前价": 当前价,
                    "数量": pos.数量
                })
        
        return 触发列表
    
    def 执行自动平仓(self, 引擎):
        """执行自动止损止盈平仓"""
        触发列表 = self.监控持仓(引擎)
        平仓记录 = []
        
        for 触发 in 触发列表:
            品种 = 触发["品种"]
            当前价 = 触发["当前价"]
            数量 = 触发["数量"]
            
            # 执行卖出
            引擎.卖出(品种, 当前价, 数量)
            
            平仓记录.append({
                "时间": datetime.now(),
                "品种": 品种,
                "类型": 触发["类型"],
                "价格": 当前价,
                "盈亏率": f"{触发['盈亏率']*100:.2f}%",
                "数量": 数量
            })
            
            # 清除移动止损记录
            if 品种 in self.移动止损记录:
                del self.移动止损记录[品种]
        
        return 平仓记录
    
    def 检查新交易(self, 品种, 方向, 数量, 价格, 引擎, 总资金):
        """检查新交易是否允许执行"""
        # 每日亏损限制
        if self.今日盈亏 <= -总资金 * self.每日最大亏损:
            return False, f"今日已触发每日亏损限制"
        
        # 单品种仓位限制
        已有持仓 = 引擎.持仓.get(品种)
        if 已有持仓:
            当前持仓金额 = 已有持仓.数量 * 价格
            新总持仓金额 = 当前持仓金额 + 数量 * 价格
        else:
            新总持仓金额 = 数量 * 价格
        
        if 新总持仓金额 > 总资金 * self.最大单品种仓位比例:
            return False, f"单品种仓位超限: {品种}"
        
        # 总仓位限制
        当前总仓位 = 0
        for s, pos in 引擎.持仓.items():
            try:
                当前价 = 行情获取.获取价格(s).价格
                当前总仓位 += pos.数量 * 当前价
            except:
                当前总仓位 += pos.数量 * pos.平均成本
        
        新总仓位 = 当前总仓位 + 数量 * 价格
        
        if 新总仓位 > 总资金 * self.最大总仓位比例:
            return False, f"总仓位超限"
        
        return True, "通过"
    
    def 检查持仓风控(self, 引擎):
        """检查所有持仓是否触发止损/止盈"""
        return self.监控持仓(引擎)
    
    def 执行风控平仓(self, 引擎):
        """自动执行风控平仓"""
        return self.执行自动平仓(引擎)
    
    def 更新每日盈亏(self, 盈亏):
        """更新今日盈亏统计"""
        today = date.today()
        if today != self.今日交易日期:
            # 新的一天，重置统计
            self.今日交易日期 = today
            self.今日盈亏 = 0
            self.今日交易次数 = 0
        
        self.今日盈亏 += 盈亏
        self.今日交易次数 += 1
    
    def 获取风控状态(self, 引擎, 总资金):
        """获取当前风控状态摘要"""
        当前总仓位 = 0
        for s, pos in 引擎.持仓.items():
            try:
                当前价 = 行情获取.获取价格(s).价格
                当前总仓位 += pos.数量 * 当前价
            except:
                当前总仓位 += pos.数量 * pos.平均成本
        
        return {
            "总仓位比例": f"{当前总仓位/总资金*100:.1f}%",
            "最大总仓位限制": f"{self.最大总仓位比例*100}%",
            "单品种仓位限制": f"{self.最大单品种仓位比例*100}%",
            "止损线": f"-{self.止损比例*100}%",
            "止盈线": f"+{self.止盈比例*100}%",
            "移动止损": "开启" if self.移动止损开关 else "关闭",
            "移动止损回撤": f"{self.移动止损回撤*100}%",
            "今日盈亏": self.今日盈亏,
            "今日交易次数": self.今日交易次数,
            "每日亏损上限": f"-{self.每日最大亏损*100}%"
        }
