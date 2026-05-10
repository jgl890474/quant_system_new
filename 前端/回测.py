# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


def 显示(引擎=None):
    """
    显示回测页面
    参数:
        引擎: 订单引擎实例（可选，用于获取实盘数据）
    """
    st.subheader("📈 策略回测")
    
    # 侧边栏参数设置
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")
        
        股票代码 = st.text_input("股票代码", value="000001", help="请输入6位股票代码，如：000001（平安银行）")
        开始日期 = st.date_input("开始日期", value=datetime.date(2024, 1, 1))
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.0003, step=0.0001, format="%.4f", help="默认万分之三")
        
        st.markdown("---")
        st.markdown("### 📊 策略参数")
        
        策略类型 = st.selectbox("回测策略", ["双均线策略", "买入持有策略", "隔夜套利策略"], index=0)
        
        if 策略类型 == "双均线策略":
            短期均线 = st.selectbox("短期均线", [5, 10, 20], index=0)
            长期均线 = st.selectbox("长期均线", [20, 30, 60], index=1)
        else:
            短期均线 = 5
            长期均线 = 20
        
        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", use_container_width=True)
    
    # 主界面提示
    st.markdown("""
    > 💡 **使用说明**：在左侧设置回测参数，点击「开始回测」按钮查看结果。
    > 
    > **策略说明**：
    > - 双均线策略：金叉买入，死叉卖出
    > - 买入持有策略：一次性买入并持有到回测结束
    > - 隔夜套利策略：每日尾盘买入，次日尾盘卖出
    """)
    
    if not 运行按钮:
        # 显示示例图表
        st.info("👈 请在左侧设置参数并点击「开始回测」")
        
        # 显示示例回测曲线
        with st.expander("📈 示例：沪深300指数回测（点击展开）"):
            demo_df = pd.DataFrame({
                "日期": pd.date_range("2024-01-01", periods=100),
                "净值": np.cumprod(1 + np.random.randn(100) * 0.01)
            })
            st.line_chart(demo_df.set_index("日期"))
            st.caption("注：此为演示数据，实际回测请点击「开始回测」")
        return
    
    # ==================== 执行回测 ====================
    with st.spinner("正在获取数据并进行回测，请稍候..."):
        try:
            # 获取股票历史数据
            df = 获取股票历史数据(股票代码, 开始日期, 结束日期)
            
            if df is None or df.empty:
                st.error(f"❌ 无法获取股票 {股票代码} 的历史数据")
                st.info("请检查股票代码是否正确，或更换其他股票代码（如：000001、600036）")
                return
            
            st.success(f"✅ 成功获取 {len(df)} 条历史数据")
            
            # 根据策略类型执行回测
            if 策略类型 == "双均线策略":
                # 计算技术指标
                df = 计算均线(df, 短期均线, 长期均线)
                结果 = 执行双均线回测(df, 初始资金, 手续费率)
            elif 策略类型 == "买入持有策略":
                结果 = 执行买入持有回测(df, 初始资金, 手续费率)
            else:
                结果 = 执行隔夜套利回测(df, 初始资金, 手续费率)
            
            # 显示回测结果
            显示回测结果(结果, 股票代码, 短期均线, 长期均线, 策略类型)
            
        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def 获取股票历史数据(股票代码, 开始日期, 结束日期):
    """获取股票历史日线数据"""
    
    # 补齐6位代码格式
    代码 = str(股票代码).zfill(6)
    
    # 方法1：使用 akshare
    if AKSHARE_AVAILABLE:
        try:
            df = ak.stock_zh_a_hist(
                symbol=代码,
                period="daily",
                start_date=开始日期.strftime("%Y%m%d"),
                end_date=结束日期.strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            if df is not None and not df.empty:
                # 标准化列名
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
    df_copy['信号'] = 0
    
    # 金叉：短期上穿长期
    df_copy['信号'] = np.where(
        (df_copy['MA_短期'] > df_copy['MA_长期']) & 
        (df_copy['MA_短期'].shift(1) <= df_copy['MA_长期'].shift(1)), 
        1, 0
    )
    # 死叉：短期下穿长期
    df_copy['信号'] = np.where(
        (df_copy['MA_短期'] < df_copy['MA_长期']) & 
        (df_copy['MA_短期'].shift(1) >= df_copy['MA_长期'].shift(1)), 
        -1, df_copy['信号']
    )
    
    return df_copy


def 执行双均线回测(df, 初始资金, 手续费率):
    """执行双均线回测"""
    
    持仓 = 0
    资金 = 初始资金
    总资产 = [初始资金]
    持仓市值 = [0]
    交易记录 = []
    
    for i in range(1, len(df)):
        当前收盘 = df.iloc[i]['收盘']
        
        if df.iloc[i]['信号'] == 1 and 持仓 == 0:
            # 买入信号
            买入量 = int(资金 / 当前收盘 / 100) * 100
            if 买入量 > 0:
                手续费 = 买入量 * 当前收盘 * 手续费率
                资金 -= (买入量 * 当前收盘 + 手续费)
                持仓 = 买入量
                交易记录.append({
                    '日期': df.iloc[i]['日期'],
                    '动作': '买入',
                    '价格': 当前收盘,
                    '数量': 买入量,
                    '手续费': round(手续费, 2),
                    '盈亏': None
                })
                
        elif df.iloc[i]['信号'] == -1 and 持仓 > 0:
            # 卖出信号
            手续费 = 持仓 * 当前收盘 * 手续费率
            资金 += (持仓 * 当前收盘 - 手续费)
            盈利 = (当前收盘 - 交易记录[-1]['价格']) * 持仓 - 手续费 - (交易记录[-1]['价格'] * 持仓 * 手续费率)
            交易记录.append({
                '日期': df.iloc[i]['日期'],
                '动作': '卖出',
                '价格': 当前收盘,
                '数量': 持仓,
                '盈亏': round(盈利, 2),
                '手续费': round(手续费, 2)
            })
            持仓 = 0
            
        当前总资产 = 资金 + (持仓 * 当前收盘 if 持仓 > 0 else 0)
        总资产.append(当前总资产)
        持仓市值.append(持仓 * 当前收盘 if 持仓 > 0 else 0)
    
    # 最终清仓
    if 持仓 > 0:
        最后价格 = df.iloc[-1]['收盘']
        手续费 = 持仓 * 最后价格 * 手续费率
        资金 += (持仓 * 最后价格 - 手续费)
        盈利 = (最后价格 - 交易记录[-1]['价格']) * 持仓 - 手续费
        交易记录.append({
            '日期': df.iloc[-1]['日期'],
            '动作': '清仓',
            '价格': 最后价格,
            '数量': 持仓,
            '盈亏': round(盈利, 2),
            '手续费': round(手续费, 2)
        })
        持仓 = 0
        当前总资产 = 资金
        总资产[-1] = 当前总资产
        持仓市值[-1] = 0
    
    结果 = {
        '初始资金': 初始资金,
        '最终资金': 资金,
        '总资产曲线': 总资产,
        '持仓市值曲线': 持仓市值,
        '交易记录': 交易记录,
        '数据': df,
        '手续费率': 手续费率
    }
    
    return 结果


def 执行买入持有回测(df, 初始资金, 手续费率):
    """执行买入持有策略回测"""
    
    首日价格 = df.iloc[0]['收盘']
    末日价格 = df.iloc[-1]['收盘']
    
    # 首日买入
    买入量 = int(初始资金 / 首日价格 / 100) * 100
    买入手续费 = 买入量 * 首日价格 * 手续费率
    资金 = 初始资金 - (买入量 * 首日价格 + 买入手续费)
    持仓 = 买入量
    
    # 每日资产曲线
    总资产 = []
    for i in range(len(df)):
        当前价格 = df.iloc[i]['收盘']
        当前总资产 = 资金 + (持仓 * 当前价格)
        总资产.append(当前总资产)
    
    # 末日卖出
    卖出手续费 = 持仓 * 末日价格 * 手续费率
    最终资金 = 资金 + (持仓 * 末日价格 - 卖出手续费)
    
    交易记录 = [
        {
            '日期': df.iloc[0]['日期'],
            '动作': '买入',
            '价格': 首日价格,
            '数量': 买入量,
            '手续费': round(买入手续费, 2),
            '盈亏': None
        },
        {
            '日期': df.iloc[-1]['日期'],
            '动作': '卖出',
            '价格': 末日价格,
            '数量': 买入量,
            '盈亏': round(最终资金 - 初始资金, 2),
            '手续费': round(卖出手续费, 2)
        }
    ]
    
    结果 = {
        '初始资金': 初始资金,
        '最终资金': 最终资金,
        '总资产曲线': 总资产,
        '持仓市值曲线': [持仓 * df.iloc[i]['收盘'] for i in range(len(df))],
        '交易记录': 交易记录,
        '数据': df,
        '手续费率': 手续费率
    }
    
    return 结果


def 执行隔夜套利回测(df, 初始资金, 手续费率):
    """执行隔夜套利策略回测（每日尾盘买入，次日尾盘卖出）"""
    
    资金 = 初始资金
    持仓 = 0
    总资产 = [初始资金]
    持仓市值 = [0]
    交易记录 = []
    
    for i in range(1, len(df)):
        if i < len(df) - 1:
            # 今日尾盘买入
            今日收盘 = df.iloc[i]['收盘']
            if 持仓 == 0:
                买入量 = int(资金 / 今日收盘 / 100) * 100
                if 买入量 > 0:
                    手续费 = 买入量 * 今日收盘 * 手续费率
                    资金 -= (买入量 * 今日收盘 + 手续费)
                    持仓 = 买入量
                    交易记录.append({
                        '日期': df.iloc[i]['日期'],
                        '动作': '买入',
                        '价格': 今日收盘,
                        '数量': 买入量,
                        '手续费': round(手续费, 2),
                        '盈亏': None
                    })
            
            # 次日尾盘卖出
            次日收盘 = df.iloc[i + 1]['收盘']
            if 持仓 > 0:
                手续费 = 持仓 * 次日收盘 * 手续费率
                盈利 = (次日收盘 - 今日收盘) * 持仓 - 手续费
                资金 += (持仓 * 次日收盘 - 手续费)
                交易记录.append({
                    '日期': df.iloc[i + 1]['日期'],
                    '动作': '卖出',
                    '价格': 次日收盘,
                    '数量': 持仓,
                    '盈亏': round(盈利, 2),
                    '手续费': round(手续费, 2)
                })
                持仓 = 0
        
        当前总资产 = 资金 + (持仓 * df.iloc[i]['收盘'] if 持仓 > 0 else 0)
        总资产.append(当前总资产)
        持仓市值.append(持仓 * df.iloc[i]['收盘'] if 持仓 > 0 else 0)
    
    结果 = {
        '初始资金': 初始资金,
        '最终资金': 资金,
        '总资产曲线': 总资产,
        '持仓市值曲线': 持仓市值,
        '交易记录': 交易记录,
        '数据': df,
        '手续费率': 手续费率
    }
    
    return 结果


def 显示回测结果(结果, 股票代码, 短期均线, 长期均线, 策略类型):
    """显示回测结果"""
    
    st.markdown("---")
    
    # ===== 核心指标卡片 =====
    初始资金 = 结果['初始资金']
    最终资金 = 结果['最终资金']
    收益率 = (最终资金 - 初始资金) / 初始资金 * 100
    盈亏额 = 最终资金 - 初始资金
    
    买入次数 = len([t for t in 结果['交易记录'] if t['动作'] == '买入'])
    卖出次数 = len([t for t in 结果['交易记录'] if t['动作'] in ['卖出', '清仓']])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("初始资金", f"¥{初始资金:,.0f}")
    col2.metric("最终资金", f"¥{最终资金:,.0f}", delta=f"¥{盈亏额:+,.0f}")
    col3.metric("收益率", f"{收益率:+.2f}%")
    col4.metric("交易次数", f"{买入次数} / {卖出次数}")
    
    st.markdown("---")
    
    # ===== 资金曲线图 =====
    st.subheader("📈 资金曲线")
    
    曲线数据 = pd.DataFrame({
        '日期': 结果['数据']['日期'],
        '总资产': 结果['总资产曲线'][1:] if len(结果['总资产曲线']) > len(结果['数据']) else 结果['总资产曲线'],
        '基准': 结果['数据']['收盘'] / 结果['数据']['收盘'].iloc[0] * 初始资金
    })
    
    # 确保长度一致
    min_len = min(len(曲线数据), len(结果['总资产曲线'][1:]) if len(结果['总资产曲线']) > len(结果['数据']) else len(结果['总资产曲线']))
    曲线数据 = 曲线数据.iloc[:min_len]
    
    st.line_chart(曲线数据.set_index('日期')[['总资产', '基准']])
    
    # ===== 交易记录表格 =====
    if 结果['交易记录']:
        st.subheader("📋 交易记录")
        
        交易记录_df = pd.DataFrame(结果['交易记录'])
        
        if not 交易记录_df.empty:
            # 显示表格
            st.dataframe(
                交易记录_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "日期": st.column_config.TextColumn("日期", width="small"),
                    "动作": st.column_config.TextColumn("动作", width="small"),
                    "价格": st.column_config.NumberColumn("价格", format="%.2f"),
                    "数量": st.column_config.NumberColumn("数量", format="%.0f"),
                    "盈亏": st.column_config.NumberColumn("盈亏", format="%.2f"),
                    "手续费": st.column_config.NumberColumn("手续费", format="%.2f"),
                }
            )
            
            # 盈亏统计
            卖出记录 = 交易记录_df[交易记录_df['动作'].isin(['卖出', '清仓'])]
            if not 卖出记录.empty and '盈亏' in 卖出记录.columns:
                总盈亏 = 卖出记录['盈亏'].sum()
                盈利次数 = len(卖出记录[卖出记录['盈亏'] > 0])
                亏损次数 = len(卖出记录[卖出记录['盈亏'] < 0])
                
                col1, col2, col3 = st.columns(3)
                col1.metric("总盈亏", f"¥{总盈亏:,.2f}")
                if 盈利次数 + 亏损次数 > 0:
                    col2.metric("胜率", f"{盈利次数/(盈利次数+亏损次数)*100:.1f}%")
                col3.metric("交易次数", f"{盈利次数}/{亏损次数}")

    else:
        st.info("本次回测没有产生任何交易信号")
    
    # ===== 策略参数摘要 =====
    with st.expander("📖 策略参数摘要"):
        st.markdown(f"""
        - **股票代码**: {股票代码}
        - **回测区间**: {结果['数据']['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {结果['数据']['日期'].iloc[-1].strftime('%Y-%m-%d')}
        - **策略类型**: {策略类型}
        """)
        
        if 策略类型 == "双均线策略":
            st.markdown(f"""
            - **短期均线**: {短期均线}日
            - **长期均线**: {长期均线}日
            """)
        
        st.markdown(f"""
        - **手续费率**: {结果['手续费率']*100:.2f}%
        - **初始资金**: ¥{结果['初始资金']:,.0f}
        - **最终资金**: ¥{结果['最终资金']:,.0f}
        - **收益率**: {((结果['最终资金'] - 结果['初始资金'])/结果['初始资金']*100):.2f}%
        """)
