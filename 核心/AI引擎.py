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
        # 使用你提供的 API Key
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
                
                # 保存原始返回内容到 session_state
                st.session_state['AI原始返回'] = 内容
                st.session_state['AI原始数据'] = 分析结果
                
                # 保存AI决策到数据库
                self._保存AI决策(品种, 价格, 策略信号, 分析结果, 技术指标)
                
                return 分析结果
            else:
                return self._简化分析(品种, 价格, 策略信号, f"API错误: {response.status_code}")
                
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._简化分析(品种, 价格, 策略信号, str(e))
    
    # ... 中间的方法保持不变（_获取技术指标、_获取多周期分析、_获取新闻情绪、_计算风险评分、_构建完整提示词）
    
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
        return self._简化分析("", 0, "", "解析失败")
    
    def _简化分析(self, 品种, 价格, 策略信号, 错误信息=""):
        """简化分析模式"""
        return {
            "最终信号": 策略信号 if 策略信号 in ["buy", "sell"] else "hold",
            "置信度": 60,
            "理由": f"AI 使用简化模式（{错误信息}）" if 错误信息 else "AI 使用简化模式",
            "建议仓位": "轻仓",
            "建议仓位比例": 30,
            "止损价": 0,
            "止盈价": 0,
            "风险提示": "请检查 API 配置"
        }
    
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
