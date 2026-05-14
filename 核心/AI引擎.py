# -*- coding: utf-8 -*-
"""
AI交易引擎 - 完整版
功能：
- DeepSeek API 集成（真实AI分析）
- 多策略动态打分推荐
- 交易信号生成
- 风险评估
- 市场分析
- 仓位建议

优化：
- 支持多种AI模型（DeepSeek/OpenAI）
- 缓存机制
- 错误处理和降级
- 批量分析
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import OrderedDict

# ==================== 配置 ====================
# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-c9a16385ae9644c1b5f13c7c519eebde"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 缓存配置
缓存数据 = {}
缓存时间 = {}
缓存秒数 = 300  # 5分钟缓存


# ==================== AI引擎类 ====================
class AI引擎:
    """AI交易引擎 - 支持DeepSeek API和本地分析"""
    
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.使用真实AI = True  # 是否使用真实AI API
        
        # 品种池配置
        self.品种池 = {
            "A股": [
                {"代码": "600519.SS", "名称": "贵州茅台", "类型": "白酒"},
                {"代码": "000858.SZ", "名称": "五粮液", "类型": "白酒"},
                {"代码": "000333.SZ", "名称": "美的集团", "类型": "家电"},
                {"代码": "300750.SZ", "名称": "宁德时代", "类型": "新能源"},
                {"代码": "002415.SZ", "名称": "海康威视", "类型": "科技"},
                {"代码": "600036.SS", "名称": "招商银行", "类型": "银行"},
                {"代码": "601318.SS", "名称": "中国平安", "类型": "保险"},
                {"代码": "002594.SZ", "名称": "比亚迪", "类型": "汽车"},
            ],
            "美股": [
                {"代码": "AAPL", "名称": "苹果", "类型": "科技"},
                {"代码": "MSFT", "名称": "微软", "类型": "科技"},
                {"代码": "NVDA", "名称": "英伟达", "类型": "芯片"},
                {"代码": "TSLA", "名称": "特斯拉", "类型": "汽车"},
                {"代码": "GOOGL", "名称": "谷歌", "类型": "科技"},
                {"代码": "AMZN", "名称": "亚马逊", "类型": "电商"},
                {"代码": "META", "名称": "Meta", "类型": "社交"},
                {"代码": "NFLX", "名称": "奈飞", "类型": "流媒体"},
            ],
            "加密货币": [
                {"代码": "BTC-USD", "名称": "比特币", "类型": "主流币"},
                {"代码": "ETH-USD", "名称": "以太坊", "类型": "主流币"},
                {"代码": "BNB-USD", "名称": "币安币", "类型": "平台币"},
                {"代码": "SOL-USD", "名称": "Solana", "类型": "公链"},
                {"代码": "DOGE-USD", "名称": "狗狗币", "类型": "meme币"},
                {"代码": "XRP-USD", "名称": "瑞波币", "类型": "支付"},
            ],
            "外汇": [
                {"代码": "EURUSD=X", "名称": "欧元/美元", "类型": "主要货币"},
                {"代码": "GBPUSD=X", "名称": "英镑/美元", "类型": "主要货币"},
                {"代码": "USDJPY=X", "名称": "美元/日元", "类型": "主要货币"},
                {"代码": "AUDUSD=X", "名称": "澳元/美元", "类型": "商品货币"},
            ],
            "期货": [
                {"代码": "GC=F", "名称": "黄金期货", "类型": "贵金属"},
                {"代码": "CL=F", "名称": "原油期货", "类型": "能源"},
                {"代码": "SI=F", "名称": "白银期货", "类型": "贵金属"},
            ]
        }
    
    def _获取缓存(self, key: str) -> Any:
        """获取缓存数据"""
        if key in 缓存数据 and key in 缓存时间:
            if time.time() - 缓存时间[key] < 缓存秒数:
                return 缓存数据[key]
        return None
    
    def _设置缓存(self, key: str, value: Any):
        """设置缓存数据"""
        缓存数据[key] = value
        缓存时间[key] = time.time()
    
    def 获取实时价格(self, code: str) -> Optional[float]:
        """获取实时价格（带缓存）"""
        缓存key = f"price_{code}"
        缓存结果 = self._获取缓存(缓存key)
        if 缓存结果 is not None:
            return 缓存结果
        
        try:
            ticker = yf.Ticker(code)
            data = ticker.history(period="1d")
            if not data.empty:
                price = float(data["Close"].iloc[-1])
                self._设置缓存(缓存key, price)
                return price
        except Exception as e:
            print(f"获取价格失败 {code}: {e}")
        
        return None
    
    def 批量获取价格(self, 代码列表: List[str]) -> Dict[str, float]:
        """批量获取价格"""
        results = {}
        for code in 代码列表:
            price = self.获取实时价格(code)
            if price:
                results[code] = price
            time.sleep(0.1)  # 避免请求过快
        return results
    
    def 计算技术指标(self, code: str, 周期: int = 60) -> Dict:
        """
        计算技术指标
        
        返回:
            RSI, 趋势, MA5, MA20, 波动率, 成交量变化等
        """
        缓存key = f"indicator_{code}"
        缓存结果 = self._获取缓存(缓存key)
        if 缓存结果 is not None:
            return 缓存结果
        
        try:
            data = yf.Ticker(code).history(period=f"{周期}d")
            if len(data) < 20:
                return {"RSI": 50, "趋势": "未知", "波动率": 0, "MA5": 0, "MA20": 0}
            
            close = data["Close"]
            volume = data["Volume"]
            
            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # 移动平均线
            ma5 = close.rolling(5).mean()
            ma20 = close.rolling(20).mean()
            ma60 = close.rolling(60).mean()
            
            # 波动率（年化）
            returns = close.pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) * 100
            
            # 成交量变化
            vol_ma5 = volume.rolling(5).mean()
            volume_ratio = volume.iloc[-1] / vol_ma5.iloc[-1] if vol_ma5.iloc[-1] > 0 else 1
            
            # 趋势判断
            if ma5.iloc[-1] > ma20.iloc[-1] and ma20.iloc[-1] > ma60.iloc[-1]:
                趋势 = "强势上涨"
            elif ma5.iloc[-1] > ma20.iloc[-1]:
                趋势 = "上涨"
            elif ma5.iloc[-1] < ma20.iloc[-1] and ma20.iloc[-1] < ma60.iloc[-1]:
                趋势 = "强势下跌"
            elif ma5.iloc[-1] < ma20.iloc[-1]:
                趋势 = "下跌"
            else:
                趋势 = "震荡"
            
            result = {
                "RSI": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else 50,
                "趋势": 趋势,
                "MA5": round(ma5.iloc[-1], 2),
                "MA20": round(ma20.iloc[-1], 2),
                "波动率": round(volatility, 2),
                "成交量比率": round(volume_ratio, 2),
                "数据量": len(data)
            }
            
            self._设置缓存(缓存key, result)
            return result
            
        except Exception as e:
            print(f"计算指标失败 {code}: {e}")
            return {"RSI": 50, "趋势": "未知", "波动率": 0, "MA5": 0, "MA20": 0}
    
    def 计算综合得分(self, 品种: Dict, 指标: Dict, 策略类型: str) -> Dict:
        """
        计算品种综合得分
        
        参数:
            品种: 品种信息（代码、名称、类型）
            指标: 技术指标
            策略类型: 策略类型
        
        返回:
            得分详情
        """
        得分 = 0
        得分明细 = []
        
        # 1. 趋势得分 (0-40分)
        if 指标["趋势"] == "强势上涨":
            得分 += 40
            得分明细.append("强势上涨+40")
        elif 指标["趋势"] == "上涨":
            得分 += 30
            得分明细.append("上涨趋势+30")
        elif 指标["趋势"] == "震荡":
            得分 += 15
            得分明细.append("震荡+15")
        elif 指标["趋势"] == "下跌":
            得分 += 5
            得分明细.append("下跌+5")
        else:
            得分明细.append("强势下跌+0")
        
        # 2. RSI得分 (0-25分)
        rsi = 指标["RSI"]
        if rsi < 30:
            得分 += 25
            得分明细.append(f"RSI超卖{rsi}+25")
        elif rsi < 40:
            得分 += 20
            得分明细.append(f"RSI偏低{rsi}+20")
        elif rsi > 70:
            得分 += 5
            得分明细.append(f"RSI超买{rsi}+5")
        elif rsi > 80:
            得分 += 0
            得分明细.append(f"RSI过热{rsi}+0")
        else:
            得分 += 15
            得分明细.append(f"RSI正常{rsi}+15")
        
        # 3. 波动率得分 (0-15分)
        波动率 = 指标["波动率"]
        if 30 < 波动率 < 60:
            得分 += 15
            得分明细.append(f"波动率适中{波动率}+15")
        elif 波动率 <= 30:
            得分 += 10
            得分明细.append(f"波动率较低{波动率}+10")
        else:
            得分 += 5
            得分明细.append(f"波动率较高{波动率}+5")
        
        # 4. 成交量得分 (0-20分)
        成交量比率 = 指标["成交量比率"]
        if 成交量比率 > 1.5:
            得分 += 20
            得分明细.append(f"放量{成交量比率}+20")
        elif 成交量比率 > 1.2:
            得分 += 15
            得分明细.append(f"温和放量{成交量比率}+15")
        elif 成交量比率 < 0.5:
            得分 += 0
            得分明细.append(f"缩量{成交量比率}+0")
        else:
            得分 += 10
            得分明细.append(f"成交量正常{成交量比率}+10")
        
        # 5. 策略类型加成 (0-20分)
        if 策略类型 == "量价策略":
            if 指标["成交量比率"] > 1.2 and 指标["趋势"] in ["上涨", "强势上涨"]:
                得分 += 20
                得分明细.append("量价齐升+20")
        elif 策略类型 == "超跌反弹策略":
            if 指标["RSI"] < 30:
                得分 += 20
                得分明细.append("超跌反弹+20")
        elif 策略类型 == "突破策略":
            if 指标["成交量比率"] > 1.5 and 指标["趋势"] in ["上涨", "强势上涨"]:
                得分 += 20
                得分明细.append("放量突破+20")
        elif 策略类型 == "趋势跟踪策略":
            if 指标["趋势"] in ["上涨", "强势上涨"]:
                得分 += 20
                得分明细.append("趋势向上+20")
        elif 策略类型 in ["加密双均线", "期货趋势策略"]:
            if 指标["趋势"] in ["上涨", "强势上涨"]:
                得分 += 15
                得分明细.append("趋势配合+15")
        
        return {
            "得分": 得分,
            "得分明细":得分明细,
            "趋势": 指标["趋势"],
            "RSI": 指标["RSI"],
            "波动率": 指标["波动率"],
            "成交量比率": 指标["成交量比率"]
        }
    
    def AI推荐(self, 市场: str, 策略类型: str, 使用真实AI: bool = True) -> Dict:
        """
        AI推荐品种（核心方法）
        
        参数:
            市场: A股/美股/加密货币/外汇/期货
            策略类型: 策略类型
            使用真实AI: 是否使用DeepSeek API
        
        返回:
            推荐结果
        """
        品种列表 = self.品种池.get(市场, [])
        
        if not 品种列表:
            return {"推荐": [], "置信度": 0, "类型": "无推荐"}
        
        # 尝试使用真实AI API
        if 使用真实AI and self.api_key:
            ai_result = self._调用DeepSeekAPI(市场, 策略类型, 品种列表)
            if ai_result and ai_result.get("推荐"):
                return ai_result
        
        # 降级：使用本地打分算法
        return self._本地打分推荐(品种列表, 策略类型)
    
    def _调用DeepSeekAPI(self, 市场: str, 策略类型: str, 品种列表: List) -> Optional[Dict]:
        """调用DeepSeek API进行推荐"""
        try:
            # 构建品种信息
            品种信息 = []
            for item in 品种列表[:10]:  # 限制数量
                价格 = self.获取实时价格(item["代码"])
                指标 = self.计算技术指标(item["代码"])
                品种信息.append({
                    "代码": item["代码"],
                    "名称": item["名称"],
                    "价格": 价格,
                    "RSI": 指标.get("RSI"),
                    "趋势": 指标.get("趋势")
                })
            
            prompt = f"""
