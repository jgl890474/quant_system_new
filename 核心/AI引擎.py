# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json

class AI引擎:
    def __init__(self):
        # 从 secrets 读取 API Key
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def 分析(self, 品种, 价格, 策略信号):
        """AI 分析行情"""
        
        # 如果没有 API Key，使用简化模式
        if not self.api_key:
            return self._简化分析(品种, 价格, 策略信号)
        
        try:
            prompt = f"""
            分析以下交易信息：
            品种: {品种}
            当前价格: {价格}
            策略信号: {策略信号}
            
            请返回JSON格式：
            {{"信号": "buy/sell/hold", "置信度": 0-100, "理由": "分析理由"}}
            """
            
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=10
            )
            
            if response.status_code == 200:
                结果 = response.json()
                内容 = 结果["choices"][0]["message"]["content"]
                return self._解析返回(内容)
            else:
                return self._简化分析(品种, 价格, 策略信号)
                
        except:
            return self._简化分析(品种, 价格, 策略信号)
    
    def _解析返回(self, 内容):
        try:
            import re
            json_match = re.search(r'\{[^{}]*\}', 内容)
            if json_match:
                数据 = json.loads(json_match.group())
                return {
                    "最终信号": 数据.get("信号", "hold"),
                    "置信度": data.get("置信度", 50),
                    "理由": data.get("理由", "分析完成")
                }
        except:
            pass
        return self._简化分析("", 0, "")
    
    def _简化分析(self, 品种, 价格, 策略信号):
        return {
            "最终信号": 策略信号 if 策略信号 in ["buy", "sell"] else "hold",
            "置信度": 60,
            "理由": "AI 使用简化模式（未配置 API Key）"
        }
