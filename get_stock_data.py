import sys
import json
import os
from datetime import datetime
import requests
import yfinance as yf

TICKER_LIST_FILE = "T.json"
DATA_DIR = "data"
PERIOD = "60d"  # 최근 60일

# TwelveData API 설정 (환경변수명 반영)
TWELVEDATA_API_KEY = os.getenv("TWELVE_API_KEY")
TWELVEDATA_URL = "https://api.twelvedata.com/time_series"

def load_tickers():
    print("[INFO] 티커 목록 불러오는 중...")
    with open(TICKER_LIST_FILE, encoding="utf-8") as f:
        tickers = json.load(f).get("tickers", [])
    print(f"[INFO] 총 {len(tickers)}개 티커.")
    return tickers

def fetch_from_twelvedata(ticker):
    if not TWELVEDATA_API_KEY:
        print("[WARN] TwelveData API KEY 누락. 환경변수 TWELVE_API_KEY 필요.")
        return None
    params = {
        "symbol": ticker,
        "interval": "1day",
        "outputsize": 60,
        "apikey": TWELVEDATA_API_KEY,
        "format": "JSON"
    }
    try:
        resp = requests.get(TWELVEDATA_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "status" in data and data["status"] == "error":
            print(f"[WARN] TwelveData 오류: {data.get('message')}")
            return None
        if "values" not in data:
            print("[ERROR] TwelveData 데이터 형식 오류.")
            return None
        result = {}
        for item in data["values"]:
            # 날짜, 종가, 거래량 등 다양한 정보 저장
            day = item["datetime"]
            result[day] = {
                "close": float(item.get("close", 0)),
                "open": float(item.get("open", 0)),
                "high": float(item.get("high", 0)),
                "low": float(item.get("low", 0)),
                "volume": float(item.get("volume", 0))
            }
        print(f"[SUCCESS] TwelveData로 {ticker} 데이터 {len(result)}건 수집.")
        return result
    except Exception as e:
        print(f"[ERROR] TwelveData 예외: {e}")
        return None

def fetch_from_yfinance(ticker):
    print(f"[INFO] yfinance로 {ticker} 데이터 수집 시도...")
    try:
        df = yf.download(ticker, period=PERIOD)
        if df.empty:
            print("[WARN] yfinance 결과 없음.")
            return None
        result = {}
        for idx, row in df.iterrows():
            date_str = idx.strftime("%Y-%m-%d")
            result[date_str] = {
                "close": float(row.get("Close", 0)),
                "open": float(row.get("Open", 0)),
                "high": float(row.get("High", 0)),
                "low": float(row.get("Low", 0)),
                "volume": float(row.get("Volume", 0))
            }
        print(f"[SUCCESS] yfinance로 {ticker} 데이터 {len(result)}건 수집.")
        return result
    except Exception as e:
        print(f"[ERROR] yfinance 예외: {e}")
        return None

def save_stock_data(ticker, stock_data):
    os.makedirs(DATA_DIR, exist_ok=True)
    data_path = os.path.join(DATA_DIR, f"{ticker}.json")
    # 기존 데이터 불러오기
    if os.path.exists(data_path):
        with open(data_path, encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = {}

    # 기존 데이터와 병합 (덮어쓰기)
    old_data.update(stock_data)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] {data_path} 파일 저장 완료 ({len(old_data)} days)")

def process_ticker(ticker):
    print(f"\n=== {ticker} 데이터 수집 시작 ===")
    stock_data = fetch_from_twelvedata(ticker)
    if not stock_data:
        print(f"[WARN] TwelveData 실패, yfinance 대체 사용")
        stock_data = fetch_from_yfinance(ticker)
    if not stock_data:
        print(f"[FAIL] {ticker}: 어떤 API에서도 데이터 얻지 못함")
        return False
    save_stock_data(ticker, stock_data)
    return True

def main():
    tickers = load_tickers()
    success, fail = 0, 0
    for ticker in tickers:
        if process_ticker(ticker):
            success += 1
        else:
            fail += 1
    print(f"\n[SUMMARY] 성공: {success}, 실패: {fail}")

if __name__ == "__main__":
    main()
