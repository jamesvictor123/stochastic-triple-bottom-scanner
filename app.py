import pandas as pd
import requests
import streamlit as st
from ta.momentum import StochasticOscillator

# 파라미터
TIMEFRAME = "1h"
LIMIT = 100
K_PERIOD = 20
K_SMOOTH = 10
D_SMOOTH = 10

# 종목 리스트
def get_symbols():
    return [  # 여기 네가 넣은 전체 USDT 심볼 리스트 (생략)
       "1000BONKUSDT", "1000FLOKIUSDT", "1000PEPEUSDT", "1000SHIBUSDT", "1INCHUSDT", "AAVEUSDT", "ACHUSDT", "ADAUSDT", "AGIXUSDT", "ALGOUSDT",
        "ALICEUSDT", "ALPHAUSDT", "AMPUSDT", "ANKRUSDT", "ANTUSDT", "APEUSDT", "API3USDT", "APTUSDT", "ARBUSDT", "ARKMUSDT",
        "ARPAUSDT", "ARUSDT", "ASTRUSDT", "ATAUSDT", "ATOMUSDT", "AUDIOUSDT", "AVAXUSDT", "AXSUSDT", "BADGERUSDT", "BAKEUSDT",
        "BALUSDT", "BANDUSDT", "BATUSDT", "BCHUSDT", "BELUSDT", "BLZUSDT", "BNBUSDT", "BNTUSDT", "BONDUSDT", "BSWUSDT",
        "BTCUSDT", "BTTCUSDT", "C98USDT", "CAKEUSDT", "CELOUSDT", "CELRUSDT", "CHZUSDT", "CKBUSDT", "CLVUSDT", "COMPUSDT",
        "COTIUSDT", "CRVUSDT", "CTKUSDT", "CTSIUSDT", "CVCUSDT", "CVXUSDT", "DARUSDT", "DASHUSDT", "DATAUSDT", "DENTUSDT",
        "DGBUSDT", "DIAUSDT", "DOGEUSDT", "DOTUSDT", "DUSKUSDT", "DYDXUSDT", "EGLDUSDT", "ENJUSDT", "ENSUSDT", "EOSUSDT",
        "ETCUSDT", "ETHUSDT", "FETUSDT", "FILUSDT", "FLMUSDT", "FLOWUSDT", "FLUXUSDT", "FOOTBALLUSDT", "FTMUSDT", "FXSUSDT",
        "GALUSDT", "GALAUSDT", "GASUSDT", "GLMRUSDT", "GMTUSDT", "GMXUSDT", "GRTUSDT", "GTCUSDT", "HBARUSDT", "HFTUSDT",
        "HIFIUSDT", "HIGHUSDT", "HOOKUSDT", "HOTUSDT", "ICPUSDT", "ICXUSDT", "IMXUSDT", "INJUSDT", "IOSTUSDT", "IOTAUSDT",
        "IOTXUSDT", "JASMYUSDT", "JOEUSDT", "KAVAUSDT", "KLAYUSDT", "KNCUSDT", "KSMUSDT", "LDOUSDT", "LEVERUSDT", "LINAUSDT",
        "LINKUSDT", "LITUSDT", "LPTUSDT", "LQTYUSDT", "LRCUSDT", "LTCUSDT", "LTOUSDT", "MAGICUSDT", "MANAUSDT", "MASKUSDT",
        "MATICUSDT", "MINAUSDT", "MKRUSDT", "MOVRUSDT", "MTLUSDT", "MULTIUSDT", "NEARUSDT", "NEOUSDT", "NKNUSDT", "NMRUSDT",
        "NULSUSDT", "OCEANUSDT", "OGNUSDT", "OMGUSDT", "ONEUSDT", "ONGUSDT", "ONTUSDT", "OPUSDT", "ORDIUSDT", "OXTUSDT",
        "PENDLEUSDT", "PEOPLEUSDT", "PERLUSDT", "PERPUSDT", "PHAUSDT", "PLAUSDT", "PNTUSDT", "POLYXUSDT", "PORTOUSDT", "POWRUSDT",
        "PROMUSDT", "PYRUSDT", "QKCUSDT", "QNTUSDT", "QTUMUSDT", "RADUSDT", "RAYUSDT", "REEFUSDT", "RENUSDT", "RETHUSDT",
        "RLCUSDT", "RNDRUSDT", "ROSEUSDT", "RSRUSDT", "RUNEUSDT", "RVNUSDT", "SANDUSDT", "SFPUSDT", "SHIBUSDT", "SKLUSDT",
        "SLPUSDT", "SNXUSDT", "SOLUSDT", "SPELLUSDT", "SRMUSDT", "SSVUSDT", "STEEMUSDT", "STGUSDT", "STMXUSDT", "STORJUSDT",
        "STPTUSDT", "STRAXUSDT", "STXUSDT", "SUIUSDT", "SUNUSDT", "SUPERUSDT", "SUSHIUSDT", "SXPUSDT", "THETAUSDT", "TLMUSDT",
        "TOMOUSDT", "TRBUSDT", "TRUUSDT", "TRXUSDT", "TUSDTUSDT", "TVKUSDT", "TWTUSDT", "UMAUSDT", "UNFIUSDT", "UNIUSDT",
        "USDCUSDT", "USTCUSDT", "UTKUSDT", "VETUSDT", "VGXUSDT", "VIBUSDT", "VOXELUSDT", "VTHOUSDT", "WAVESUSDT", "WAXPUSDT",
        "WLDUSDT", "WNXMUSDT", "WOOUSDT", "WRXUSDT", "XEMUSDT", "XLMUSDT", "XMRUSDT", "XNOUSDT", "XRPUSDT", "XTZUSDT",
        "XVSUSDT", "YFIUSDT", "YGGUSDT", "ZECUSDT", "ZENUSDT", "ZILUSDT", "ZRXUSDT"
    ]

# 캔들 데이터
def get_klines(symbol, interval="1h", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)
    return df

# 쓰리바닥 패턴
def detect_triple_bottom(df):
    try:
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'],
                                     window=K_PERIOD, smooth_window=K_SMOOTH)
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

# Streamlit 화면 출력
st.title("📉 Stochastic 쓰리바닥 패턴 탐지기")
st.caption("Binance USDT 마켓 1시간봉 기준, 스토캐스틱(20,10,10) 조건")

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

st.success(f"✅ 쓰리바닥 패턴 포착 종목 수: {len(results)}개")
st.write("🎯 포착 종목 리스트:")
st.write(results)
