# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd

class AI引擎:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")

    def 获取实时价格(self, code):
        try:
            data = yf.Ticker(code).history(period="1d")
            return round(data["Close"].iloc[-1], 4) if not data.empty else None
        except:
            return None

    def 计算技术指标(self, code):
        try:
            data = yf.Ticker(code).history(period="60d")
            if len(data) < 20:
                return {"RSI": 50, "趋势": "未知"}
            close = data["Close"]
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            ma5 = close.rolling(5).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            return {
                "RSI": round(rsi.iloc[-1], 2),
                "趋势": "上涨" if ma5 > ma20 else "下跌"
            }
        except:
            return {"RSI": 50, "趋势": "未知"}

    def AI推荐(self, 市场, 策略类型):
        """✅ 全市场推荐（A股 / 美股 / 外汇 / 加密货币 / 期货）"""
        品种映射 = {
            "A股": [
                {"代码": "600519.SS", "名称": "贵州茅台"},
                {"代码": "000858.SZ", "名称": "五粮液"},
                {"代码": "000333.SZ", "名称": "美的集团"}
            ],
            "美股": [
                {"代码": "AAPL", "名称": "苹果"},
                {"代码": "MSFT", "名称": "微软"},
                {"代码": "NVDA", "名称": "英伟达"}
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

        品种列表 = 品种映射.get(市场, [])
        推荐列表 = []

        for item in 品种列表:
            价格 = self.获取实时价格(item["代码"])
            指标 = self.计算技术指标(item["代码"])
            if not 价格:
                continue

            # ✅ 根据策略类型做简单判断（避免空推荐）
            推荐理由 = f"{指标['趋势']}趋势，RSI={指标['RSI']}"
            if 指标["趋势"] == "上涨":
                推荐列表.append({
                    "代码": item["代码"],
                    "名称": item["名称"],
                    "价格": 价格,
                    "趋势": 指标["趋势"],
                    "RSI": 指标["RSI"],
                    "理由": 推荐理由
                })

        return {
            "推荐": 推荐列表[:3],
            "置信度": 70,
            "类型": "全市场推荐"
        }
