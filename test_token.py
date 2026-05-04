import requests
import urllib3
urllib3.disable_warnings()

# 关键修改：把原来的 EURUSD 换成 DEMO_EURUSD
# 演示产品代码请从Dashboard查看
symbol = "DEMO_EURUSD"   # ✅ 免费账号可用的演示产品

# 其他参数保持不变
query_data = {
    "trace": "quant_test",
    "data": {
        "code": symbol,
        "kline_type": 1,
        "query_kline_num": 5,
        "kline_timestamp_end": 0
    }
}

import json, urllib.parse
query_str = urllib.parse.quote(json.dumps(query_data))
url = f"https://quote.alltick.co/quote-b-api/kline?token=7673d2198462d2db0d84acb3bd486d02-c-app&query={query_str}"

print(f"正在请求产品: {symbol}")
resp = requests.get(url, timeout=10, verify=False)
print(f"状态码: {resp.status_code}")
print(f"返回内容: {resp.text}")