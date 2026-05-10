# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


def 显示(引擎=None):
    """
    显示回测页面 - 动态多策略净值曲线
    参数:
        引擎: 订单引擎实例（可选，用于获取实盘数据）
    """
    st.subheader("📈 动态多策略回测")
    
    # ==================== 侧边栏参数设置 ====================
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")
        
        股票代码 = st.text_input("股票代码", value="000001", help="请输入6位股票代码，如：000001（平安银行）")
        开始日期 = st.date_input("开始日期", value=datetime.date(2024, 1, 1))
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.0003, step=0.0001, format="%.4f", help="默认万分之三")
        
        st.markdown("---")
        st.markdown("### 📊 选择策略")
        
        # 多策略选择
        启用双均线 = st.checkbox("双均线策略", value=True)
        启用买入持有 = st.checkbox("买入持有策略", value=True)
        启用隔夜套利 = st.checkbox("隔夜套利策略", value=True)
        启用布林带 = st.checkbox("布林带策略", value=False)
        启用RSI = st.checkbox("RSI超买超卖策略", value=False)
        
        st.markdown("---")
        
        # 策略参数（仅在启用时显示）
        if 启用双均线:
            with st.expander("双均线参数"):
                短期均线 = st.selectbox("短期均线", [5, 10, 20], index=0)
                长期均线 = st.selectbox("长期均线", [20, 30, 60], index=1)
        
        if 启用布林带:
            with st.expander("布林带参数"):
                布林带周期 = st.number_input("周期", value=20, min_value=5, max_value=50)
                布林带标准差 = st.number_input("标准差倍数", value=2.0, min_value=1.0, max_value=3.0, step=0.5)
        
        if 启用RSI:
            with st.expander("RSI参数"):
                RSI周期 = st.number_input("RSI周期", value=14, min_value=5, max_value=30)
                RSI超卖 = st.number_input("超卖阈值", value=30, min_value=10, max_value=40)
                RSI超买 = st.number_input("超买阈值", value=70, min_value=60, max_value=90)
        
        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", use_container_width=True)
    
    # 主界面提示
    st.markdown("""
    > 💡 **使用说明**：在左侧选择策略并设置参数，点击「开始回测」查看多策略净值曲线对比。
    > 
    > **策略说明**：
    > - 双均线策略：金叉买入，死叉卖出
    > - 买入持有策略：一次性买入并持有到回测结束
    > - 隔夜套利策略：每日尾盘买入，次日尾盘卖出
    > - 布林带策略：触及下轨买入，触及上轨卖出
    > - RSI策略：超卖区域买入，超买区域卖出
    """)
    
    if not 运行按钮:
        # 显示示例图表
        st.info("👈 请在左侧选择策略并点击「开始回测」")
        
        # 显示示例多策略曲线
        with st.expander("📈 示例：多策略净值曲线对比（点击展开）"):
            dates = pd.date_range("2024-01-01", periods=252)
            demo_df = pd.DataFrame({"日期": dates})
            demo_df["双均线策略"] = np.cumprod(1 + np.random.randn(252) * 0.01 + 0.0003)
            demo_df["买入持有"] = np.cumprod(1 + np.random.randn(252) * 0.008 + 0.0002)
            demo_df["隔夜套利"] = np.cumprod(1 + np.random.randn(252) * 0.012 + 0.0005)
            demo_df["基准"] = np.cumprod(1 + np.random.randn(252) * 0.01)
            
            # 归一化到初始资金
            for col in demo_df.columns:
                if col != "日期":
                    demo_df[col] = 1000000 * demo_df[col] / demo_df[col].iloc[0]
            
            fig = 绘制多策略曲线(demo_df, "示例：多策略净值曲线对比")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("注：此为演示数据，实际回测请点击「开始回测」")
        return
    
    # ==================== 执行回测 ====================
    with st.spinner("正在获取数据并进行多策略回测，请稍候..."):
        try:
            # 获取股票历史数据
            df = 获取股票历史数据(股票代码, 开始日期, 结束日期)
            
            if df is None or df.empty:
                st.error(f"❌ 无法获取股票 {股票代码} 的历史数据")
                st.info("请检查股票代码是否正确，或更换其他股票代码（如：000001、600036、000858）")
                return
            
            st.success(f"✅ 成功获取 {len(df)} 条历史数据（{df['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {df['日期'].iloc[-1].strftime('%Y-%m-%d')}）")
            
            # 存储各策略结果
            策略结果 = {}
            策略净值曲线 = pd.DataFrame()
            策略净值曲线['日期'] = df['日期']
            策略净值曲线['基准'] = df['收盘'] / df['收盘'].iloc[0] * 初始资金
            
            # 执行各策略
            if 启用双均线:
                with st.spinner("正在计算双均线策略..."):
                    df_ma = 计算均线(df.copy(), 短期均线, 长期均线)
                    结果 = 执行双均线回测(df_ma, 初始资金, 手续费率)
                    策略结果['双均线策略'] = 结果
                    策略净值曲线['双均线策略'] = 结果['总资产曲线'][1:] if len(结果['总资产曲线']) > len(df) else 结果['总资产曲线']
            
            if 启用买入持有:
                with st.spinner("正在计算买入持有策略..."):
                    结果 = 执行买入持有回测(df.copy(), 初始资金, 手续费率)
                    策略结果['买入持有'] = 结果
                    策略净值曲线['买入持有'] = 结果['总资产曲线']
            
            if 启用隔夜套利:
                with st.spinner("正在计算隔夜套利策略..."):
                    结果 = 执行隔夜套利回测(df.copy(), 初始资金, 手续费率)
                    策略结果['隔夜套利'] = 结果
                    策略净值曲线['隔夜套利'] = 结果['总资产曲线']
            
            if 启用布林带:
                with st.spinner("正在计算布林带策略..."):
                    df_bb = 计算布林带(df.copy(), 布林带周期, 布林带标准差)
                    结果 = 执行布林带回测(df_bb, 初始资金, 手续费率)
                    策略结果['布林带策略'] = 结果
                    策略净值曲线['布林带策略'] = 结果['总资产曲线']
            
            if 启用RSI:
                with st.spinner("正在计算RSI策略..."):
                    df_rsi = 计算RSI(df.copy(), RSI周期)
                    结果 = 执行RSI回测(df_rsi, 初始资金, 手续费率, RSI超卖, RSI超买)
                    策略结果['RSI策略'] = 结果
                    策略净值曲线['RSI策略'] = 结果['总资产曲线']
            
            # 确保所有列长度一致
            min_len = len(df)
            for col in 策略净值曲线.columns:
                if col != '日期' and len(策略净值曲线[col]) > min_len:
                    策略净值曲线[col] = 策略净值曲线[col].iloc[:min_len]
                elif col != '日期' and len(策略净值曲线[col]) < min_len:
                    策略净值曲线[col] = 策略净值曲线[col].reindex(range(min_len), method='ffill')
            
            # 显示多策略对比结果
            显示多策略结果(策略结果, 策略净值曲线, 股票代码, 初始资金)
            
        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def 获取股票历史数据(股票代码, 开始日期, 结束日期):
    """获取股票历史日线数据"""
    
    代码 = str(股票代码).zfill(6)
    
    # 方法1：使用 akshare
    if AKSHARE_AVAILABLE:
        try:
            df = ak.stock_zh_a_hist(
                symbol=代码,
                period="daily",
                start_date=开始日期.strftime("%Y%m%d"),
                end_date=结束日期.strftime("%Y%m%d"),
                adjust="qfq"
            )
            if df is not None and not df.empty:
                df.columns = ['日期', '开盘', '最高', '最低', '收盘', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
                return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        except Exception as e:
            print(f"akshare 获取失败: {e}")
    
    # 方法2：东方财富接口
    try:
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": f"1.{代码}" if 代码.startswith('6') else f"0.{代码}",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "beg": 开始日期.strftime("%Y%m%d"),
            "end": 结束日期.strftime("%Y%m%d"),
            "ut": "fa5fd1943c7b386a172cb689d1c0edf1"
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            rows = []
            for k in klines:
                parts = k.split(",")
                rows.append({
                    "日期": parts[0],
                    "开盘": float(parts[1]),
                    "最高": float(parts[2]),
                    "最低": float(parts[3]),
                    "收盘": float(parts[4]),
                    "成交量": float(parts[5])
                })
            df = pd.DataFrame(rows)
            df['日期'] = pd.to_datetime(df['日期'])
            return df
    except Exception as e:
        print(f"东方财富接口获取失败: {e}")
    
    return None


def 计算均线(df, 短期均线, 长期均线):
    """计算移动平均线"""
    df['MA_短期'] = df['收盘'].rolling(window=短期均线).mean()
    df['MA_长期'] = df['收盘'].rolling(window=长期均线).mean()
    df['信号'] = 0
    df['信号'] = np.where(
        (df['MA_短期'] > df['MA_长期']) & (df['MA_短期'].shift(1) <= df['MA_长期'].shift(1)), 1, 0)
    df['信号'] = np.where(
        (df['MA_短期'] < df['MA_长期']) & (df['MA_短期'].shift(1) >= df['MA_长期'].shift(1)), -1, df['信号'])
    return df


def 计算布林带(df, 周期, 标准差倍数):
    """计算布林带"""
    df['中轨'] = df['收盘'].rolling(window=周期).mean()
    df['标准差'] = df['收盘'].rolling(window=周期).std()
    df['上轨'] = df['中轨'] + 标准差倍数 * df['标准差']
    df['下轨'] = df['中轨'] - 标准差倍数 * df['标准差']
    df['信号'] = 0
    # 触及下轨买入信号
    df.loc[df['收盘'] <= df['下轨'], '信号'] = 1
    # 触及上轨卖出信号
    df.loc[df['收盘'] >= df['上轨'], '信号'] = -1
    return df


def 计算RSI(df, 周期):
    """计算RSI指标"""
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=周期).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=周期).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['信号'] = 0
    return df


