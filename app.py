import streamlit as st
import pandas as pd
import requests
from ta.momentum import StochasticOscillator

st.set_page_config(page_title="Stochastic 쓰리바닥 스캐너", layout="wide")
st.title("📉 Stochastic 쓰리바닥 패턴 탐지기 (1시간봉 기준)")

# 파라미터 설정
TIMEFRAME = "1h"
LIMIT = 100
K_PERIOD = 20
K_SMOOTH = 10
D_SMOOTH = 10

# 모든 USDT 마켓 심볼 가져오기
@st.cache_data(show_spinner=False)
def get_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url).json()
    symbols = [s['symbol'] for s in data['symbols'] if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING']
    return symbols

# 심볼별 캔들 데이터 가져오기
@st.cache_data(show_spinner=False)
def get_klines(symbol, interval="1h", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"])
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)
    return df

# 쓰리바닥 패턴 감지
def detect_triple_bottom(df):
    try:
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=K_PERIOD, smooth_window=K_SMOOTH)
        df['%K'] = stoch.stoch()
        df['%D'] = stoch.stoch_signal()

        bottoms = []
        for i in range(2, len(df) - 1):
            if df['%K'].iloc[i-1] > df['%K'].iloc[i] < df['%K'].iloc[i+1]:
                bottoms.append((i, df['%K'].iloc[i]))

        if len(bottoms) < 3:
            return False

        btm3 = bottoms[-3:]
        if btm3[0][1] < btm3[1][1] < btm3[2][1]:
            last_idx = btm3[2][0]
            if df['%K'].iloc[last_idx + 1] > df['%D'].iloc[last_idx + 1]:
                return True
        return False
    except:
        return False

# 앱 실행
st.info("USDT 마켓 전체 코인에서 1시간봉 기준 쓰리바닥 패턴을 탐색 중입니다.")

symbols = get_symbols()
results = []
progress = st.progress(0)

for idx, symbol in enumerate(symbols):
    try:
        df = get_klines(symbol, interval=TIMEFRAME, limit=LIMIT)
        if detect_triple_bottom(df):
            results.append(symbol)
    except:
        continue
    progress.progress((idx + 1) / len(symbols))

progress.empty()

if results:
    st.success(f"총 {len(results)}개의 종목이 쓰리바닥 패턴을 만족합니다!")
    st.dataframe(pd.DataFrame(results, columns=["Symbol"]))
else:
    st.warning("조건을 만족하는 종목이 없습니다.")
