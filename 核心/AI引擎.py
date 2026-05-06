# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import time


class AI引擎:
    def __init__(self):
        # 优先从 st.secrets 读取，其次从环境变量
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def 分析(self, 品种, 价格, 策略信号):
        """
        调用 DeepSeek API 分析行情并给出交易建议
        返回: {
            "最终信号": "buy" / "sell" / "hold",
            "置信度": 0-100,
            "理由": "分析理由"
        }
        """
        
        # 如果没有配置 API Key，降级为简化模式
        if not self.api_key or self.api_key == "":
            return self._简化分析(品种, 价格, 策略信号)
        
        try:
            # 构建提示词
            prompt = self._构建提示词(品种, 价格, 策略信号)
            
            # 调用 DeepSeek API
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的量化交易AI助手。根据用户提供的品种、价格和策略信号，给出交易建议。只返回JSON格式。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.status_code == 200:
                结果 = response.json()
                内容 = 结果["choices"][0]["message"]["content"]
                return self._解析AI返回(内容)
            else:
                st.warning(f"AI API 调用失败: {response.status_code}，使用简化模式")
                return self._简化分析(品种, 价格, 策略信号)
                
        except requests.exceptions.Timeout:
            st.warning("AI API 超时，使用简化模式")
            return self._简化分析(品种, 价格, 策略信号)
        except Exception as e:
            st.warning(f"AI 分析出错: {e}，使用简化模式")
            return self._简化分析(品种, 价格, 策略信号)
    
    def _构建提示词(self, 品种, 价格, 策略信号):
        """构建发送给 AI 的提示词"""
        return f"""
请分析以下交易信息，并给出交易建议：

品种: {品种}
当前价格: {价格}
策略信号: {策略信号}

请严格按照以下 JSON 格式返回：
{{
    "信号": "buy/sell/hold",
    "置信度": 数字(0-100),
    "理由": "简要分析理由"
}}

注意：
- 如果策略信号是 buy，但价格处于高位，可以考虑 hold
- 如果策略信号是 sell，但价格处于低位，可以考虑 hold
- 综合考虑风险和收益
"""
    
    def _解析AI返回(self, 内容):
        """解析 AI 返回的 JSON"""
        try:
            # 尝试提取 JSON 部分（处理可能的多余文字）
            import re
            json_match = re.search(r'\{[^{}]*\}', 内容)
            if json_match:
                数据 = json.loads(json_match.group())
                return {
                    "最终信号": 数据.get("信号", "hold"),
                    "置信度": 数据.get("置信度", 50),
                    "理由": 数据.get("理由", "AI 分析完成")
                }
        except:
            pass
        
        # 解析失败，返回默认值
        return self._简化分析("", 0, "")
    
    def _简化分析(self, 品种, 价格, 策略信号):
        """当 API 不可用时的简化分析"""
        return {
            "最终信号": 策略信号 if 策略信号 in ["buy", "sell"] else "hold",
            "置信度": 60,
            "理由": "AI 引擎使用简化模式（未配置 API Key 或网络异常）"
        }