def 执行双均线回测(df, 初始资金, 手续费率):
    """执行双均线回测"""
    持仓 = 0
    资金 = 初始资金
    总资产 = [初始资金]
    交易记录 = []
    
    for i in range(1, len(df)):
        当前收盘 = df.iloc[i]['收盘']
        
        if df.iloc[i]['信号'] == 1 and 持仓 == 0:
            买入量 = int(资金 / 当前收盘 / 100) * 100
            if 买入量 > 0:
                手续费 = 买入量 * 当前收盘 * 手续费率
                资金 -= (买入量 * 当前收盘 + 手续费)
                持仓 = 买入量
                交易记录.append({'日期': df.iloc[i]['日期'], '动作': '买入', '价格': 当前收盘, '数量': 买入量})
                
        elif df.iloc[i]['信号'] == -1 and 持仓 > 0:
            手续费 = 持仓 * 当前收盘 * 手续费率
            资金 += (持仓 * 当前收盘 - 手续费)
            交易记录.append({'日期': df.iloc[i]['日期'], '动作': '卖出', '价格': 当前收盘, '数量': 持仓})
            持仓 = 0
            
        当前总资产 = 资金 + (持仓 * 当前收盘 if 持仓 > 0 else 0)
        总资产.append(当前总资产)
    
    if 持仓 > 0:
        最后价格 = df.iloc[-1]['收盘']
        手续费 = 持仓 * 最后价格 * 手续费率
        资金 += (持仓 * 最后价格 - 手续费)
        交易记录.append({'日期': df.iloc[-1]['日期'], '动作': '清仓', '价格': 最后价格, '数量': 持仓})
        总资产[-1] = 资金
    
    return {'初始资金': 初始资金, '最终资金': 资金, '总资产曲线': 总资产, '交易记录': 交易记录, '数据': df}


