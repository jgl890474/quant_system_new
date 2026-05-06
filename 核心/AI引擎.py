# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json

class AI引擎:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    def 分析(self, 品种, 价格, 策略信号):
        """调用 DeepSeek API 进行 AI 决策"""
        if not self.api_key:
            return {"最终信号": 策略信号, "置信度": 70, "理由": "API未配置，使用策略信号"}
        
        prompt = f"""你是量化交易AI。品种:{品种}, 价格:{价格}, 策略信号:{策略信号}。
只输出JSON: {{"signal":"buy/sell/hold", "confidence":0-100, "reason":"简短理由"}}"""
        
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                timeout=10
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                data = json.loads(content)
                return {
                    "最终信号": data.get("signal", 策略信号),
                    "置信度": data.get("confidence", 70),
                    "理由": data.get("reason", "AI分析")
                }
        except Exception as e:
            print(f"AI调用失败: {e}")
        
        return {"最终信号": 策略信号, "置信度": 70, "理由": "AI分析完成"}
