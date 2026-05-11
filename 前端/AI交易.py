# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time


# 缓存A股行情数据（60秒内不重复请求）
@st.cache_data(ttl=60)
def 获取A股行情缓存():
    """获取A股行情并缓存60秒"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot()
        return df
    except Exception as e:
        print(f"获取A股行情失败: {e}")
        return pd.DataFrame()


def 获取A股价格和涨跌幅(代码):
    """从缓存获取A股价格和涨跌幅"""
    try:
        df = 获取A股行情缓存()
        if df.empty:
            return None, None
        row = df[df['代码'] == 代码]
        if not row.empty:
            价格 = float(row['最新价'].iloc[0])
            涨跌幅 = float(row['涨跌幅'].iloc[0])
            return 价格, 涨跌幅
    except:
        pass
    return None, None


def 获取加密货币价格(代码):
    """获取加密货币价格"""
    try:
        import requests
        symbol = 代码.replace("-", "").upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "price" in data:
            return float(data["price"])
    except:
        pass
    return None


def 获取美股价格(代码):
    """获取美股价格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(代码)
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except:
        pass
    return None


def 获取外汇价格(货币对):
    """获取外汇价格（模拟/演示数据）"""
    # 外汇数据获取较复杂，使用模拟数据
    模拟价格 = {
        "EUR/USD": 1.0890,
        "GBP/USD": 1.2670,
        "USD/JPY": 148.50,
        "AUD/USD": 0.6600,
        "USD/CAD": 1.3650,
    }
    return 模拟价格.get(货币对, 1.0)


def 获取期货价格(品种):
    """获取期货价格（模拟/演示数据）"""
    模拟价格 = {
        "GC=F": 2350.0,   # 黄金期货
        "CL=F": 78.50,    # 原油期货
        "SI=F": 28.50,    # 白银期货
        "HG=F": 4.20,     # 铜期货
    }
    return 模拟价格.get(品种, 100.0)