def 执行买入持有回测(df, 初始资金, 手续费率):
    """执行买入持有策略"""
    首日价格 = df.iloc[0]['收盘']
    末日价格 = df.iloc[-1]['收盘']
    买入量 = int(初始资金 / 首日价格 / 100) * 100
    买入手续费 = 买入量 * 首日价格 * 手续费率
    资金 = 初始资金 - (买入量 * 首日价格 + 买入手续费)
    持仓 = 买入量
    
    总资产 = []
    for i in range(len(df)):
        当前总资产 = 资金 + (持仓 * df.iloc[i]['收盘'])
        总资产.append(当前总资产)
    
    卖出手续费 = 持仓 * 末日价格 * 手续费率
    最终资金 = 资金 + (持仓 * 末日价格 - 卖出手续费)
    总资产[-1] = 最终资金
    
    return {'初始资金': 初始资金, '最终资金': 最终资金, '总资产曲线': 总资产, '交易记录': [], '数据': df}


def 执行隔夜套利回测(df, 初始资金, 手续费率):
    """执行隔夜套利策略"""
    资金 = 初始资金
    持仓 = 0
    总资产 = [初始资金]
    交易记录 = []
    
    for i in range(len(df) - 1):
        今日收盘 = df.iloc[i]['收盘']
        次日收盘 = df.iloc[i + 1]['收盘']
        
        if 持仓 == 0:
            买入量 = int(资金 / 今日收盘 / 100) * 100
            if 买入量 > 0:
                手续费 = 买入量 * 今日收盘 * 手续费率
                资金 -= (买入量 * 今日收盘 + 手续费)
                持仓 = 买入量
                交易记录.append({'日期': df.iloc[i]['日期'], '动作': '买入', '价格': 今日收盘, '数量': 买入量})
        
        if 持仓 > 0:
            手续费 = 持仓 * 次日收盘 * 手续费率
            资金 += (持仓 * 次日收盘 - 手续费)
            交易记录.append({'日期': df.iloc[i + 1]['日期'], '动作': '卖出', '价格': 次日收盘, '数量': 持仓})
            持仓 = 0
        
        总资产.append(资金)
    
    return {'初始资金': 初始资金, '最终资金': 资金, '总资产曲线': 总资产, '交易记录': 交易记录, '数据': df}


