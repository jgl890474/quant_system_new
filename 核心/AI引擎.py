# 在现有 AI引擎.py 文件末尾追加以下代码

# ==================== 新增导入 ====================
from 核心.技术指标 import 获取指标计算器
from 核心.真实AI引擎 import 获取真实AI
from 核心.新闻情绪 import 获取情绪分析器

# ==================== 在 AI引擎 类中添加新方法 ====================

def 获取完整技术指标(self, 品种代码: str) -> Dict:
    """获取完整技术指标"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(品种代码)
        df = ticker.history(period="120d")
        
        if df.empty:
            return {}
        
        calc = 获取指标计算器()
        
        return {
            '趋势': calc.计算趋势指标(df),
            'MACD': calc.计算MACD(df),
            '布林带': calc.计算布林带(df),
            'RSI': calc.计算RSI(df),
            'KDJ': calc.计算KDJ(df),
            '成交量': calc.计算成交量指标(df)
        }
    except Exception as e:
        print(f"获取技术指标失败: {e}")
        return {}

def 智能推荐增强版(self, 市场: str, 策略类型: str, 使用AI: bool = True) -> Dict:
    """
    智能推荐增强版 - 结合本地规则和真实AI
    """
    # 1. 获取本地推荐
    local_result = self.AI推荐(市场, 策略类型, use_real_ai=False)
    
    if not 使用AI:
        return local_result
    
    # 2. 对前3名进行AI深度分析
    candidates = local_result.get('推荐', [])[:3]
    enhanced_results = []
    
   真实AI = 获取真实AI()
    情绪分析 = 获取情绪分析器()
    
    for item in candidates:
        代码 = item.get('代码')
        if not 代码:
            continue
        
        # 获取完整技术指标
        技术指标 = self.获取完整技术指标(代码)
        
        # 情绪分析
        新闻 = 情绪分析.获取新闻(代码)
        情绪 = 情绪分析.分析情绪(新闻)
        
        # AI综合分析
        ai_result = 真实AI.综合分析(
            代码,
            {'技术指标': 技术指标},
            情绪
        )
        
        enhanced_results.append({
            **item,
            'AI评分': ai_result.get('综合评分', 50),
            'AI决策': ai_result.get('交易决策', '持有'),
            'AI置信度': ai_result.get('置信度', 50),
            '建议仓位': ai_result.get('建议仓位', 10),
            '止损位': ai_result.get('止损位'),
            '止盈目标': ai_result.get('止盈目标1')
        })
    
    # 3. 融合评分（本地40% + AI60%）
    for item in enhanced_results:
        item['综合得分'] = round(
            item.get('得分', 50) * 0.4 + item.get('AI评分', 50) * 0.6, 1
        )
    
    enhanced_results.sort(key=lambda x: x.get('综合得分', 0), reverse=True)
    
    return {
        '推荐': enhanced_results[:5],
        '置信度': 85,
        '类型': 'AI增强推荐 (本地+DeepSeek)',
        'AI使用': 使用AI
    }

def 获取完整交易信号(self, 品种代码: str) -> Dict:
    """获取完整交易信号"""
    # 1. 技术指标
    技术指标 = self.获取完整技术指标(品种代码)
    
    # 2. 价格
    价格 = self.获取实时价格(品种代码)
    
    # 3. 情绪分析
    情绪分析 = 获取情绪分析器()
    新闻 = 情绪分析.获取新闻(品种代码)
    情绪 = 情绪分析.分析情绪(新闻)
    
    # 4. 本地信号
    本地信号 = self.获取信号(品种代码)
    
    # 5. AI分析
    真实AI = 获取真实AI()
    ai_result = 真实AI.综合分析(
        品种代码,
        {
            '价格': 价格,
            '技术指标': 技术指标,
            '本地信号': 本地信号
        },
        情绪
    )
    
    return {
        '品种': 品种代码,
        '价格': 价格,
        '本地信号': 本地信号.get('信号', '持有'),
        'AI信号': ai_result.get('交易决策', '持有'),
        'AI置信度': ai_result.get('置信度', 50),
        '综合评分': ai_result.get('综合评分', 50),
        '建议仓位': ai_result.get('建议仓位', 10),
        '止损位': ai_result.get('止损位'),
        '止盈目标': ai_result.get('止盈目标1'),
        '风险等级': ai_result.get('风险等级', '中'),
        '分析总结': ai_result.get('分析总结', ''),
        '情绪评分': 情绪.get('评分', 50)
    }
