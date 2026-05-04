from 数据.market_data import get_1min_kline

result = get_1min_kline("EURUSD")
if result:
    print("✅ 获取成功！")
    print(f"价格: {result['close']}")
else:
    print("❌ 获取失败")