# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

class AI引擎:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    def 获取实时价格(self, 品种代码):
        """获取单个品种的实时价格"""
        try:
            股票 = yf.Ticker(品种代码)
            数据 = 股票.history(period="1d")
            if not 数据.empty:
                return round(数据['Close'].iloc[-1], 2)
        except:
            pass
        return None
    
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
    
    def AI推荐(self, 市场, 策略类型):
        """AI推荐股票/品种（带实时价格）"""
        # 定义各市场的品种列表
        市场品种 = {
            "A股": [
                {"代码": "600519.SS", "名称": "贵州茅台"},
                {"代码": "000858.SZ", "名称": "五粮液"},
                {"代码": "000333.SZ", "名称": "美的集团"},
                {"代码": "300750.SZ", "名称": "宁德时代"}
            ],
            "美股": [
                {"代码": "AAPL", "名称": "苹果"},
                {"代码": "MSFT", "名称": "微软"},
                {"代码": "GOOGL", "名称": "谷歌"},
                {"代码": "TSLA", "名称": "特斯拉"}
            ],
            "外汇": [
                {"代码": "EURUSD=X", "名称": "欧元/美元"},
                {"代码": "GBPUSD=X", "名称": "英镑/美元"}
            ],
            "加密货币": [
                {"代码": "BTC-USD", "名称": "比特币"},
                {"代码": "ETH-USD", "名称": "以太坊"}
            ],
            "期货": [
                {"代码": "GC=F", "名称": "黄金期货"},
                {"代码": "CL=F", "名称": "原油期货"}
            ]
        }
        
        品种列表 = 市场品种.get(市场, [])
        推荐列表 = []
        
        for 品种 in 品种列表:
            try:
                实时价格 = self.获取实时价格(品种["代码"])
                指标 = self.计算技术指标(品种["代码"])
                
                if 实时价格:
                    推荐列表.append({
                        "代码": 品种["代码"],
                        "名称": 品种["名称"],
                        "价格": 实时价格,
                        "涨跌幅": 0,
                        "RSI": 指标.get("RSI", 50),
                        "趋势": 指标.get("趋势", "未知"),
                        "理由": f"价格: ${实时价格:.2f}, RSI={指标.get('RSI', 50)}, 趋势={指标.get('趋势', '未知')}"
                    })
            except:
                continue
        
        return {
            "推荐": 推荐列表[:3],
            "置信度": 70,
            "类型": "股票池" if 市场 in ["A股", "美股"] else "固定品种"
        }
    
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
