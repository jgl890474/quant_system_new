import yinhedata as yh
import akshare as ak

print("=== 银禾数据 + AkShare 测试 ===\n")

# 方法1：通过银禾数据获取期货行情（测试）
print("1. 测试期货行情...")
try:
    futures = yh.futures_hq_jr()
    print(f"期货数据: {futures.head() if hasattr(futures, 'head') else futures}")
except Exception as e:
    print(f"期货接口错误: {e}")

# 方法2：直接使用 AkShare 获取外汇数据
print("\n2. 通过 AkShare 获取外汇数据...")
try:
    # 外汇实时汇率
    forex = ak.currency_boc_sina(symbol="美元")
    print(f"美元汇率数据: {forex}")
except Exception as e:
    print(f"外汇接口错误: {e}")

# 方法3：获取加密货币数据（通过 AkShare）
print("\n3. 通过 AkShare 获取加密货币数据...")
try:
    # 比特币实时行情
    btc = ak.crypto_js_spot(symbol="BTC")
    print(f"BTC 数据: {btc}")
except Exception as e:
    print(f"加密货币接口错误: {e}")