def 执行布林带回测(df, 初始资金, 手续费率):
    """执行布林带策略回测"""
    持仓 = 0
    资金 = 初始资金
    总资产 = [初始资金]
    交易记录 = []
    
    for i in range(1, len(df)):
        当前收盘 = df.iloc[i]['收盘']
        
        if df.iloc[i]['信号'] == 1 and 持仓 == 0:
            买入量 = int(资金 / 当前收盘 / 100) * 100
            if 买入量 > 0:
                手续费 = 买入量 * 当前收盘 * 手续费率
                资金 -= (买入量 * 当前收盘 + 手续费)
                持仓 = 买入量
                交易记录.append({'日期': df.iloc[i]['日期'], '动作': '买入', '价格': 当前收盘, '数量': 买入量})
                
        elif df.iloc[i]['信号'] == -1 and 持仓 > 0:
            手续费 = 持仓 * 当前收盘 * 手续费率
            资金 += (持仓 * 当前收盘 - 手续费)
            交易记录.append({'日期': df.iloc[i]['日期'], '动作': '卖出', '价格': 当前收盘, '数量': 持仓})
            持仓 = 0
            
        当前总资产 = 资金 + (持仓 * 当前收盘 if 持仓 > 0 else 0)
        总资产.append(当前总资产)
    
    return {'初始资金': 初始资金, '最终资金': 资金, '总资产曲线': 总资产, '交易记录': 交易记录, '数据': df}


def 执行RSI回测(df, 初始资金, 手续费率, 超卖阈值=30, 超买阈值=70):
    """执行RSI策略回测"""
    持仓 = 0
    资金 = 初始资金
    总资产 = [初始资金]
    交易记录 = []
    
    for i in range(1, len(df)):
        当前收盘 = df.iloc[i]['收盘']
        rsi = df.iloc[i]['RSI'] if 'RSI' in df.columns else 50
        
        if rsi < 超卖阈值 and 持仓 == 0:
            买入量 = int(资金 / 当前收盘 / 100) * 100
            if 买入量 > 0:
                手续费 = 买入量 * 当前收盘 * 手续费率
                资金 -= (买入量 * 当前收盘 + 手续费)
                持仓 = 买入量
                交易记录.append({'日期': df.iloc[i]['日期'], '动作': '买入', '价格': 当前收盘, '数量': 买入量})
                
        elif rsi > 超买阈值 and 持仓 > 0:
            手续费 = 持仓 * 当前收盘 * 手续费率
            资金 += (持仓 * 当前收盘 - 手续费)
            交易记录.append({'日期': df.iloc[i]['日期'], '动作': '卖出', '价格': 当前收盘, '数量': 持仓})
            持仓 = 0
            
        当前总资产 = 资金 + (持仓 * 当前收盘 if 持仓 > 0 else 0)
        总资产.append(当前总资产)
    
    return {'初始资金': 初始资金, '最终资金': 资金, '总资产曲线': 总资产, '交易记录': 交易记录, '数据': df}


