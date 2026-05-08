# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import yfinance as yf
import pandas as pd
from datetime import datetime
from 工具 import 数据库
import os

class AI引擎:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 加载市场配置
        self.市场配置 = self._加载市场配置()
    
    def _加载市场配置(self):
        """加载市场配置文件"""
        配置路径 = "配置/市场配置.json"
        if os.path.exists(配置路径):
            with open(配置路径, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
            "A股": {"类型": "股票池", "品种列表": [], "策略": []},
            "美股": {"类型": "股票池", "品种列表": [], "策略": []},
            "外汇": {"类型": "固定品种", "品种列表": [], "策略": []},
            "加密货币": {"类型": "固定品种", "品种列表": [], "策略": []},
            "期货": {"类型": "固定品种", "品种列表": [], "策略": []}
        }
    
    def 获取品种实时数据(self, 品种代码):
        """获取单个品种的实时数据"""
        try:
            股票 = yf.Ticker(品种代码)
            数据 = 股票.history(period="5d")
            if not 数据.empty:
                当前价 = 数据['Close'].iloc[-1]
                成交量 = 数据['Volume'].iloc[-1] if 'Volume' in 数据.columns else 0
                涨跌幅 = (数据['Close'].iloc[-1] - 数据['Close'].iloc[-2]) / 数据['Close'].iloc[-2] * 100 if len(数据) > 1 else 0
                return {
                    "代码": 品种代码,
                    "价格": round(当前价, 4),
                    "涨跌幅": round(涨跌幅, 2),
                    "成交量": int(成交量) if成交量 else 0
                }
        except:
            pass
        return None
    
    def 计算技术指标(self, 品种代码):
        """计算技术指标"""
        try:
            股票 = yf.Ticker(品种代码)
            数据 = 股票.history(period="60d")
            if len(数据) < 20:
                return {}
            
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
                "MA5": round(ma5, 4) if not pd.isna(ma5) else 0,
                "MA20": round(ma20, 4) if not pd.isna(ma20) else 0,
                "趋势": "上涨" if ma5 > ma20 else "下跌"
            }
        except:
            return {}
    
    def 筛选股票池(self, 市场, 策略类型):
        """从股票池中筛选符合条件的股票"""
        配置 = self.市场配置.get(市场, {})
        品种列表 = 配置.get("品种列表", [])
        
        候选品种 = []
        for 品种 in 品种列表:
            实时数据 = self.获取品种实时数据(品种["代码"])
            if not 实时数据:
                continue
            
            技术指标 = self.计算技术指标(品种["代码"])
            
            # 根据策略类型筛选
            if 策略类型 == "量价策略":
                if 实时数据["涨跌幅"] > 1:
                    候选品种.append({**品种, **实时数据, **技术指标})
            elif 策略类型 == "双均线策略":
                if 技术指标.get("趋势") == "上涨":
                    候选品种.append({**品种, **实时数据, **技术指标})
            elif 策略类型 == "动量策略":
                if 实时数据["涨跌幅"] > 0:
                    候选品种.append({**品种, **实时数据, **技术指标})
            else:
                候选品种.append({**品种, **实时数据, **技术指标})
        
        return 候选品种
    
    def 分析固定品种(self, 市场, 策略类型):
        """分析固定品种（外汇/加密货币/期货）"""
        配置 = self.市场配置.get(市场, {})
        品种列表 = 配置.get("品种列表", [])
        
        分析结果 = []
        for 品种 in 品种列表:
            实时数据 = self.获取品种实时数据(品种["代码"])
            if not 实时数据:
                continue
            
            技术指标 = self.计算技术指标(品种["代码"])
            
            # 判断信号
            信号 = "hold"
            if 策略类型 == "外汇利差策略":
                if 技术指标.get("趋势") == "上涨":
                    信号 = "buy"
                elif 技术指标.get("趋势") == "下跌":
                    信号 = "sell"
            elif 策略类型 == "加密双均线":
                if 技术指标.get("趋势") == "上涨":
                    信号 = "buy"
            
            分析结果.append({
                **品种,
                **实时数据,
                **技术指标,
                "信号": 信号
            })
        
        return 分析结果
    
    def AI推荐(self, 市场, 策略类型):
        """AI主入口"""
        配置 = self.市场配置.get(市场, {})
        市场类型 = 配置.get("类型", "固定品种")
        
        if 市场类型 == "股票池":
            # 股票池模式：筛选 + AI推荐
            候选品种 = self.筛选股票池(市场, 策略类型)
            return self._AI推荐股票(候选品种, 策略类型)
        else:
            # 固定品种模式：分析每个品种
            分析结果 = self.分析固定品种(市场, 策略类型)
            return self._AI分析固定品种(分析结果, 策略类型)
    
    def _AI推荐股票(self, 候选品种, 策略类型):
        """AI推荐股票"""
        if not self.api_key or len(候选品种) == 0:
            return {"推荐": 候选品种[:3], "置信度": 60, "类型": "股票池"}
        
        try:
            prompt = f"""
策略: {策略类型}
候选股票: {json.dumps(候选品种, ensure_ascii=False, indent=2)}

请推荐最值得买入的1-3只股票，返回JSON:
{{"推荐": [{"代码": "xxx", "理由": "xxx"}], "置信度": 85}}
"""
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 500},
                timeout=15
            )
            if response.status_code == 200:
                结果 = response.json()
                内容 = 结果["choices"][0]["message"]["content"]
                import re
                json_match = re.search(r'\{[^{}]*\}', 内容, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except:
            pass
        
        return {"推荐": 候选品种[:3], "置信度": 60, "类型": "股票池"}
    
    def _AI分析固定品种(self, 分析结果, 策略类型):
        """AI分析固定品种"""
        return {"分析": 分析结果, "类型": "固定品种"}
