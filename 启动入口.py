# ... 前面的导入和初始化代码 ...

st.markdown('<h1 style="text-align:center; color:#3b82f6">📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#94a3b8">多类目 · 多策略 · AI自动交易 | 云端部署</p>', unsafe_allow_html=True)

# ========== 显示消息 ==========
if '成功消息' in st.session_state and st.session_state['成功消息']:
    st.success(st.session_state['成功消息'])
    st.session_state['成功消息'] = None

if '错误消息' in st.session_state and st.session_state['错误消息']:
    st.error(st.session_state['错误消息'])
    st.session_state['错误消息'] = None

# ========== 创建Tab ==========
tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线", "回测"])
# ... 后续代码不变 ...
