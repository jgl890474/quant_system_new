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
    显示回测页面 - 持仓动态回测
    参数:
        引擎: 订单引擎实例（可选，用于获取实盘数据）
    """
    st.subheader("📈 持仓动态回测")
    
    # ==================== 侧边栏参数设置 ====================
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")
        
        股票代码 = st.text_input("股票代码", value="000001", help="请输入6位股票代码，如：000001（平安银行）")
        开始日期 = st.date_input("开始日期", value=datetime.date(2024, 1, 1))
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.0003, step=0.0001, format="%.4f", help="默认万分之三")
        
        st.markdown("---")
        st.markdown("### 📊 策略参数")
        
        # 均线策略参数
        短期均线 = st.slider("短期均线（买入信号）", 3, 30, 5, 1)
        长期均线 = st.slider("长期均线（卖出信号）", 10, 60, 20, 1)
        
        st.markdown("---")
        st.markdown("### 🎯 止盈止损")
        
        止盈百分比 = st.number_input("止盈目标 (%)", value=5.0, step=1.0, min_value=0.0, max_value=50.0)
        止损百分比 = st.number_input("止损目标 (%)", value=-3.0, step=0.5, min_value=-30.0, max_value=0.0)
        
        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", use_container_width=True)
    
    # 主界面提示
    st.markdown("""
    > 💡 **使用说明**：在左侧设置回测参数，点击「开始回测」查看持仓回测结果。
    > 
    > **策略说明**：双均线交叉策略（金叉买入，死叉卖出），支持止盈止损控制。
    """)
    
    if not 运行按钮:
        # 显示示例图表
        st.info("👈 请在左侧设置参数并点击「开始回测」")
        
        # 显示示例回测曲线
        with st.expander("📈 示例：持仓回测曲线（点击展开）"):
            dates = pd.date_range("2024-01-01", periods=100)
            demo_df = pd.DataFrame({
                "日期": dates,
                "净值": 1000000 * np.cumprod(1 + np.random.randn(100) * 0.01)
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=demo_df['日期'], y=demo_df['净值'],
                mode='lines', name='资金曲线',
                line=dict(color='#FF6B6B', width=2),
                fill='tozeroy', fillcolor='rgba(255,107,107,0.1)'
            ))
            fig.update_layout(
                title="示例：资金曲线",
                xaxis_title="日期",
                yaxis_title="资产净值 (¥)",
                hovermode='x unified',
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("注：此为演示数据，实际回测请点击「开始回测」")
        return
    
    # ==================== 执行回测 ====================
    with st.spinner("正在获取数据并执行回测，请稍候..."):
        try:
            # 获取股票历史数据
            df = 获取股票历史数据(股票代码, 开始日期, 结束日期)
            
            if df is None or df.empty:
                st.error(f"❌ 无法获取股票 {股票代码} 的历史数据")
                st.info("请检查股票代码是否正确，或更换其他股票代码（如：000001、600036、000858）")
                return
            
            st.success(f"✅ 成功获取 {len(df)} 条历史数据")
            st.caption(f"📅 回测区间：{df['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {df['日期'].iloc[-1].strftime('%Y-%m-%d')}")
            
            # 计算技术指标
            df = 计算均线(df, 短期均线, 长期均线)
            
            # 执行回测
            回测结果 = 执行持仓回测(
                df, 初始资金, 手续费率, 
                止盈百分比 / 100, 止损百分比 / 100
            )
            
            # 显示回测结果
            显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比)
            
        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            with st.expander("详细错误信息"):
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
    df_copy = df.copy()
    df_copy['MA_短期'] = df_copy['收盘'].rolling(window=短期均线).mean()
    df_copy['MA_长期'] = df_copy['收盘'].rolling(window=长期均线).mean()
    df_copy['持仓'] = 0
    df_copy['信号'] = 0
    
    # 金叉：短期上穿长期 -> 买入信号 (1)
    # 死叉：短期下穿长期 -> 卖出信号 (-1)
    for i in range(1, len(df_copy)):
        if df_copy['MA_短期'].iloc[i] > df_copy['MA_长期'].iloc[i]:
            if df_copy['MA_短期'].iloc[i-1] <= df_copy['MA_长期'].iloc[i-1]:
                df_copy.loc[df_copy.index[i], '信号'] = 1  # 金叉买入
        elif df_copy['MA_短期'].iloc[i] < df_copy['MA_长期'].iloc[i]:
            if df_copy['MA_短期'].iloc[i-1] >= df_copy['MA_长期'].iloc[i-1]:
                df_copy.loc[df_copy.index[i], '信号'] = -1  # 死叉卖出
    
    return df_copy


def 执行持仓回测(df, 初始资金, 手续费率, 止盈率, 止损率):
    """执行持仓回测 - 包含止盈止损"""
    
    资金 = 初始资金
    持仓数量 = 0
    持仓成本 = 0
    持仓记录 = []
    交易记录 = []
    每日资产 = []
    每日持仓市值 = []
    每日现金 = []
    
    买入价 = 0
    
    for i in range(len(df)):
        当前日期 = df['日期'].iloc[i]
        当前收盘 = df['收盘'].iloc[i]
        
        # 检查持仓中的止盈止损
        止盈触发 = False
        止损触发 = False
        
        if 持仓数量 > 0 and 买入价 > 0:
            当前盈亏率 = (当前收盘 - 买入价) / 买入价
            if 止盈率 > 0 and 当前盈亏率 >= 止盈率:
                止盈触发 = True
            if 止损率 < 0 and 当前盈亏率 <= 止损率:
                止损触发 = True
        
        # 止盈止损卖出
        if (止盈触发 or 止损触发) and 持仓数量 > 0:
            卖出金额 = 持仓数量 * 当前收盘
            手续费 = 卖出金额 * 手续费率
            实际收入 = 卖出金额 - 手续费
            资金 += 实际收入
            盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
            
            交易记录.append({
                '日期': 当前日期,
                '行动': '止盈卖出' if 止盈触发 else '止损卖出',
                '价格': 当前收盘,
                '数量': 持仓数量,
                '手续费': round(手续费, 2),
                '资金变动': round(实际收入, 2),
                '盈亏': round(盈亏, 2)
            })
            
            持仓记录.append({
                '品种': df.get('代码', ['未知'])[0] if '代码' in df else '未知',
                '买入价': 买入价,
                '卖出价': 当前收盘,
                '数量': 持仓数量,
                '盈亏': round(盈亏, 2)
            })
            
            持仓数量 = 0
            持仓成本 = 0
            买入价 = 0
        
        # 检查买入信号
        elif df['信号'].iloc[i] == 1 and 持仓数量 == 0:
            # 买入
            可用资金 = 资金
            买入数量 = int(可用资金 / 当前收盘 / 100) * 100
            
            if 买入数量 > 0:
                买入金额 = 买入数量 * 当前收盘
                手续费 = 买入金额 * 手续费率
                资金 -= (买入金额 + 手续费)
                持仓数量 = 买入数量
                持仓成本 = 当前收盘
                买入价 = 当前收盘
                
                交易记录.append({
                    '日期': 当前日期,
                    '行动': '买入',
                    '价格': 当前收盘,
                    '数量': 持仓数量,
                    '手续费': round(手续费, 2),
                    '资金变动': round(-(买入金额 + 手续费), 2),
                    '盈亏': 0
                })
        
        # 检查卖出信号
        elif df['信号'].iloc[i] == -1 and 持仓数量 > 0:
            卖出金额 = 持仓数量 * 当前收盘
            手续费 = 卖出金额 * 手续费率
            实际收入 = 卖出金额 - 手续费
            资金 += 实际收入
            盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
            
            交易记录.append({
                '日期': 当前日期,
                '行动': '卖出(信号)',
                '价格': 当前收盘,
                '数量': 持仓数量,
                '手续费': round(手续费, 2),
                '资金变动': round(实际收入, 2),
                '盈亏': round(盈亏, 2)
            })
            
            持仓记录.append({
                '品种': df.get('代码', ['未知'])[0] if '代码' in df else '未知',
                '买入价': 买入价,
                '卖出价': 当前收盘,
                '数量': 持仓数量,
                '盈亏': round(盈亏, 2)
            })
            
            持仓数量 = 0
            持仓成本 = 0
            买入价 = 0
        
        # 计算每日资产
        当前持仓市值 = 持仓数量 * 当前收盘
        当日总资产 = 资金 + 当前持仓市值
        每日资产.append(当日总资产)
        每日持仓市值.append(当前持仓市值)
        每日现金.append(资金)
    
    # 回测结束 - 如果还有持仓，强制平仓
    if 持仓数量 > 0:
        最后价格 = df['收盘'].iloc[-1]
        卖出金额 = 持仓数量 * 最后价格
        手续费 = 卖出金额 * 手续费率
        实际收入 = 卖出金额 - 手续费
        资金 += 实际收入
        盈亏 = (最后价格 - 买入价) * 持仓数量 - 手续费
        
        交易记录.append({
            '日期': df['日期'].iloc[-1],
            '行动': '强制平仓',
            '价格': 最后价格,
            '数量': 持仓数量,
            '手续费': round(手续费, 2),
            '资金变动': round(实际收入, 2),
            '盈亏': round(盈亏, 2)
        })
        
        持仓记录.append({
            '品种': df.get('代码', ['未知'])[0] if '代码' in df else '未知',
            '买入价': 买入价,
            '卖出价': 最后价格,
            '数量': 持仓数量,
            '盈亏': round(盈亏, 2)
        })
        
        每日资产[-1] = 资金
        每日持仓市值[-1] = 0
        每日现金[-1] = 资金
    
    return {
        '初始资金': 初始资金,
        '最终资金': 资金,
        '总盈亏': 资金 - 初始资金,
        '总收益率': (资金 - 初始资金) / 初始资金 * 100,
        '每日资产': 每日资产,
        '每日持仓市值': 每日持仓市值,
        '每日现金': 每日现金,
        '交易记录': 交易记录,
        '持仓记录': 持仓记录,
        '数据': df,
        '手续费率': 手续费率
    }


def 绘制动态净值曲线(df, 回测结果, 股票代码):
    """使用Plotly绘制动态交互式净值曲线"""
    
    # 创建子图：资金曲线 + 持仓量
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=('资产净值曲线', '持仓量'),
        row_heights=[0.7, 0.3]
    )
    
    # 资金曲线
    fig.add_trace(
        go.Scatter(
            x=df['日期'],
            y=回测结果['每日资产'],
            mode='lines',
            name='总资产',
            line=dict(color='#FF6B6B', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,107,107,0.1)',
            hovertemplate='%{x|%Y-%m-%d}<br>总资产: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 现金曲线
    fig.add_trace(
        go.Scatter(
            x=df['日期'],
            y=回测结果['每日现金'],
            mode='lines',
            name='可用资金',
            line=dict(color='#4ECDC4', width=1.5, dash='dash'),
            hovertemplate='%{x|%Y-%m-%d}<br>可用资金: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 基准曲线（买入持有）
    基准曲线 = 回测结果['初始资金'] * df['收盘'] / df['收盘'].iloc[0]
    fig.add_trace(
        go.Scatter(
            x=df['日期'],
            y=基准曲线,
            mode='lines',
            name='买入持有(基准)',
            line=dict(color='#95A5A6', width=1.5, dash='dot'),
            hovertemplate='%{x|%Y-%m-%d}<br>基准: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 持仓市值（填充区域）
    fig.add_trace(
        go.Scatter(
            x=df['日期'],
            y=回测结果['每日持仓市值'],
            mode='lines',
            name='持仓市值',
            line=dict(color='#45B7D1', width=1.5),
            fill='tozeroy',
            fillcolor='rgba(69,183,209,0.15)',
            hovertemplate='%{x|%Y-%m-%d}<br>持仓市值: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 持仓量（第二子图）
    持仓量数据 = []
    当前持仓 = 0
    for i in range(len(df)):
        if i < len(回测结果['交易记录']):
            # 简化：根据交易记录计算持仓量（实际需要更复杂的逻辑）
            pass
        # 从每日持仓市值反推持仓量（粗略）
        持仓量 = 回测结果['每日持仓市值'][i] / df['收盘'].iloc[i] if df['收盘'].iloc[i] > 0 else 0
        持仓量数据.append(持仓量)
    
    fig.add_trace(
        go.Scatter(
            x=df['日期'],
            y=持仓量数据,
            mode='lines',
            name='持仓数量',
            line=dict(color='#F39C12', width=2),
            fill='tozeroy',
            fillcolor='rgba(243,156,18,0.1)',
            hovertemplate='%{x|%Y-%m-%d}<br>持仓: %{y:.0f}股<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 添加买卖点标记
    买入点 = 回测结果['数据'][回测结果['数据']['信号'] == 1]
    卖出点 = 回测结果['数据'][回测结果['数据']['信号'] == -1]
    
    if not 买入点.empty:
        fig.add_trace(
            go.Scatter(
                x=买入点['日期'],
                y=回测结果['每日资产'][买入点.index] if max(买入点.index) < len(回测结果['每日资产']) else [],
                mode='markers',
                name='买入信号',
                marker=dict(symbol='triangle-up', size=12, color='#2ECC71'),
                hovertemplate='买入信号<br>%{x|%Y-%m-%d}<extra></extra>'
            ),
            row=1, col=1
        )
    
    if not 卖出点.empty:
        fig.add_trace(
            go.Scatter(
                x=卖出点['日期'],
                y=回测结果['每日资产'][卖出点.index] if max(卖出点.index) < len(回测结果['每日资产']) else [],
                mode='markers',
                name='卖出信号',
                marker=dict(symbol='triangle-down', size=12, color='#E74C3C'),
                hovertemplate='卖出信号<br>%{x|%Y-%m-%d}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text=f"{股票代码} - 持仓回测资金曲线",
            x=0.5,
            font=dict(size=18)
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        height=600,
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(title_text="日期", row=2, col=1, gridcolor='#E8E8E8')
    fig.update_yaxes(title_text="资产净值 (¥)", row=1, col=1, gridcolor='#E8E8E8', tickformat=',.0f')
    fig.update_yaxes(title_text="持仓数量 (股)", row=2, col=1, gridcolor='#E8E8E8')
    
    return fig


def 显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比):
    """显示回测结果"""
    
    st.markdown("---")
    
    # ==================== 核心指标卡片 ====================
    st.subheader("📊 回测指标")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("初始资金", f"¥{回测结果['初始资金']:,.0f}")
    col2.metric("最终资金", f"¥{回测结果['最终资金']:,.0f}", 
                delta=f"¥{回测结果['总盈亏']:+,.0f}")
    col3.metric("总收益率", f"{回测结果['总收益率']:+.2f}%",
                delta=f"{回测结果['总收益率']:+.2f}%")
    col4.metric("最大回撤", "计算中...")
    col5.metric("交易次数", len([t for t in 回测结果['交易记录'] if t['行动'] in ['买入', '卖出(信号)']]))
    
    st.markdown("---")
    
    # ==================== 动态净值曲线 ====================
    st.subheader("📈 动态净值曲线")
    
    fig = 绘制动态净值曲线(回测结果['数据'], 回测结果, 股票代码)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 策略参数摘要 ====================
    with st.expander("📖 策略参数", expanded=False):
        col1, col2 = st.columns(2)
        col1.markdown(f"""
        - **股票代码**: {股票代码}
        - **回测区间**: {回测结果['数据']['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {回测结果['数据']['日期'].iloc[-1].strftime('%Y-%m-%d')}
        - **短期均线**: {短期均线}日
        - **长期均线**: {长期均线}日
        """)
        col2.markdown(f"""
        - **手续费率**: {回测结果['手续费率']*100:.2f}%
        - **止盈目标**: {止盈百分比}%
        - **止损目标**: {止损百分比}%
        - **初始资金**: ¥{回测结果['初始资金']:,.0f}
        """)
    
    # ==================== 收益分析图 ====================
    st.subheader("📊 收益分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 收益率分布图
        收益数据 = [t['盈亏'] for t in 回测结果['交易记录'] if t['盈亏'] != 0]
        if 收益数据:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['盈利交易', '亏损交易'],
                values=[len([x for x in 收益数据 if x > 0]), len([x for x in 收益数据 if x < 0])],
                marker_colors=['#2ECC71', '#E74C3C'],
                hole=0.4
            )])
            fig_pie.update_layout(title="盈亏交易比例", height=350)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("暂无盈亏数据")
    
    with col2:
        # 资金增长曲线
        if len(回测结果['每日资产']) > 0:
            增长数据 = pd.DataFrame({
                '日期': 回测结果['数据']['日期'],
                '总资产': 回测结果['每日资产'],
                '基准': 回测结果['初始资金'] * 回测结果['数据']['收盘'] / 回测结果['数据']['收盘'].iloc[0]
            })
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=增长数据['日期'], y=增长数据['总资产'], 
                                          name='策略收益', line=dict(color='#3498DB')))
            fig_line.add_trace(go.Scatter(x=增长数据['日期'], y=增长数据['基准'],
                                          name='基准收益', line=dict(color='#95A5A6', dash='dash')))
            fig_line.update_layout(title="策略 vs 基准", height=350, xaxis_title="日期", yaxis_title="资产净值 (¥)")
            st.plotly_chart(fig_line, use_container_width=True)
    
    # ==================== 交易记录表格 ====================
    if 回测结果['交易记录']:
        st.subheader("📋 交易记录")
        
        交易_df = pd.DataFrame(回测结果['交易记录'])
        st.dataframe(
            交易_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "日期": st.column_config.TextColumn("日期", width="small"),
                "行动": st.column_config.TextColumn("行动", width="small"),
                "价格": st.column_config.NumberColumn("价格", format="%.2f"),
                "数量": st.column_config.NumberColumn("数量", format="%.0f"),
                "手续费": st.column_config.NumberColumn("手续费", format="%.2f"),
                "盈亏": st.column_config.NumberColumn("盈亏", format="%.2f"),
            }
        )
        
        # 盈亏统计
        盈利交易 = [t for t in 回测结果['交易记录'] if t['盈亏'] > 0]
        亏损交易 = [t for t in 回测结果['交易记录'] if t['盈亏'] < 0]
        
        if 盈利交易 or 亏损交易:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总盈利", f"¥{sum(t['盈亏'] for t in 盈利交易):,.2f}" if 盈利交易 else "¥0")
            col2.metric("总亏损", f"¥{sum(t['盈亏'] for t in 亏损交易):,.2f}" if 亏损交易 else "¥0")
            col3.metric("盈利次数", len(盈利交易))
            col4.metric("亏损次数", len(亏损交易))
            
            if len(盈利交易) + len(亏损交易) > 0:
                胜率 = len(盈利交易) / (len(盈利交易) + len(亏损交易)) * 100
                st.metric("胜率", f"{胜率:.1f}%")
    
    else:
        st.info("本次回测没有产生任何交易记录")
    
    # ==================== 策略总结 ====================
    st.markdown("---")
    st.subheader("💡 回测总结")
    
    总收益率 = 回测结果['总收益率']
    if 总收益率 > 0:
        st.success(f"✅ 策略在回测区间内取得了 {总收益率:+.2f}% 的正收益")
    else:
        st.warning(f"⚠️ 策略在回测区间内取得了 {总收益率:+.2f}% 的负收益")
    
    # 建议
    st.markdown("""
    **⚠️ 风险提示**：
    - 历史回测结果不代表未来收益
    - 实际交易中可能存在滑点和流动性风险
    - 建议在实盘前进行充分的参数优化和压力测试
    """)