你是一个专业的量化交易AI助手。请分析以下{市场}品种，为{策略类型}策略推荐最佳买入标的。

品种数据：
{json.dumps(品种信息, ensure_ascii=False, indent=2)}

请返回JSON格式，包含：
- recommendations: 推荐列表（最多5个），每个包含 code, name, score(0-100), reason
- market_analysis: 市场整体分析
- risk_warning: 风险提示

只返回JSON，不要有其他内容。
"""
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    
                    # 格式化推荐结果
                    推荐列表 = []
                    for rec in data.get('recommendations', []):
                        推荐列表.append({
                            "代码": rec.get('code'),
                            "名称": rec.get('name'),
                            "价格": self.获取实时价格(rec.get('code')),
                            "得分": rec.get('score', 50),
                            "理由": rec.get('reason', ''),
                            "来源": "DeepSeek AI"
                        })
                    
                    return {
                        "推荐": 推荐列表,
                        "置信度": 85,
                        "类型": "DeepSeek AI推荐",
                        "市场分析": data.get('market_analysis', ''),
                        "风险提示": data.get('risk_warning', '')
                    }
            
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
        
        return None
    
    def _本地打分推荐(self, 品种列表: List, 策略类型: str) -> Dict:
        """本地打分推荐（降级方案）"""
        打分结果 = []
        
        for item in 品种列表:
            价格 = self.获取实时价格(item["代码"])
            if not 价格:
                continue
            
            指标 = self.计算技术指标(item["代码"])
            得分详情 = self.计算综合得分(item, 指标, 策略类型)
            
            打分结果.append({
                "代码": item["代码"],
                "名称": item["名称"],
                "类型": item.get("类型", ""),
                "价格": round(价格, 2),
                "趋势": 得分详情["趋势"],
                "RSI": 得分详情["RSI"],
                "波动率": 得分详情["波动率"],
                "成交量比率": 得分详情["成交量比率"],
                "得分": 得分详情["得分"],
                "得分明细": 得分详情["得分明细"],
                "理由": f"{得分详情['趋势']} | RSI={得分详情['RSI']} | 得分{得分详情['得分']}",
                "来源": "本地AI引擎"
            })
        
        # 按得分排序，取前5
        打分结果.sort(key=lambda x: x["得分"], reverse=True)
        
        return {
            "推荐": 打分结果[:5],
            "置信度": 75,
            "类型": f"本地策略打分推荐 - {策略类型}"
        }
    
    def 获取信号(self, 品种代码: str) -> Dict:
        """
        获取单个品种的交易信号
        
        参数:
            品种代码: 品种代码
        
        返回:
            交易信号（买入/卖出/持有）
        """
        价格 = self.获取实时价格(品种代码)
        if not 价格:
            return {"信号": "持有", "置信度": 0, "理由": "无法获取价格"}
        
        指标 = self.计算技术指标(品种代码)
        
        # 信号判断逻辑
        信号 = "持有"
        置信度 = 50
        理由 = []
        
        # 买入信号
        if 指标["RSI"] < 30 and 指标["趋势"] in ["上涨", "强势上涨"]:
            信号 = "买入"
            置信度 = 75
            理由.append(f"RSI超卖({指标['RSI']})且趋势向上")
        elif 指标["RSI"] < 25:
            信号 = "买入"
            置信度 = 70
            理由.append(f"RSI严重超卖({指标['RSI']})")
        elif 指标["趋势"] == "强势上涨" and 指标["成交量比率"] > 1.5:
            信号 = "买入"
            置信度 = 80
            理由.append("强势上涨伴随放量")
        
        # 卖出信号
        elif 指标["RSI"] > 75 and 指标["趋势"] in ["下跌", "强势下跌"]:
            信号 = "卖出"
            置信度 = 70
            理由.append(f"RSI超买({指标['RSI']})且趋势向下")
        elif 指标["RSI"] > 85:
            信号 = "卖出"
            置信度 = 75
            理由.append(f"RSI严重超买({指标['RSI']})")
        elif 指标["趋势"] == "强势下跌" and 指标["成交量比率"] > 1.3:
            信号 = "卖出"
            置信度 = 75
            理由.append("强势下跌伴随放量")
        
        # 持有信号
        else:
            理由.append(f"趋势{指标['趋势']}，RSI={指标['RSI']}")
        
        return {
            "信号": 信号,
            "置信度": 置信度,
            "理由": " | ".join(理由),
            "价格": 价格,
            "指标": 指标
        }
    
    def 分析市场(self, 市场: str = "A股") -> Dict:
        """
        分析市场整体状况
        
        参数:
            市场: 市场名称
        
        返回:
            市场分析结果
        """
        品种列表 = self.品种池.get(市场, [])[:10]
        
        上涨数量 = 0
        下跌数量 = 0
        平均RSI = 0
        平均波动率 = 0
        
        for item in 品种列表:
            指标 = self.计算技术指标(item["代码"])
            if 指标["趋势"] in ["上涨", "强势上涨"]:
                上涨数量 += 1
            elif 指标["趋势"] in ["下跌", "强势下跌"]:
                下跌数量 += 1
            
            平均RSI += 指标.get("RSI", 50)
            平均波动率 += 指标.get("波动率", 0)
        
        total = len(品种列表)
        平均RSI = round(平均RSI / total, 2) if total > 0 else 50
        平均波动率 = round(平均波动率 / total, 2) if total > 0 else 0
        
        # 市场情绪判断
        if 上涨数量 > 下跌数量 * 2:
            情绪 = "乐观"
        elif 下跌数量 > 上涨数量 * 2:
            情绪 = "悲观"
        else:
            情绪 = "中性"
        
        # 建议仓位
        if 情绪 == "乐观":
            建议仓位 = 70
        elif 情绪 == "中性":
            建议仓位 = 50
        else:
            建议仓位 = 30
        
        return {
            "市场": 市场,
            "上涨家数": 上涨数量,
            "下跌家数": 下跌数量,
            "平均RSI": 平均RSI,
            "平均波动率": 平均波动率,
            "市场情绪": 情绪,
            "建议仓位": 建议仓位,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def 生成交易计划(self, 资金: float, 风险偏好: str = "medium") -> Dict:
        """
        生成交易计划
        
        参数:
            资金: 总资金
            风险偏好: low/medium/high
        
        返回:
            交易计划
        """
        风险映射 = {
            "low": {"仓位上限": 0.5, "单笔风险": 0.02, "品种上限": 3},
            "medium": {"仓位上限": 0.7, "单笔风险": 0.03, "品种上限": 5},
            "high": {"仓位上限": 0.9, "单笔风险": 0.05, "品种上限": 8}
        }
        
        配置 = 风险映射.get(风险偏好, 风险映射["medium"])
        
        return {
            "总资金": 资金,
            "风险偏好": 风险偏好,
            "建议总仓位": 资金 * 配置["仓位上限"],
            "单笔最大风险": 资金 * 配置["单笔风险"],
            "建议持仓品种数": 配置["品种上限"],
            "每品种建议仓位": 资金 * 配置["仓位上限"] / 配置["品种上限"],
            "止损建议": "5-8%",
            "止盈建议": "15-20%"
        }
    
    def 批量分析(self, 品种列表: List[str]) -> List[Dict]:
        """批量分析多个品种"""
        results = []
        for code in 品种列表:
            signal = self.获取信号(code)
            results.append({
                "品种": code,
                "信号": signal["信号"],
                "置信度": signal["置信度"],
                "价格": signal["价格"],
                "理由": signal["理由"]
            })
            time.sleep(0.1)
        return results
    
    def 清空缓存(self):
        """清空所有缓存"""
        global 缓存数据, 缓存时间
        缓存数据 = {}
        缓存时间 = {}
        print("🗑️ AI引擎缓存已清空")


# ==================== 全局实例 ====================
_AI引擎实例 = None

def 获取AI引擎() -> AI引擎:
    """获取全局AI引擎实例"""
    global _AI引擎实例
    if _AI引擎实例 is None:
        _AI引擎实例 = AI引擎()
    return _AI引擎实例


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("AI引擎测试")
    print("=" * 50)
    
    ai = AI引擎()
    
    # 测试获取价格
    print("\n📊 测试获取价格:")
    price = ai.获取实时价格("AAPL")
    print(f"  AAPL: ${price}")
    
    # 测试技术指标
    print("\n📊 测试技术指标:")
    indicators = ai.计算技术指标("BTC-USD")
    print(f"  BTC: {indicators}")
    
    # 测试AI推荐
    print("\n📊 测试AI推荐:")
    result = ai.AI推荐("A股", "量价策略", use_real_ai=False)
    for rec in result.get("推荐", []):
        print(f"  {rec['名称']}: 得分{rec['得分']} - {rec['理由']}")
    
    # 测试获取信号
    print("\n📊 测试获取信号:")
    signal = ai.获取信号("AAPL")
    print(f"  AAPL: {signal['信号']} (置信度{signal['置信度']}%)")
    
    # 测试市场分析
    print("\n📊 测试市场分析:")
    analysis = ai.分析市场("美股")
    print(f"  市场情绪: {analysis['市场情绪']}, 建议仓位: {analysis['建议仓位']}%")
    
    print("\n✅ AI引擎测试完成")
