import requests
import urllib3
urllib3.disable_warnings()

url = "https://quote.alltick.co/quote-b-api/kline?token=53afb5f7847560aacd629fe43398f72d-c-app&query=%7B%22trace%22%3A%22test%22%2C%22data%22%3A%7B%22code%22%3A%22EURUSD%22%2C%22kline_type%22%3A1%2C%22query_kline_num%22%3A1%2C%22kline_timestamp_end%22%3A0%7D%7D"

try:
    resp = requests.get(url, timeout=10, verify=False)
    print(f"状态码: {resp.status_code}")
    print(f"返回内容: {resp.text[:200]}")
except Exception as e:
    print(f"错误: {e}")