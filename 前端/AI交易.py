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
        # 直接写死 API Key（临时测试）
        self.api_key = "sk-45427643f729440585233fac41de6be1"
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 缓存新闻数据
        self.新闻缓存 = {}
        self.新闻更新时间 = None
    
    def 分析(self, 品种, 价格, 策略信号):
        """完整AI分析"""
        
        try:
            # 1. 获取技术指标
            技术指标 = self._获取技术指标(品种)
            
            # 2. 获取多周期分析
            多周期 = self._获取多周期分析(品种)
            
            # 3. 获取新闻情绪
            新闻情绪 = self._获取新闻情绪(品种)
            
            # 4. 计算风险评分
            风险评分 = self._计算风险评分(品种, 价格, 技术指标)
            
            # 5. 构建完整提示词
            prompt = self._构建完整提示词(
                品种, 价格, 策略信号, 
                技术指标, 多周期, 新闻情绪, 风险评分
            )
            
            # 调用 DeepSeek API
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的量化交易AI助手，精通技术分析、基本面分析和风险管理。请根据用户提供的数据，给出专业的交易建议。只返回JSON格式。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800
                },
                timeout=15
            )
            
            if response.status_code == 200:
                结果 = response.json()
                内容 = 结果["choices"][0]["message"]["content"]
                分析结果 = self._解析完整返回(内容)
                
                # 保存原始返回内容
                st.session_state['AI原始返回'] = 内容
                st.session_state['AI原始数据'] = 分析结果
                
                return 分析结果
            else:
                return self._简化分析(品种, 价格, 策略信号, f"API错误: {response.status_code}")
                
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._简化分析(品种, 价格, 策略信号, str(e))
    
    def _获取技术指标(self, 品种):
        """计算技术指标"""
        try:
            代码映射 = {
                "AAPL": "AAPL", "BTC-USD": "BTC-USD", "GC=F": "GC=F",
                "EURUSD": "EURUSD=X", "TSLA": "TSLA", "NVDA": "NVDA"
            }
            代码 = 代码映射.get(品种, 品种)
            
            # 获取历史数据
            数据 = yf.download(代码, period="3mo", interval="1d", progress=False)
            
            if 数据.empty:
                return {"error": "无法获取数据"}
            
            收盘价 = 数据['Close']
            
            # 计算RSI
            delta = 收盘价.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            当前RSI = round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else 50
            
            # 计算MACD
            exp1 = 收盘价.ewm(span=12, adjust=False).mean()
            exp2 = 收盘价.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # 计算均线
            ma5 = round(float(收盘价.rolling(5).mean().iloc[-1]), 2)
            ma10 = round(float(收盘价.rolling(10).mean().iloc[-1]), 2)
            ma20 = round(float(收盘价.rolling(20).mean().iloc[-1]), 2)
            ma60 = round(float(收盘价.rolling(60).mean().iloc[-1]), 2) if len(收盘价) > 60 else ma20
            
            # 判断趋势
            if ma5 > ma10 > ma20:
                趋势 = "多头排列（上涨趋势）"
            elif ma5 < ma10 < ma20:
                趋势 = "空头排列（下跌趋势）"
            else:
                趋势 = "震荡整理"
            
            return {
                "RSI": 当前RSI,
                "MACD": round(float(macd.iloc[-1]), 4),
                "MA5": ma5,
                "MA10": ma10,
                "MA20": ma20,
                "MA60": ma60,
                "趋势": 趋势,
                "当前价格": round(float(收盘价.iloc[-1]), 2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _获取多周期分析(self, 品种):
        """多周期分析"""
        try:
            代码映射 = {
                "AAPL": "AAPL", "BTC-USD": "BTC-USD", "GC=F": "GC=F",
                "EURUSD": "EURUSD=X", "TSLA": "TSLA", "NVDA": "NVDA"
            }
            代码 = 代码映射.get(品种, 品种)
            
            日线数据 = yf.download(代码, period="3mo", interval="1d", progress=False)
            
            result = {}
            if not 日线数据.empty:
                日线收盘 = 日线数据['Close']
                日线MA20 = 日线收盘.rolling(20).mean()
                result["日线"] = {
                    "趋势": "上涨" if 日线收盘.iloc[-1] > 日线MA20.iloc[-1] else "下跌",
                    "价格": round(float(日线收盘.iloc[-1]), 2)
                }
            return result
        except:
            return {}
    
    def _获取新闻情绪(self, 品种):
        """新闻情绪分析"""
        品种名称 = {"AAPL": "苹果", "BTC-USD": "比特币", "GC=F": "黄金", "TSLA": "特斯拉", "NVDA": "英伟达"}
        名称 = 品种名称.get(品种, 品种)
        return {
            "情绪": "中性",
            "分数": 0,
            "摘要": f"当前无重大{名称}相关新闻"
        }
    
    def _计算风险评分(self, 品种, 价格, 技术指标):
        """计算风险评分"""
        风险分 = 50
        warnings = []
        
        if "error" in 技术指标:
            return {"风险等级": "中", "风险分数": 50, "警告": warnings}
        
        rsi = 技术指标.get("RSI", 50)
        if rsi > 80:
            风险分 += 20
            warnings.append("RSI严重超买")
        elif rsi > 70:
            风险分 += 10
            warnings.append("RSI超买区")
        elif rsi < 20:
            风险分 += 20
            warnings.append("RSI严重超卖")
        elif rsi < 30:
            风险分 += 10
            warnings.append("RSI超卖区")
        
        if 风险分 >= 70:
            风险等级 = "高"
        elif 风险分 >= 50:
            风险等级 = "中"
        else:
            风险等级 = "低"
        
        return {"风险等级": 风险等级, "风险分数": 风险分, "警告": warnings}
    
    def _构建完整提示词(self, 品种, 价格, 策略信号, 技术指标, 多周期, 新闻情绪, 风险评分):
        """构建提示词"""
        return f"""
分析交易信息：
品种: {品种}
当前价格: {价格}
策略信号: {策略信号}
技术指标: {技术指标}
风险等级: {风险评分.get('风险等级', '中')}

请返回JSON格式：
{{"最终信号": "buy/sell/hold", "置信度": 0-100, "理由": "分析", "建议仓位": "轻仓/半仓/重仓", "止损价": 数字, "止盈价": 数字, "风险提示": "提示"}}
"""
    
    def _解析完整返回(self, 内容):
        """解析AI返回"""
        try:
            import re
            json_match = re.search(r'\{[^{}]*\}', 内容, re.DOTALL)
            if json_match:
                数据 = json.loads(json_match.group())
                return {
                    "最终信号": 数据.get("最终信号", "hold"),
                    "置信度": 数据.get("置信度", 50),
                    "理由": 数据.get("理由", "分析完成"),
                    "建议仓位": 数据.get("建议仓位", "轻仓"),
                    "止损价": 数据.get("止损价", 0),
                    "止盈价": 数据.get("止盈价", 0),
                    "风险提示": 数据.get("风险提示", "注意风险")
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
            "止损价": 0,
            "止盈价": 0,
            "风险提示": "注意风险控制"
        }
