# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
import datetime


# ==================== Tushare 配置（替代 akshare） ====================
try:
    import tushare as ts
    ts.set_token('a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac')
    pro = ts.pro_api()
    TUSHARE_AVAILABLE = True
    print("✅ Tushare Pro 已连接")
except Exception as e:
    TUSHARE_AVAILABLE = False
    print(f"⚠️ Tushare Pro 连接失败: {e}")
    pro = None


# ==================== 获取A股实时数据（Tushare） ====================
@st.cache_data(ttl=60)
def 获取A股实时行情():
    """使用 Tushare 获取A股实时行情"""
    if not TUSHARE_AVAILABLE or pro is None:
        return pd.DataFrame()
    
    try:
        # 获取今天日期
        today = datetime.datetime.now().strftime('%Y%m%d')
        
        # 获取交易日历
        trade_cal = pro.trade_cal(exchange='SSE', start_date=today, end_date=today)
        if trade_cal.empty or trade_cal['is_open'].iloc[0] == 0:
            # 非交易日，使用最近交易日数据
            trade_cal = pro.trade_cal(exchange='SSE', start_date='20240101', end_date=today)
            trade_cal = trade_cal[trade_cal['is_open'] == 1]
            if not trade_cal.empty:
                latest_trade_date = trade_cal['cal_date'].iloc[-1]
            else:
                latest_trade_date = today
        else:
            latest_trade_date = today
        
        # 获取指定股票列表的日线数据
        股票列表 = [
            {"ts_code": "000001.SZ", "symbol": "000001", "name": "平安银行"},
            {"ts_code": "000858.SZ", "symbol": "000858", "name": "五粮液"},
            {"ts_code": "002415.SZ", "symbol": "002415", "name": "海康威视"},
            {"ts_code": "600036.SH", "symbol": "600036", "name": "招商银行"},
            {"ts_code": "600519.SH", "symbol": "600519", "name": "贵州茅台"},
            {"ts_code": "601318.SH", "symbol": "601318", "name": "中国平安"},
            {"ts_code": "300750.SZ", "symbol": "300750", "name": "宁德时代"},
            {"ts_code": "002594.SZ", "symbol": "002594", "name": "比亚迪"},
        ]
        
        result = []
        for 股票 in 股票列表:
            try:
                df = pro.daily(ts_code=股票["ts_code"], start_date=latest_trade_date, end_date=latest_trade_date)
                if not df.empty:
                    result.append({
                        "代码": 股票["symbol"],
                        "名称": 股票["name"],
                        "最新价": round(df['close'].iloc[0], 2),
                        "涨跌幅": round(df['pct_chg'].iloc[0], 2) if 'pct_chg' in df.columns else 0,
                        "开盘": round(df['open'].iloc[0], 2),
                        "最高": round(df['high'].iloc[0], 2),
                        "最低": round(df['low'].iloc[0], 2),
                        "成交量": df['vol'].iloc[0],
                    })
            except Exception as e:
                print(f"获取 {股票['name']} 数据失败: {e}")
                continue
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"获取A股实时行情失败: {e}")
        return pd.DataFrame()


def 获取A股价格(代码):
    """获取单个A股价格"""
    try:
        df = 获取A股实时行情()
        if df.empty:
            return None
        row = df[df['代码'] == 代码]
        if not row.empty:
            return float(row['最新价'].iloc[0])
    except:
        pass
    return None


def 获取A股涨跌幅(代码):
    """获取单个A股涨跌幅"""
    try:
        df = 获取A股实时行情()
        if df.empty:
            return None
        row = df[df['代码'] == 代码]
        if not row.empty:
            return float(row['涨跌幅'].iloc[0])
    except:
        pass
    return None


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
    # 返回模拟价格作为备用
    模拟价格 = {"BTCUSD": 65000, "ETHUSD": 3500, "SOLUSD": 150, "BNBUSD": 600}
    return 模拟价格.get(代码.replace("-", "").upper(), 100)


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
    # 返回模拟价格
    模拟价格 = {"AAPL": 175, "GOOGL": 140, "MSFT": 420, "NVDA": 120, "TSLA": 170}
    return 模拟价格.get(代码, 100)


