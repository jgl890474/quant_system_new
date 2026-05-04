import tushare as ts

# 设置你的 Token
ts.set_token('你的Token')
pro = ts.pro_api()

# 获取澳元兑美元汇率（Tushare 基础积分可调用）
try:
    df = pro.fx_daily(pair='AUDUSD')
    if df is not None and not df.empty:
        print("✅ 澳元兑美元 (AUDUSD) 最新数据：")
        print(df.head())
    else:
        print("⚠️ 数据为空，可能需要更高积分权限")
except Exception as e:
    print(f"❌ 获取失败: {e}")
    print("提示：积分可能不足，或接口名需要调整")

# 你也可以试试获取股票列表作为验证（基础积分可调用）
try:
    df_stock = pro.stock_basic(exchange='', list_status='L')
    print(f"\n✅ Tushare 连接正常，股票总数: {len(df_stock)}")
except Exception as e:
    print(f"❌ 股票接口失败: {e}")