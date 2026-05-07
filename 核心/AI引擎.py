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
        # 从 secrets 读取 API Key
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 缓存新闻数据
        self.新闻缓存 = {}
        self.新闻更新时间 = None
    
    def 分析(self, 品种, 价格, 策略信号):
        """完整AI分析 - 技术指标 + 多周期 + 新闻情绪 + 风险警告 + 仓位建议 + 止损止盈"""
        
        # 如果没有 API Key，使用简化模式
        if not self.api_key:
            return self._简化分析(品种, 价格, 策略信号)
        
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
                
                # 保存AI决策到数据库
                self._保存AI决策(品种, 价格, 策略信号, 分析结果, 技术指标)
                
                return 分析结果
            else:
                return self._简化分析(品种, 价格, 策略信号)
                
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._简化分析(品种, 价格, 策略信号)
    
    def _获取技术指标(self, 品种):
        """计算技术指标：RSI、MACD、均线"""
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
            histogram = macd - signal
            当前MACD = round(float(macd.iloc[-1]), 4) if not pd.isna(macd.iloc[-1]) else 0
            MACD信号 = "金叉" if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2] else "死叉" if macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2] else "震荡"
            
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
            
            # 判断RSI状态
            if 当前RSI > 70:
                RSI状态 = "超买区"
            elif 当前RSI < 30:
                RSI状态 = "超卖区"
            else:
                RSI状态 = "中性区"
            
            return {
                "RSI": 当前RSI,
                "RSI状态": RSI状态,
                "MACD": 当前MACD,
                "MACD信号": MACD信号,
                "MA5": ma5,
                "MA10": ma10,
                "MA20": ma20,
                "MA60": ma60,
                "趋势": 趋势,
                "当前价格": round(float(收盘价.iloc[-1]), 2)
            }
        except Exception as e:
            print(f"技术指标获取失败: {e}")
            return {"error": str(e)}
    
    def _获取多周期分析(self, 品种):
        """多周期分析：日线、小时线"""
        try:
            代码映射 = {
                "AAPL": "AAPL", "BTC-USD": "BTC-USD", "GC=F": "GC=F",
                "EURUSD": "EURUSD=X", "TSLA": "TSLA", "NVDA": "NVDA"
            }
            代码 = 代码映射.get(品种, 品种)
            
            # 日线
            日线数据 = yf.download(代码, period="3mo", interval="1d", progress=False)
            # 小时线
            小时线数据 = yf.download(代码, period="1mo", interval="1h", progress=False)
            
            result = {}
            
            if not 日线数据.empty:
                日线收盘 = 日线数据['Close']
                日线MA20 = 日线收盘.rolling(20).mean()
                result["日线"] = {
                    "趋势": "上涨" if 日线收盘.iloc[-1] > 日线MA20.iloc[-1] else "下跌",
                    "价格": round(float(日线收盘.iloc[-1]), 2),
                    "MA20": round(float(日线MA20.iloc[-1]), 2) if not pd.isna(日线MA20.iloc[-1]) else 0
                }
            
            if not 小时线数据.empty:
                小时线收盘 = 小时线数据['Close']
                小时线MA20 = 小时线收盘.rolling(20).mean()
                result["小时线"] = {
                    "趋势": "上涨" if 小时线收盘.iloc[-1] > 小时线MA20.iloc[-1] else "下跌",
                    "价格": round(float(小时线收盘.iloc[-1]), 2)
                }
            
            return result
        except:
            return {"error": "无法获取多周期数据"}
    
    def _获取新闻情绪(self, 品种):
        """获取新闻情绪分析（使用免费API或模拟）"""
        # 这里使用模拟数据，实际可接入 NewsAPI
        品种新闻映射 = {
            "AAPL": "苹果公司",
            "BTC-USD": "比特币",
            "GC=F": "黄金",
            "TSLA": "特斯拉",
            "NVDA": "英伟达"
        }
        名称 = 品种新闻映射.get(品种, 品种)
        
        # 模拟新闻情绪（实际可接入真实新闻API）
        import random
        random.seed(hash(品种) % 10000)
        情绪分数 = random.uniform(-0.5, 0.5)
        
        if 情绪分数 > 0.2:
            情绪 = "积极"
            摘要 = f"近期关于{名称}的消息整体偏积极，市场情绪乐观"
        elif 情绪分数 < -0.2:
            情绪 = "消极"
            摘要 = f"近期关于{名称}的消息存在一些负面因素，需谨慎"
        else:
            情绪 = "中性"
            摘要 = f"近期关于{名称}的市场消息中性，无明显偏向"
        
        return {
            "情绪": 情绪,
            "分数": round(情绪分数, 2),
            "摘要": 摘要,
            "来源": "新闻聚合分析"
        }
    
    def _计算风险评分(self, 品种, 价格, 技术指标):
        """计算综合风险评分（0-100，越高风险越大）"""
        风险分 = 50  # 基础分
        
        if "error" in 技术指标:
            return {"风险等级": "中", "风险分数": 50, "警告": []}
        
        warnings = []
        
        # RSI风险
        rsi = 技术指标.get("RSI", 50)
        if rsi > 80:
            风险分 += 20
            warnings.append(f"RSI={rsi}，严重超买，回调风险高")
        elif rsi > 70:
            风险分 += 10
            warnings.append(f"RSI={rsi}，超买区，注意回调")
        elif rsi < 20:
            风险分 += 20
            warnings.append(f"RSI={rsi}，严重超卖，可能反弹")
        elif rsi < 30:
            风险分 += 10
            warnings.append(f"RSI={rsi}，超卖区，可能存在反弹机会")
        
        # 趋势风险
        趋势 = 技术指标.get("趋势", "")
        if "下跌" in 趋势:
            风险分 += 15
            warnings.append("价格处于下跌趋势，做多风险较高")
        
        # MACD风险
        macd信号 = 技术指标.get("MACD信号", "")
        if "死叉" in macd信号:
            风险分 += 10
            warnings.append("MACD形成死叉，短期看跌")
        
        # 确定风险等级
        if 风险分 >= 70:
            风险等级 = "高"
        elif 风险分 >= 50:
            风险等级 = "中"
        else:
            风险等级 = "低"
        
        return {
            "风险分数": 风险分,
            "风险等级": 风险等级,
            "警告": warnings
        }
    
    def _构建完整提示词(self, 品种, 价格, 策略信号, 技术指标, 多周期, 新闻情绪, 风险评分):
        """构建完整的AI提示词"""
        
        # 格式化技术指标
        技术指标文本 = f"""
- RSI(14): {技术指标.get('RSI', 'N/A')} ({技术指标.get('RSI状态', 'N/A')})
- MACD: {技术指标.get('MACD', 'N/A')} ({技术指标.get('MACD信号', 'N/A')})
- 均线: MA5={技术指标.get('MA5', 'N/A')}, MA10={技术指标.get('MA10', 'N/A')}, MA20={技术指标.get('MA20', 'N/A')}, MA60={技术指标.get('MA60', 'N/A')}
- 趋势: {技术指标.get('趋势', 'N/A')}
"""
        
        # 格式化多周期
        多周期文本 = ""
        if "日线" in 多周期:
            多周期文本 += f"- 日线: {多周期['日线'].get('趋势', 'N/A')} (价格={多周期['日线'].get('价格', 'N/A')})\n"
        if "小时线" in 多周期:
            多周期文本 += f"- 小时线: {多周期['小时线'].get('趋势', 'N/A')} (价格={多周期['小时线'].get('价格', 'N/A')})\n"
        
        # 格式化风险
        风险文本 = f"""
- 风险等级: {风险评分.get('风险等级', '中')}
- 风险分数: {风险评分.get('风险分数', 50)}/100
- 风险警告: {', '.join(风险评分.get('警告', ['无']))}
"""
        
        return f"""
请分析以下交易信息，给出完整的交易建议：

## 基本信息
- 品种: {品种}
- 当前价格: {价格}
- 策略信号: {策略信号}

## 技术指标分析
{技术指标文本}

## 多周期分析
{多周期文本}

## 新闻情绪
- 市场情绪: {新闻情绪.get('情绪', '中性')}
- 情绪分数: {新闻情绪.get('分数', 0)}
- 摘要: {新闻情绪.get('摘要', '无')}

## 风险评估
{风险文本}

请严格按照以下JSON格式返回：
{{
    "最终信号": "buy/sell/hold",
    "置信度": 数字(0-100),
    "理由": "综合分析理由（100字以内）",
    "建议仓位": "轻仓/半仓/重仓",
    "建议仓位比例": 数字(0-100),
    "止损价": 数字,
    "止盈价": 数字,
    "风险提示": "风险提示内容"
}}

注意：
- 综合所有信息给出专业判断
- 止损价建议设置在支撑位下方
- 止盈价建议设置在阻力位上方
- 根据风险等级调整仓位比例
"""
    
    def _解析完整返回(self, 内容):
        """解析AI返回的完整JSON"""
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
                    "建议仓位比例": 数据.get("建议仓位比例", 30),
                    "止损价": 数据.get("止损价", 0),
                    "止盈价": 数据.get("止盈价", 0),
                    "风险提示": 数据.get("风险提示", "注意风险控制")
                }
        except:
            pass
        return self._简化分析("", 0, "")
    
    def _保存AI决策(self, 品种, 价格, 策略信号, 分析结果, 技术指标):
        """保存AI决策到数据库"""
        try:
            数据库.保存AI决策(
                品种, 价格, 策略信号,
                分析结果.get("最终信号", "hold"),
                分析结果.get("置信度", 50),
                f"仓位: {分析结果.get('建议仓位', 'N/A')}, 止损: {分析结果.get('止损价', 'N/A')}, " + 分析结果.get("理由", "")
            )
        except:
            pass
    
    def _简化分析(self, 品种, 价格, 策略信号):
        """简化分析模式"""
        return {
            "最终信号": 策略信号 if 策略信号 in ["buy", "sell"] else "hold",
            "置信度": 60,
            "理由": "AI 使用简化模式（未配置 API Key）",
            "建议仓位": "轻仓",
            "建议仓位比例": 30,
            "止损价": 0,
            "止盈价": 0,
            "风险提示": "请配置 DeepSeek API Key 获取完整分析"
        }
