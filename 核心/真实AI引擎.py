# -*- coding: utf-8 -*-
"""
真实AI引擎 - DeepSeek API 集成
功能：技术分析、情绪分析、综合分析
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class 真实AI引擎:
    """真实AI分析引擎"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk-c9a16385ae9644c1b5f13c7c519eebde"
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def 技术分析(self, 品种代码: str, 技术指标: Dict, 价格: float = None) -> Dict:
        """使用AI进行技术分析"""
        prompt = f"""
你是一位资深量化交易分析师。请对{品种代码}进行技术分析。

当前技术数据：
- 当前价格: {price}
- 趋势: {技术指标.get('趋势', '未知')}
- RSI: {技术指标.get('RSI', 50)}
- MACD状态: {技术指标.get('MACD状态', '中性')}
- 布林带信号: {技术指标.get('布林带信号', '正常')}
- 成交量比率: {技术指标.get('成交量比率', 1)}

请分析并返回JSON格式：
{{
    "形态": "形态描述",
    "趋势判断": "看涨/看跌/震荡",
    "交易建议": "买入/卖出/持有",
    "置信度": 0-100,
    "理由": "详细理由"
}}
"""
        return self._调用AI(prompt)
    
    def 综合分析(self, 品种代码: str, 技术数据: Dict, 
                  情绪数据: Dict = None) -> Dict:
        """综合分析：技术面 + 情绪面"""
        prompt = f"""
你是一位顶级量化交易策略师。请对{品种代码}进行全面分析。

【技术面数据】
{json.dumps(技术数据, ensure_ascii=False, indent=2)}

【情绪面数据】
{json.dumps(情绪数据 or {}, ensure_ascii=False, indent=2)}

请输出完整的交易决策，返回JSON格式：
{{
    "综合评分": 0-100,
    "交易决策": "买入/卖出/持有",
    "置信度": 0-100,
    "建议仓位": 0-100,
    "止损位": 0,
    "止盈目标1": 0,
    "止盈目标2": 0,
    "风险等级": "低/中/高",
    "分析总结": "总结内容"
}}
"""
        return self._调用AI(prompt)
    
    def _调用AI(self, prompt: str, 超时秒数: int = 30) -> Dict:
        """调用DeepSeek API"""
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是专业的量化交易AI分析师，只返回JSON格式结果。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                },
                timeout=超时秒数
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"AI调用失败: {e}")
        
        return self._降级分析()
    
    def _降级分析(self) -> Dict:
        """API失败时的降级分析"""
        return {
            "综合评分": 50,
            "交易决策": "持有",
            "置信度": 50,
            "建议仓位": 10,
            "风险等级": "中",
            "分析总结": "AI服务暂时不可用，使用本地规则",
            "降级模式": True
        }


# 全局实例
_真实AI = None

def 获取真实AI():
    global _真实AI
    if _真实AI is None:
        _真实AI = 真实AI引擎()
    return _真实AI
