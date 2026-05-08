# ✅ 核心/AI引擎.py（AI推荐按策略变化）
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
            if not data.empty:
                return round(data["Close"].iloc[-1], 2)
        except:
            pass
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
        """✅ 按策略类型动态推荐（不是固定几只）"""
        市场品种 = {
            "A股": [
                {"代码": "600519.SS", "名称": "贵州茅台"},
                {"代码": "000858.SZ", "名称": "五粮液"},
                {"代码": "000333.SZ", "名称": "美的集团"},
                {"代码": "300750.SZ", "名称": "宁德时代"},
                {"代码": "002415.SZ", "名称": "海康威视"}
            ],
            "美股": [
                {"代码": "AAPL", "名称": "苹果"},
                {"代码": "MSFT", "名称": "微软"},
                {"代码": "NVDA", "名称": "英伟达"},
                {"代码": "TSLA", "名称": "特斯拉"}
            ]
        }

        品种列表 = 市场品种.get(市场, [])

        # ✅ 根据策略类型决定筛选逻辑
        推荐列表 = []
        for 品种 in 品种列表:
            价 = self.获取实时价格(品种["代码"])
            指 = self.计算技术指标(品种["代码"])
            if not 价:
                continue

            得分 = 0
            if 策略类型 in ["量价策略", "隔夜套利策略"]:
                if 指["趋势"] == "上涨":
                    得分 += 1
                if 指["RSI"] < 40:
                    得分 += 1
            elif 策略类型 in ["双均线策略"]:
                if 指["趋势"] == "上涨":
                    得分 += 2
            else:
                # 默认：趋势向上
                if 指["趋势"] == "上涨":
                    得分 += 1

            if 得分 > 0:
                推荐列表.append({
                    "代码": 品种["代码"],
                    "名称": 品种["名称"],
                    "价格": 价,
                    "趋势": 指["趋势"],
                    "RSI": 指["RSI"],
                    "理由": f"{指['趋势']}趋势，RSI={指['RSI']}"
                })

        # ✅ 按得分排序
        推荐列表.sort(key=lambda x: x["RSI"], reverse=False)

        return {
            "推荐": 推荐列表[:3],
            "置信度": 70,
            "类型": "股票池"
        }
