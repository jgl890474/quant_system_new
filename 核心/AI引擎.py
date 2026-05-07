# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from 工具 import 数据库

class AI引擎:
    def __init__(self):
        # 直接写死 API Key
        self.api_key = "sk-45427643f729440585233fac41de6be1"
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def 分析(self, 品种, 价格, 策略信号):
        """完整AI分析"""
        
        try:
            # 1. 获取技术指标
            技术指标 = self.获取技术指标(品种)
            
            # 2. 获取多周期分析
            多周期 = self.获取多周期分析(品种)
            
            # 3. 计算风险评分
            风险评分 = self.计算风险评分(品种, 价格, 技术指标)
            
            # 4. 构建提示词
            prompt = self._构建提示词(品种, 价格, 策略信号, 技术指标, 风险评分)
            
            # 调用 API
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.status_code == 200:
                结果 = response.json()
                内容 = 结果["choices"][0]["message"]["content"]
                return self._解析返回(内容)
            else:
                return self._简化分析(品种, 价格, 策略信号, f"API错误: {response.status_code}")
                
        except Exception as e:
            return self._简化分析(品种, 价格, 策略信号, str(e))
    
    def 获取技术指标(self, 品种):
        """计算技术指标"""
        try:
            代码映射 = {
                "AAPL": "AAPL", "BTC-USD": "BTC-USD", "GC=F": "GC=F",
                "EURUSD": "EURUSD=X", "TSLA": "TSLA", "NVDA": "NVDA"
            }
            代码 = 代码映射.get(品种, 品种)
            
            数据 = yf.download(代码, period="3mo", interval="1d", progress=False)
            
            if 数据.empty:
                return {"RSI": 50, "MA5": 0, "MA20": 0, "趋势": "未知"}
            
            收盘价 = 数据['Close']
            
            # RSI
            delta = 收盘价.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            当前RSI = round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else 50
            
            # 均线
            ma5 = round(float(收盘价.rolling(5).mean().iloc[-1]), 2)
            ma20 = round(float(收盘价.rolling(20).mean().iloc[-1]), 2)
            
            # 趋势
            if ma5 > ma20:
                趋势 = "上涨"
            else:
                趋势 = "下跌"
            
            return {
                "RSI": 当前RSI,
                "MA5": ma5,
                "MA20": ma20,
                "趋势": 趋势,
                "当前价格": round(float(收盘价.iloc[-1]), 2)
            }
        except Exception as e:
            return {"RSI": 50, "MA5": 0, "MA20": 0, "趋势": "未知", "error": str(e)}
    
    def 获取多周期分析(self, 品种):
        """多周期分析"""
        try:
            代码映射 = {
                "AAPL": "AAPL", "BTC-USD": "BTC-USD", "GC=F": "GC=F",
                "EURUSD": "EURUSD=X", "TSLA": "TSLA", "NVDA": "NVDA"
            }
            代码 = 代码映射.get(品种, 品种)
            
            数据 = yf.download(代码, period="1mo", interval="1d", progress=False)
            
            if not 数据.empty:
                收盘价 = 数据['Close']
                ma20 = 收盘价.rolling(20).mean()
                return {
                    "日线趋势": "上涨" if 收盘价.iloc[-1] > ma20.iloc[-1] else "下跌",
                    "价格": round(float(收盘价.iloc[-1]), 2)
                }
            return {"日线趋势": "未知"}
        except:
            return {"日线趋势": "未知"}
    
    def 计算风险评分(self, 品种, 价格, 技术指标):
        """计算风险评分"""
        风险分 = 50
        warnings = []
        
        rsi = 技术指标.get("RSI", 50)
        if rsi > 80:
            风险分 += 20
            warnings.append("RSI严重超买")
        elif rsi > 70:
            风险分 += 10
            warnings.append("RSI超买")
        elif rsi < 20:
            风险分 += 20
            warnings.append("RSI严重超卖")
        elif rsi < 30:
            风险分 += 10
            warnings.append("RSI超卖")
        
        if 风险分 >= 70:
            风险等级 = "高风险"
        elif 风险分 >= 50:
            风险等级 = "中风险"
        else:
            风险等级 = "低风险"
        
        return {"风险等级": 风险等级, "风险分数": 风险分, "警告": warnings}
    
    def _构建提示词(self, 品种, 价格, 策略信号, 技术指标, 风险评分):
        return f"""
分析交易：
品种: {品种}
价格: {价格}
策略信号: {策略信号}
RSI: {技术指标.get('RSI', 50)}
趋势: {技术指标.get('趋势', '未知')}
风险: {风险评分.get('风险等级', '中')}

返回JSON: {{"信号": "buy/sell/hold", "置信度": 数字, "理由": "简短理由", "仓位": "轻仓/半仓/重仓"}}
"""
    
    def _解析返回(self, 内容):
        try:
            import re
            json_match = re.search(r'\{[^{}]*\}', 内容)
            if json_match:
                数据 = json.loads(json_match.group())
                return {
                    "最终信号": 数据.get("信号", "hold"),
                    "置信度": 数据.get("置信度", 50),
                    "理由": 数据.get("理由", "分析完成"),
                    "建议仓位": 数据.get("仓位", "轻仓"),
                    "建议仓位比例": 30,
                    "止损价": 0,
                    "止盈价": 0,
                    "风险提示": ""
                }
        except:
            pass
        return self._简化分析("", 0, "", "解析失败")
    
    def _简化分析(self, 品种, 价格, 策略信号, 错误信息=""):
        return {
            "最终信号": 策略信号 if 策略信号 in ["buy", "sell"] else "hold",
            "置信度": 60,
            "理由": f"AI分析: {错误信息}" if 错误信息 else "AI分析完成",
            "建议仓位": "轻仓",
            "建议仓位比例": 30,
            "止损价": 0,
            "止盈价": 0,
            "风险提示": "请检查API配置" if 错误信息 else ""
        }
