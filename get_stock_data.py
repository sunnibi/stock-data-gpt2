import os
import json
import yfinance as yf
from twelvedata import TDClient
from requests.exceptions import RequestException

# GitHub Actions에서는 TWELVE_API_KEY를 Secret으로 등록
TD_API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_data_twelvedata(ticker):
    try:
        td = TDClient(apikey=TD_API_KEY)
        ts = td.time_series(symbol=ticker, interval="1day", outputsize=60)
        data = ts.as_json()["values"]

        return [
            {
                "date": item["datetime"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(float(item["volume"]))
            }
            for item in data
        ]
    except (KeyError, RequestException, ValueError) as e:
        print(f"TwelveData 실패: {e}")
        return None

def fetch_data_yfinance(ticker):
    try:
        df = yf.download(ticker, period="60d")
        return [
            {
                "date": idx.strftime('%Y-%m-%d'),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            }
            for idx, row in df.iterrows()
        ]
    except Exception as e:
        print(f"yfinance 실패: {e}")
        return None

def fetch_stock_data(ticker):
    print(f"🔎 {ticker} 데이터 수집 중...")
    data = fetch_data_twelvedata(ticker)
    if not data:
        print("⚠️ TwelveData 실패 → yfinance 백업으로 전환")
        data = fetch_data_yfinance(ticker)
    return data
