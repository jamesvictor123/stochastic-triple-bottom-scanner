import streamlit as st
import pandas as pd
import requests
import time
from ta.momentum import StochasticOscillator

# ---------------------- 파라미터 설정 ---------------------- #
TIMEFRAME = "1h"
LIMIT = 100
K_PERIOD = 20
K_SMOOTH = 10
D_SMOOTH = 10
REFRESH_INTERVAL = 900  # 900초 = 15분

# ---------------------- 심볼 목록 ---------------------- #
def get_symbols():
    return ["BTCUSDT", "ETHUSDT", "AVAXUSDT", "SOLUSDT", "DOGEUSDT", "SUIUSDT", "1000FLOKIUSDT", "1000PEPEUSDT"]  # 예시 일부

# ---------------------- 캔들 데이터 가져오기 ---------------------- #
def get_klines(symbol, interval="1h", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume",
                                     "close_time", "quote_asset_volume", "number_of_trades",
                                     "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"])
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)
    return df

# ---------------------- 쓰리바닥 패턴 탐지 ---------------------- #
def detect_triple_bottom(df):
    try:
        stoch = StochasticOscillator(
            high=df['high'], low=df['low'], close=df['close'],
            window=K_PERIOD, smooth_window=K_SMOOTH
        )
        df['%K'] = stoch.stoch()
        df['%D'] = stoch.stoch_signal()

        bottoms = []
        for i in range(1, len(df) - 1):
            if df['%K'].iloc[i-1] > df['%K'].iloc[i] < df['%K'].iloc[i+1]:
                bottoms.append((i, df['%K'].iloc[i]))

        if len(bottoms) < 3:
            return False

        btm3 = bottoms[-3:]
        k1, k2, k3 = btm3[0][1], btm3[1][1], btm3[2][1]
        if not (k1 < k2 < k3):
            return False

        last_idx = btm3[2][0]
        for offset in range(1, 4):
            idx = last_idx + offset
            if idx < len(df):
                if df['%K'].iloc[idx] > df['%D'].iloc[idx]:
                    return True

        return False
    except:
        return False

# ---------------------- Streamlit 앱 본문 ---------------------- #
def main():
    st.set_page_config(page_title="Stochastic 쓰리바닥 패턴", layout="wide")
    st.title("📉 Stochastic 쓰리바닥 패턴 탐지기")
    st.caption("Binance USDT 마켓 1시간봉 기준, 스토캐스틱(20,10,10) 조건")

    results = []
    symbols = get_symbols()
    progress_bar = st.progress(0)

    for i, symbol in enumerate(symbols):
        try:
            df = get_klines(symbol, interval=TIMEFRAME, limit=LIMIT)
            if detect_triple_bottom(df):
                results.append(symbol)
        except:
            continue
        progress_bar.progress((i + 1) / len(symbols))

    st.success(f"✅ 쓰리바닥 패턴 포착 종목 수: {len(results)}")
    st.write("🎯 포함 종목 리스트:", results)

    st.info(f"⏳ {REFRESH_INTERVAL}초 후 자동 새로고침됩니다.")
    time.sleep(REFRESH_INTERVAL)
    st.experimental_rerun()

if __name__ == '__main__':
    main()
