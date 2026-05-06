# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, date


class 风控引擎:
    def __init__(self, 配置=None):
        """
        初始化风控引擎
        """
        self.配置 = 配置 or {}
        # 临时禁用仓位限制（改成100%）
        self.最大单品种仓位比例 = self.配置.get("最大单品种仓位比例", 1.0)   # 原来是0.3
        self.最大总仓位比例 = self.配置.get("最大总仓位比例", 1.0)         # 原来是0.8
        self.止损比例 = self.配置.get("止损比例", 0.02)
        self.止盈比例 = self.配置.get("止盈比例", 0.04)
        self.每日最大亏损 = self.配置.get("每日最大亏损", 0.05)
        
        # 每日统计
        self.今日交易日期 = date.today()
        self.今日盈亏 = 0
        self.今日交易次数 = 0
