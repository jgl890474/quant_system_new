# -*- coding: utf-8 -*-
"""
测试AI引擎新功能
运行: python test_new_ai.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🧪 AI引擎新功能测试")
print("=" * 60)

# ========== 测试1：导入模块 ==========
print("\n📦 1. 测试模块导入...")

try:
    from 核心.技术指标 import 获取指标计算器
    print("   ✅ 技术指标模块导入成功")
except Exception as e:
    print(f"   ❌ 技术指标模块导入失败: {e}")

try:
    from 核心.真实AI引擎 import 获取真实AI
    print("   ✅ 真实AI引擎模块导入成功")
except Exception as e:
    print(f"   ❌ 真实AI引擎模块导入失败: {e}")

try:
    from 核心.新闻情绪 import 获取情绪分析器
    print("   ✅ 新闻情绪模块导入成功")
except Exception as e:
    print(f"   ❌ 新闻情绪模块导入失败: {e}")

try:
    from 核心.AI引擎 import AI引擎
    print("   ✅ AI引擎模块导入成功")
except Exception as e:
    print(f"   ❌ AI引擎模块导入失败: {e}")

# ========== 测试2：技术指标计算 ==========
print("\n📊 2. 测试技术指标计算...")

try:
    calc = 获取指标计算器()
    
    # 模拟数据
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(end='2024-01-01', periods=100, freq='D')
    price = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * 0.99,
        '最高': price * 1.01,
        '最低': price * 0.98,
        '收盘': price,
        '成交量': np.random.randint(1000, 10000, 100)
    })
    
    # 测试各指标
    macd = calc.计算MACD(df)
    print(f"   MACD: {macd.get('状态', 'N/A')}")
    
    bb = calc.计算布林带(df)
    print(f"   布林带: {bb.get('信号', 'N/A')}")
    
    rsi = calc.计算RSI(df)
    print(f"   RSI: {rsi.get('RSI', 'N/A')} ({rsi.get('状态', 'N/A')})")
    
    kdj = calc.计算KDJ(df)
    print(f"   KDJ: K={kdj.get('K', 'N/A')}, 信号={kdj.get('信号', 'N/A')}")
    
    vol = calc.计算成交量指标(df)
    print(f"   成交量比率: {vol.get('成交量比率', 'N/A')}")
    
    trend = calc.计算趋势指标(df)
    print(f"   趋势: {trend.get('趋势', 'N/A')}")
    
    print("   ✅ 技术指标计算正常")
    
except Exception as e:
    print(f"   ❌ 技术指标计算失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 测试3：新闻情绪分析 ==========
print("\n📰 3. 测试新闻情绪分析...")

try:
    sentiment = 获取情绪分析器()
    
    # 获取新闻
    news = sentiment.获取新闻("BTC-USD")
    print(f"   获取到 {len(news)} 条新闻")
    
    # 分析情绪
    emotion = sentiment.分析情绪(news)
    print(f"   情绪: {emotion.get('情绪', 'N/A')} (评分: {emotion.get('评分', 'N/A')})")
    
    print("   ✅ 新闻情绪分析正常")
    
except Exception as e:
    print(f"   ❌ 新闻情绪分析失败: {e}")

# ========== 测试4：AI引擎新功能 ==========
print("\n🤖 4. 测试AI引擎新功能...")

try:
    ai = AI引擎()
    
    # 测试获取完整技术指标
    print("   测试获取完整技术指标...")
    indicators = ai.获取完整技术指标("AAPL")
    if indicators:
        print(f"     趋势: {indicators.get('趋势', {}).get('趋势', 'N/A')}")
        print(f"     RSI: {indicators.get('RSI', {}).get('RSI', 'N/A')}")
    else:
        print("     返回空数据（可能网络问题）")
    
    # 测试增强推荐（不使用AI，只用本地）
    print("\n   测试增强推荐（本地模式）...")
    result = ai.智能推荐增强版("A股", "量价策略", use_ai=False)
    print(f"     推荐数量: {len(result.get('推荐', []))}")
    for i, rec in enumerate(result.get('推荐', [])[:3]):
        print(f"     {i+1}. {rec.get('名称', 'N/A')}: 得分{rec.get('得分', 0)}")
    
    print("   ✅ AI引擎新功能正常")
    
except Exception as e:
    print(f"   ❌ AI引擎测试失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 测试5：真实AI API（可选） ==========
print("\n🌐 5. 测试真实AI API（可选）...")

try:
    from 核心.真实AI引擎 import 真实AI引擎
    real_ai = 真实AI引擎()
    
    # 测试API调用
    result = real_ai._调用AI("请返回JSON: {\"test\": \"success\"}")
    
    if result and not result.get('降级模式'):
        print("   ✅ 真实AI API连接正常")
    else:
        print("   ⚠️ 真实AI API连接失败（使用降级模式）")
        print("     提示：检查API Key或网络连接")
        
except Exception as e:
    print(f"   ⚠️ 真实AI API测试跳过: {e}")

# ========== 测试总结 ==========
print("\n" + "=" * 60)
print("📋 测试总结")
print("=" * 60)

print("""
请检查以上输出：

✅ = 通过
⚠️ = 警告（功能可能受限）
❌ = 失败（需要修复）

下一步建议：
1. 如果所有模块都显示 ✅，可以部署到 Streamlit Cloud
2. 如果有 ⚠️，不影响基本功能，但真实AI功能需要检查API Key
3. 如果有 ❌，请把错误信息发给我
""")
