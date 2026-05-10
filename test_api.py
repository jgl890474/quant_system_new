import yfinance as yf
import requests

print("测试 yfinance...")
data = yf.Ticker("AAPL").history(period="1d")
if not data.empty:
    print(f"AAPL 真实价格: ${data['Close'].iloc[-1]}")
else:
    print("yfinance 失败")

print("测试币安 API...")
try:
    r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
    price = r.json()['price']
    print(f"BTC 真实价格: ${price}")
except Exception as e:
    print(f"币安 API 失败: {e}")
