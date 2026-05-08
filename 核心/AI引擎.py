# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

class AI引擎:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    def 计算技术指标(self, 品种代码):
        """计算RSI和均线"""
        try:
            股票 = yf.Ticker(品种代码)
            数据 = 股票.history(period="60d")
            if len(数据) < 20:
                return {"RSI": 50, "趋势": "未知"}
            
            收盘价 = 数据['Close']
            
            # RSI
            delta = 收盘价.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # 均线
            ma5 = 收盘价.rolling(5).mean().iloc[-1]
            ma20 = 收盘价.rolling(20).mean().iloc[-1]
            
            return {
                "RSI": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else 50,
                "趋势": "上涨" if ma5 > ma20 else "下跌"
            }
        except:
            return {"RSI": 50, "趋势": "未知"}
    
    def 分析(self, 品种, 价格, 策略信号):
        """AI分析"""
        指标 = self.计算技术指标(品种)
        
        结果 = {
            "最终信号": "hold",
            "置信度": 60,
            "理由": f"RSI={指标.get('RSI', 50)}, 趋势={指标.get('趋势', '未知')}",
            "建议仓位": "轻仓",
            "止损价": 0,
            "止盈价": 0,
            "风险提示": ""
        }
        
        if 策略信号 == "buy":
            if 指标.get("趋势") == "上涨":
                结果["最终信号"] = "buy"
                结果["置信度"] = 75
                结果["理由"] = "均线多头排列，技术面看涨"
            else:
                结果["理由"] = "策略信号买入但技术面偏弱"
        elif 策略信号 == "sell":
            if 指标.get("趋势") == "下跌":
                结果["最终信号"] = "sell"
                结果["置信度"] = 75
                结果["理由"] = "均线空头排列，技术面看跌"
            else:
                结果["理由"] = "策略信号卖出但技术面偏强"
        
        return 结果