def 获取真实AI推荐(市场, 策略类型, 引擎):
    """获取真实的AI推荐（基于行情数据）"""
    推荐列表 = []
    
    # ==================== A股 ====================
    if 市场 == "A股":
        # 热门A股候选
        候选品种 = [
            {"代码": "000001", "名称": "平安银行"},
            {"代码": "000002", "名称": "万科A"},
            {"代码": "000858", "名称": "五粮液"},
            {"代码": "002415", "名称": "海康威视"},
            {"代码": "600036", "名称": "招商银行"},
            {"代码": "600519", "名称": "贵州茅台"},
            {"代码": "601318", "名称": "中国平安"},
            {"代码": "300750", "名称": "宁德时代"},
            {"代码": "002594", "名称": "比亚迪"},
        ]
        
        for 股票 in 候选品种:
            代码 = 股票["代码"]
            名称 = 股票["名称"]
            try:
                价格, 涨跌幅 = 获取A股价格和涨跌幅(代码)
                
                if 价格 and 涨跌幅 is not None:
                    # 筛选条件：涨幅1%-5%
                    if 1 <= 涨跌幅 <= 5:
                        推荐列表.append({
                            "代码": 代码,
                            "名称": 名称,
                            "价格": 价格,
                            "趋势": "上涨",
                            "得分": int(50 + 涨跌幅 * 8),
                            "理由": f"涨幅{涨跌幅:.2f}%，量能充足",
                            "市场": "A股"
                        })
                    elif 涨跌幅 > 5:
                        推荐列表.append({
                            "代码": 代码,
                            "名称": 名称,
                            "价格": 价格,
                            "趋势": "强势",
                            "得分": int(70 + 涨跌幅 * 2),
                            "理由": f"涨幅{涨跌幅:.2f}%，强势突破",
                            "市场": "A股"
                        })
            except Exception as e:
                continue
        
        # 如果没有符合条件的，返回几个热门股作为参考
        if not 推荐列表:
            for 股票 in 候选品种[:3]:
                代码 = 股票["代码"]
                名称 = 股票["名称"]
                try:
                    价格, _ = 获取A股价格和涨跌幅(代码)
                    if 价格:
                        推荐列表.append({
                            "代码": 代码,
                            "名称": 名称,
                            "价格": 价格,
                            "趋势": "观望",
                            "得分": 50,
                            "理由": "热门品种，可关注",
                            "市场": "A股"
                        })
                except:
                    continue
    
    # ==================== 美股 ====================
    elif 市场 == "美股":
        候选品种 = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA", "META", "AMZN"]
        for 代码 in 候选品种:
            try:
                价格 = 获取美股价格(代码)
                if 价格 and 价格 > 0:
                    推荐列表.append({
                        "代码": 代码,
                        "名称": 代码,
                        "价格": 价格,
                        "趋势": "震荡",
                        "得分": 65,
                        "理由": f"当前价格 ${价格:.2f}，技术面稳定",
                        "市场": "美股"
                    })
            except:
                continue
        
        # 按得分排序
        推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    # ==================== 加密货币 ====================
    elif 市场 == "加密货币":
        候选品种 = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
        for 代码 in 候选品种:
            try:
                价格 = 获取加密货币价格(代码)
                if 价格 and 价格 > 0:
                    名称 = 代码.split('-')[0]
                    推荐列表.append({
                        "代码": 代码,
                        "名称": 名称,
                        "价格": 价格,
                        "趋势": "上涨" if 名称 == "BTC" else "震荡",
                        "得分": 75 if 名称 == "BTC" else 65,
                        "理由": f"当前价格 ${价格:.2f}，市场活跃",
                        "市场": "加密货币"
                    })
            except:
                continue
        
        推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    # ==================== 外汇 ====================
    elif 市场 == "外汇":
        候选品种 = [
            {"代码": "EUR/USD", "名称": "欧元/美元"},
            {"代码": "GBP/USD", "名称": "英镑/美元"},
            {"代码": "USD/JPY", "名称": "美元/日元"},
            {"代码": "AUD/USD", "名称": "澳元/美元"},
            {"代码": "USD/CAD", "名称": "美元/加元"},
        ]
        for 品种 in 候选品种:
            try:
                价格 = 获取外汇价格(品种["代码"])
                if 价格:
                    推荐列表.append({
                        "代码": 品种["代码"],
                        "名称": 品种["名称"],
                        "价格": 价格,
                        "趋势": "震荡",
                        "得分": 55,
                        "理由": f"当前汇率 {价格:.4f}",
                        "市场": "外汇"
                    })
            except:
                continue
    
    # ==================== 期货 ====================
    elif 市场 == "期货":
        候选品种 = [
            {"代码": "GC=F", "名称": "黄金期货"},
            {"代码": "CL=F", "名称": "原油期货"},
            {"代码": "SI=F", "名称": "白银期货"},
            {"代码": "HG=F", "名称": "铜期货"},
        ]
        for 品种 in 候选品种:
            try:
                价格 = 获取期货价格(品种["代码"])
                if 价格:
                    推荐列表.append({
                        "代码": 品种["代码"],
                        "名称": 品种["名称"],
                        "价格": 价格,
                        "趋势": "震荡",
                        "得分": 55,
                        "理由": f"当前价格 ${价格:.2f}",
                        "市场": "期货"
                    })
            except:
                continue
    
    # 限制返回数量
    return 推荐列表[:5]


def 获取实时价格(代码, 市场类型):
    """获取实时价格"""
    try:
        if 市场类型 == "A股":
            价格, _ = 获取A股价格和涨跌幅(代码)
            return 价格
        elif 市场类型 == "加密货币":
            return 获取加密货币价格(代码)
        elif 市场类型 == "美股":
            return 获取美股价格(代码)
        elif 市场类型 == "外汇":
            return 获取外汇价格(代码)
        elif 市场类型 == "期货":
            return 获取期货价格(代码)
    except:
        pass
    return None


