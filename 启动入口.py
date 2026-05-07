# 在现有的 st.markdown 样式后面添加以下内容

st.markdown("""
<style>
    /* 全局字体缩小 */
    .stApp {
        font-size: 13px;
    }
    
    /* 指标卡片字体 */
    .stMetric label {
        font-size: 12px !important;
    }
    .stMetric value {
        font-size: 20px !important;
    }
    
    /* 标题缩小 */
    h1 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 16px !important;
    }
    h4 {
        font-size: 14px !important;
    }
    
    /* 按钮缩小 */
    .stButton button {
        font-size: 12px !important;
        padding: 4px 12px !important;
    }
    
    /* 表格字体 */
    .dataframe td, .dataframe th {
        font-size: 12px !important;
        padding: 4px 8px !important;
    }
    
    /* 选择框字体 */
    .stSelectbox label, .stNumberInput label {
        font-size: 12px !important;
    }
    
    /* 信息框字体 */
    .stAlert, .stInfo, .stWarning, .stSuccess {
        font-size: 12px !important;
        padding: 8px !important;
    }
    
    /* 指标卡片区域间距 */
    .stMetric {
        padding: 8px !important;
    }
    
    /* 行列间距 */
    .row-widget {
        margin-bottom: 8px !important;
    }
    
    /* 分割线样式 */
    hr {
        margin: 8px 0 !important;
        border-color: #334155 !important;
    }
    
    /* K线图线条变细 */
    .main-svg {
        stroke-width: 0.5px !important;
    }
    
    /* 标签页字体 */
    .stTabs [data-baseweb="tab"] {
        font-size: 12px !important;
        padding: 6px 16px !important;
    }
    
    /* 侧边栏字体 */
    [data-testid="stSidebar"] {
        font-size: 12px !important;
    }
    
    /* 展开器字体 */
    .streamlit-expanderHeader {
        font-size: 13px !important;
    }
    
    /* 代码块字体 */
    code {
        font-size: 11px !important;
    }
    
    /* 指标卡片紧凑 */
    .element-container {
        margin-bottom: 8px !important;
    }
    
    /* 图表线条变细 */
    .plotly .main-svg {
        stroke-width: 0.8px !important;
    }
    
    /* 卡片间距 */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)