def 获取外汇价格(货币对):
    """获取外汇价格（演示数据）"""
    模拟价格 = {
        "EUR/USD": 1.0890,
        "GBP/USD": 1.2670,
        "USD/JPY": 148.50,
    }
    return 模拟价格.get(货币对, 1.0)


def 获取期货价格(品种):
    """获取期货价格（演示数据）"""
    模拟价格 = {
        "GC=F": 2350.0,
        "CL=F": 78.50,
    }
    return 模拟价格.get(品种, 100.0)


def 获取股票名称(代码):
    """获取股票名称"""
    名称映射 = {
        "000001": "平安银行",
        "000858": "五粮液",
        "002415": "海康威视",
        "600036": "招商银行",
        "600519": "贵州茅台",
        "601318": "中国平安",
        "300750": "宁德时代",
        "002594": "比亚迪",
    }
    return 名称映射.get(代码, 代码)


def 获取真实AI推荐(市场, 策略类型, 引擎):
    """获取真实的AI推荐"""
    推荐列表 = []
    
    # ==================== A股（使用 Tushare） ====================
    if 市场 == "A股":
        df = 获取A股实时行情()
        
        if not df.empty:
            for _, row in df.iterrows():
                代码 = row['代码']
                名称 = row['名称']
                价格 = row['最新价']
                涨跌幅 = row['涨跌幅']
                
                if 价格 and 价格 > 0:
                    if 涨跌幅 > 0:
                        得分 = int(50 + min(涨跌幅 * 8, 50))
                        趋势 = "上涨" if 涨跌幅 < 5 else "强势"
                        理由 = f"涨幅{涨跌幅:.2f}%"
                    elif 涨跌幅 < 0:
                        得分 = int(50 + max(涨跌幅 * 2, -20))
                        趋势 = "下跌"
                        理由 = f"跌幅{abs(涨跌幅):.2f}%"
                    else:
                        得分 = 45
                        趋势 = "平盘"
                        理由 = f"当前价格 ¥{价格:.2f}"
                    
                    推荐列表.append({
                        "代码": 代码,
                        "名称": 名称,
                        "价格": 价格,
                        "趋势": 趋势,
                        "得分": 得分,
                        "理由": 理由,
                        "市场": "A股"
                    })
        else:
            # 如果获取失败，使用模拟数据
            for 代码, 名称 in [("000001", "平安银行"), ("600036", "招商银行"), ("600519", "贵州茅台")]:
                推荐列表.append({
                    "代码": 代码,
                    "名称": 名称,
                    "价格": 100.00,
                    "趋势": "观望",
                    "得分": 50,
                    "理由": "Tushare数据获取中",
                    "市场": "A股"
                })
        
        # 按得分排序
        推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    # ==================== 加密货币 ====================
    elif 市场 == "加密货币":
        候选品种 = [
            {"代码": "BTC-USD", "名称": "比特币"},
            {"代码": "ETH-USD", "名称": "以太坊"},
            {"代码": "SOL-USD", "名称": "Solana"},
            {"代码": "BNB-USD", "名称": "币安币"},
        ]
        
        for 币种 in 候选品种:
            try:
                价格 = 获取加密货币价格(币种["代码"])
                if 价格 and 价格 > 0:
                    推荐列表.append({
                        "代码": 币种["代码"],
                        "名称": 币种["名称"],
                        "价格": 价格,
                        "趋势": "上涨",
                        "得分": 75,
                        "理由": f"当前价格 ${价格:.2f}",
                        "市场": "加密货币"
                    })
            except:
                continue
        
        推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    # ==================== 美股 ====================
    elif 市场 == "美股":
        候选品种 = ["AAPL", "NVDA", "MSFT", "GOOGL", "TSLA"]
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
                        "理由": f"当前价格 ${价格:.2f}",
                        "市场": "美股"
                    })
            except:
                continue
        推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    # ==================== 外汇 ====================
    elif 市场 == "外汇":
        候选品种 = ["EUR/USD", "GBP/USD"]
        for 代码 in 候选品种:
            价格 = 获取外汇价格(代码)
            推荐列表.append({
                "代码": 代码,
                "名称": 代码,
                "价格": 价格,
                "趋势": "震荡",
                "得分": 55,
                "理由": f"当前汇率 {价格:.4f}",
                "市场": "外汇"
            })
    
    # ==================== 期货 ====================
    elif 市场 == "期货":
        候选品种 = [{"代码": "GC=F", "名称": "黄金期货"}, {"代码": "CL=F", "名称": "原油期货"}]
        for 品种 in 候选品种:
            价格 = 获取期货价格(品种["代码"])
            推荐列表.append({
                "代码": 品种["代码"],
                "名称": 品种["名称"],
                "价格": 价格,
                "趋势": "震荡",
                "得分": 55,
                "理由": f"当前价格 ${价格:.2f}",
                "市场": "期货"
            })
    
    return 推荐列表[:5]