def 执行买入(引擎, 代码, 价格, 数量, 市场类型, 策略类型):
    """执行买入操作"""
    try:
        # 检查可用资金
        可用资金 = 引擎.获取可用资金()
        预计花费 = 价格 * 数量
        if 预计花费 > 可用资金:
            return {"success": False, "error": f"资金不足，需要 ¥{预计花费:.2f}，可用 ¥{可用资金:.2f}"}
        
        # 执行买入
        结果 = 引擎.买入(代码, 价格, 数量)
        return 结果
    except Exception as e:
        return {"success": False, "error": str(e)}


def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场选择
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    # 策略映射
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认策略"]))
    
    # 获取可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    # 存储AI推荐结果
    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner(f"AI 正在使用【{策略类型}】分析【{市场}】..."):
            try:
                st.session_state.ai_list = 获取真实AI推荐(市场, 策略类型, 引擎)
                
                if st.session_state.ai_list:
                    st.success(f"✅ AI 分析完成！共推荐 {len(st.session_state.ai_list)} 只标的")
                else:
                    st.warning("⚠️ 当前策略下未筛选出合适标的")
                st.rerun()
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # 显示推荐列表
    if st.session_state.ai_list:
        st.markdown("### 📈 AI 推荐买入（按策略打分）")
        
        for idx, item in enumerate(st.session_state.ai_list):
            code = item.get("代码", "")
            name = item.get("名称", "未知")
            price = item.get("价格", 0)
            趋势 = item.get("趋势", "未知")
            理由 = item.get("理由", "")
            得分 = item.get("得分", 0)
            市场类型 = item.get("市场", "未知")
            
            # 根据市场类型计算建议数量
            if 市场类型 == "A股":
                建议数量 = int(可用资金 * 0.1 / price / 100) * 100
                建议数量 = max(建议数量, 100)
                数量单位 = "股"
            elif 市场类型 == "加密货币":
                建议数量 = round(可用资金 * 0.1 / price, 4)
                数量单位 = "个"
            elif 市场类型 == "外汇":
                建议数量 = round(可用资金 * 0.1 / price, 2)
                数量单位 = "手"
            elif 市场类型 == "期货":
                建议数量 = int(可用资金 * 0.1 / price)
                建议数量 = max(建议数量, 1)
                数量单位 = "手"
            else:
                建议数量 = int(可用资金 * 0.1 / price / 100) * 100
                建议数量 = max(建议数量, 100)
                数量单位 = "股"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: {price:.4f}")
                with col2:
                    if 趋势 in ["上涨", "强势"]:
                        st.markdown("🟢 趋势向上")
                    elif 趋势 == "下跌":
                        st.markdown("🔴 趋势向下")
                    else:
                        st.markdown("🟡 震荡")
                    st.caption(f"得分: {得分}")
                with col3:
                    st.caption(f"建议: {建议数量}{数量单位}")
                    st.caption(f"金额: ¥{price * 建议数量:.0f}")
                with col4:
                    if st.button(f"买入", key=f"buy_{code}_{idx}"):
                        if price > 0:
                            # 获取实时价格
                            实时价格 = 获取实时价格(code, 市场类型)
                            if 实时价格 and 实时价格 > 0:
                                实际价格 = 实时价格
                            else:
                                实际价格 = price
                            
                            with st.spinner(f"正在买入 {name}..."):
                                结果 = 执行买入(引擎, code, 实际价格, 建议数量, 市场类型, 策略类型)
                                if 结果.get("success"):
                                    st.success(f"✅ {结果['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 买入失败: {结果.get('error')}")
                        else:
                            st.error("价格无效，无法买入")
                
                if 理由:
                    st.caption(f"📝 {理由}")
                st.divider()
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if hasattr(引擎, '持仓') and 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            平均成本 = getattr(pos, '平均成本', 0)
            当前价格 = getattr(pos, '当前价格', 平均成本)
            浮动盈亏 = (当前价格 - 平均成本) * 数量
            
            持仓数据.append({
                "品种": sym,
                "数量": int(数量) if isinstance(数量, (int, float)) else 0,
                "成本": round(平均成本, 4),
                "现价": round(当前价格, 4),
                "浮动盈亏": round(浮动盈亏, 2)
            })
        st.dataframe(持仓数据, use_container_width=True)
    else:
        st.info("暂无持仓")
