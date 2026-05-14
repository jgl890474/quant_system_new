# -*- coding: utf-8 -*-
"""
新闻情绪分析模块
功能：获取新闻、分析情绪
"""

import requests
from datetime import datetime
from typing import Dict, List


class 新闻情绪分析器:
    """新闻情绪分析器"""
    
    def __init__(self):
        self.新闻缓存 = {}
    
    def 获取新闻(self, 品种代码: str) -> List[Dict]:
        """获取相关新闻"""
        keyword = 品种代码.split('-')[0]
        
        # 尝试免费API
        try:
            url = f"https://gnews.io/api/v4/search"
            params = {
                'q': keyword,
                'lang': 'zh',
                'max': 5,
                'token': 'demo'  # 免费demo token
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                return articles
        except:
            pass
        
        # 返回模拟数据
        return [
            {'title': f'{品种代码}市场关注度提升', 'publishedAt': datetime.now().isoformat()}
        ]
    
    def 分析情绪(self, 新闻列表: List[Dict]) -> Dict:
        """分析新闻情绪"""
        if not 新闻列表:
            return {'情绪': '中性', '评分': 50, '正面新闻': 0, '负面新闻': 0, '新闻数量': 0}
        
        positive_words = ['上涨', '突破', '利好', '增持', '买入', '乐观', '新高', '涨']
        negative_words = ['下跌', '破位', '利空', '减持', '卖出', '悲观', '新低', '跌']
        
        positive_count = 0
        negative_count = 0
        
        for news in 新闻列表:
            title = news.get('title', '')
            for word in positive_words:
                if word in title:
                    positive_count += 1
                    break
            for word in negative_words:
                if word in title:
                    negative_count += 1
                    break
        
        total = positive_count + negative_count
        if total > 0:
            score = positive_count / total * 100
        else:
            score = 50
        
        if score >= 70:
            sentiment = '乐观'
        elif score <= 30:
            sentiment = '悲观'
        else:
            sentiment = '中性'
        
        return {
            '情绪': sentiment,
            '评分': round(score, 1),
            '正面新闻': positive_count,
            '负面新闻': negative_count,
            '新闻数量': len(新闻列表)
        }


# 全局实例
_情绪分析器 = None

def 获取情绪分析器():
    global _情绪分析器
    if _情绪分析器 is None:
        _情绪分析器 = 新闻情绪分析器()
    return _情绪分析器
