import sys
import json
import os
from datetime import datetime
import yfinance as yf

TICKER_LIST_FILE = "T.json"
DATA_DIR = "data"
PERIOD = "60d"  # 기본 60일

def load_tickers():
    with open(TICKER_LIST_FILE, encoding="utf-8") as f:
        return json.load(f).get("tickers", [])

def accumulate_stock_data(ticker):
    os.makedirs(DATA_DIR, exist_ok=True)
    data_path = os.path.join(DATA_DIR, f"{ticker}.json")

    # 기존 데이터 불러오기
    if os.path.exists(data_path):
        with open(data_path, encoding="utf-8") as f:
            price_data = json.load(f)
    else:
        price_data = {}

    # yfinance로 데이터 다운로드
    df = yf.download(ticker, period=PERIOD)

    for idx, row in df.iterrows():
        date_str = idx.strftime("%Y-%m-%d")
        price_data[date_str] = {
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        }

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(price_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {data_path} ({len(price_data)} days)")

def main():
    tickers = load_tickers()
    for ticker in tickers:
        accumulate_stock_data(ticker)

if __name__ == "__main__":
    main()