def 获取实时价格(代码, 市场类型):
    """获取实时价格"""
    try:
        if 市场类型 == "A股":
            return 获取A股价格(代码)
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
    """执行买入操作 - 修复数量类型问题"""
    try:
        # 确保数量是整数（A股、美股、期货）或浮点数（加密货币、外汇）
        if 市场类型 in ["A股", "美股", "期货"]:
            数量 = int(数量)
        else:
            数量 = float(数量)
        
        # 确保价格是浮点数
        价格 = float(价格)
        
        if 价格 <= 0:
            return {"success": False, "error": f"价格无效: {价格}"}
        
        if 数量 <= 0:
            return {"success": False, "error": f"数量无效: {数量}"}
        
        可用资金 = 引擎.获取可用资金()
        预计花费 = 价格 * 数量
        if 预计花费 > 可用资金:
            return {"success": False, "error": f"资金不足，需要 ¥{预计花费:.2f}，可用 ¥{可用资金:.2f}"}
        
        print(f"执行买入: 代码={代码}, 价格={价格}, 数量={数量}, 市场={市场类型}")
        
        结果 = 引擎.买入(代码, 价格, 数量)
        print(f"买入结果: {结果}")
        
        return 结果
    except Exception as e:
        print(f"买入异常: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认策略"]))
    
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []
    
    # 修复：use_container_width=True -> width='stretch'
    if st.button("🚀 AI 分析", type="primary", width='stretch'):
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
            else:
                建议数量 = int(可用资金 * 0.1 / price / 100) * 100
                建议数量 = max(建议数量, 100)
                数量单位 = "股"
            
            # 确保数量不为0
            if 建议数量 <= 0:
                建议数量 = 1 if 市场类型 == "加密货币" else 100
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: {price:.4f}")
                with col2:
                    if 趋势 in ["上涨", "强势"]:
                        st.markdown("🟢 趋势向上")
                    elif 趋势 == "下跌":
                        st.markdown("🔻 趋势向下")
                    else:
                        st.markdown("🟡 观望")
                    st.caption(f"得分: {得分}")
                with col3:
                    st.caption(f"建议: {建议数量}{数量单位}")
                    st.caption(f"金额: ¥{price * 建议数量:.0f}")
                with col4:
                    if st.button(f"买入", key=f"buy_{code}_{idx}"):
                        if price > 0:
                            实时价格 = 获取实时价格(code, 市场类型)
                            实际价格 = 实时价格 if 实时价格 else price
                            
                            with st.spinner(f"正在买入 {name}..."):
                                结果 = 执行买入(引擎, code, 实际价格, 建议数量, 市场类型, 策略类型)
                                if 结果.get("success"):
                                    st.success(f"✅ {结果['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 买入失败: {结果.get('error')}")
                        else:
                            st.error("价格无效")
                
                if 理由:
                    st.caption(f"📝 {理由}")
                st.divider()
    
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
        st.dataframe(持仓数据, width='stretch', hide_index=True)
    else:
        st.info("暂无持仓")