def 绘制多策略曲线(df, 标题="多策略净值曲线对比"):
    """使用Plotly绘制多策略净值曲线"""
    fig = go.Figure()
    
    colors = {
        '双均线策略': '#FF6B6B',
        '买入持有': '#4ECDC4',
        '隔夜套利': '#45B7D1',
        '布林带策略': '#96CEB4',
        'RSI策略': '#FFEAA7',
        '基准': '#DFE6E9'
    }
    
    for col in df.columns:
        if col != '日期':
            color = colors.get(col, '#74B9FF')
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col],
                mode='lines',
                name=col,
                line=dict(width=2, color=color),
                hovertemplate='%{x|%Y-%m-%d}<br>%{y:,.0f}<extra></extra>'
            ))
    
    fig.update_layout(
        title=dict(text=标题, x=0.5, font=dict(size=20)),
        xaxis=dict(title='日期', gridcolor='#E8E8E8'),
        yaxis=dict(title='资产净值 (¥)', gridcolor='#E8E8E8', tickformat=',.0f'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='white',
        height=500
    )
    
    return fig


def 显示多策略结果(策略结果, 策略净值曲线, 股票代码, 初始资金):
    """显示多策略回测结果"""
    
    st.markdown("---")
    
    # ==================== 多策略净值曲线图 ====================
    st.subheader("📈 多策略净值曲线对比")
    
    fig = 绘制多策略曲线(策略净值曲线, f"{股票代码} - 多策略净值曲线对比")
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 策略性能指标对比表 ====================
    st.subheader("📊 策略性能指标对比")
    
    性能数据 = []
    for 策略名, 结果 in 策略结果.items():
        最终资金 = 结果['最终资金']
        总收益率 = (最终资金 - 初始资金) / 初始资金 * 100
        年化收益率 = 总收益率 / (len(结果['数据']) / 252) if len(结果['数据']) > 0 else 0
        交易次数 = len(结果['交易记录'])
        
        性能数据.append({
            "策略名称": 策略名,
            "最终资金": f"¥{最终资金:,.0f}",
            "总收益率": f"{总收益率:+.2f}%",
            "年化收益率": f"{年化收益率:+.2f}%",
            "交易次数": 交易次数
        })
    
    if 性能数据:
        st.dataframe(
            pd.DataFrame(性能数据),
            use_container_width=True,
            hide_index=True,
            column_config={
                "策略名称": st.column_config.TextColumn("策略名称", width="small"),
                "最终资金": st.column_config.TextColumn("最终资金", width="small"),
                "总收益率": st.column_config.TextColumn("总收益率", width="small"),
                "年化收益率": st.column_config.TextColumn("年化收益率", width="small"),
                "交易次数": st.column_config.NumberColumn("交易次数", width="small"),
            }
        )
    
    # ==================== 各策略详细结果（可折叠） ====================
    st.subheader("📋 各策略详细结果")
    
    for 策略名, 结果 in 策略结果.items():
        with st.expander(f"{策略名} - 详细结果"):
            col1, col2, col3 = st.columns(3)
            col1.metric("初始资金", f"¥{结果['初始资金']:,.0f}")
            col2.metric("最终资金", f"¥{结果['最终资金']:,.0f}")
            收益率 = (结果['最终资金'] - 结果['初始资金']) / 结果['初始资金'] * 100
            col3.metric("收益率", f"{收益率:+.2f}%")
            
            if 结果['交易记录']:
                st.caption(f"共 {len(结果['交易记录'])} 条交易记录")
                交易_df = pd.DataFrame(结果['交易记录'])
                st.dataframe(交易_df, use_container_width=True, hide_index=True)
            else:
                st.info("无交易记录")
    
    # ==================== 策略总结 ====================
    st.markdown("---")
    st.subheader("💡 策略总结")
    
    # 找出最优策略
    if 策略结果:
        最优策略 = max(策略结果.items(), key=lambda x: x[1]['最终资金'])
        st.success(f"🏆 本次回测最优策略：**{最优策略[0]}**，最终资金 ¥{最优策略[1]['最终资金']:,.0f}，收益率 {((最优策略[1]['最终资金'] - 初始资金) / 初始资金 * 100):+.2f}%")
