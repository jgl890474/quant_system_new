# ... 前面的导入保持不变，添加 , 回测

from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测

# ... 中间不变

# ========== 创建7个Tab ==========
tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线", "回测", "快速交易"])

# ... 前面的 tabs 不变

with tabs[5]:
    回测.显示()

with tabs[6]:
    # 快速交易代码
    st.markdown("### 快速交易")
    品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD"])
    from 核心 import 行情获取
    当前价格 = 行情获取.获取价格(品种).价格
    st.info(f"当前价格: {当前价格}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("买入", type="primary"):
            引擎.买入(品种, 当前价格)
            st.rerun()
    with col2:
        if st.button("卖出"):
            引擎.卖出(品种, 当前价格)
            st.rerun()
