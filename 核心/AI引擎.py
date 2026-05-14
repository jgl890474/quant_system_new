# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import numpy as np

class AI引擎:
    def __init__(self):
        self.api_key = "sk-c9a16385ae9644c1b5f13c7c519eebde"
    
    def 获取实时价格(self, code):
        try:
            ticker = yf.Ticker(code)
            data = ticker.history(period="1d")
            return data["Close"].iloc[-1] if not data.empty else None
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
        品种池 = {
            "A股": [
                {"代码": "600519.SS", "名称": "贵州茅台"},
                {"代码": "000858.SZ", "名称": "五粮液"},
                {"代码": "000333.SZ", "名称": "美的集团"},
            ],
            "美股": [
                {"代码": "AAPL", "名称": "苹果"},
                {"代码": "MSFT", "名称": "微软"},
            ],
            "加密货币": [
                {"代码": "BTC-USD", "名称": "比特币"},
                {"代码": "ETH-USD", "名称": "以太坊"},
            ]
        }
        品种列表 = 品种池.get(市场, [])
        打分结果 = []
        for item in 品种列表:
            价格 = self.获取实时价格(item["代码"])
            指标 = self.计算技术指标(item["代码"])
            if not 价格:
                continue
            得分 = 0
            if 指标["趋势"] == "上涨":
                得分 += 3
            if 指标["RSI"] < 40:
                得分 += 2
            打分结果.append({
                "代码": item["代码"],
                "名称": item["名称"],
                "价格": round(价格, 4),
                "趋势": 指标["趋势"],
                "RSI": 指标["RSI"],
                "得分": 得分,
                "理由": f"{指标['趋势']}趋势 | RSI={指标['RSI']}"
            })
        打分结果.sort(key=lambda x: x["得分"], reverse=True)
        return {"推荐": 打分结果[:5], "置信度": 80, "类型": "策略打分推荐"}
    
    def 获取完整技术指标(self, code):
        """获取完整技术指标"""
        try:
            from 核心.技术指标 import 获取指标计算器
            import yfinance as yf
            
            ticker = yf.Ticker(code)
            df = ticker.history(period="120d")
            
            if df.empty:
                return {}
            
            calc = 获取指标计算器()
            return {
                '趋势': calc.计算趋势指标(df),
                'MACD': calc.计算MACD(df),
                '布林带': calc.计算布林带(df),
                'RSI': calc.计算RSI(df),
                'KDJ': calc.计算KDJ(df),
                '成交量': calc.计算成交量指标(df)
            }
        except Exception as e:
            print(f"获取技术指标失败: {e}")
            return {}
    
    def 智能推荐增强版(self, 市场, 策略类型, use_ai=True):
        """增强版推荐"""
        return self.AI推荐(市场, 策略类型)


def 获取AI引擎():
    return AI引擎()
