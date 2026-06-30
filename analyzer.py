import pandas as pd
import numpy as np
import requests
import yfinance as yf

def get_live_data(asset, timeframe):
    """
    🌐 صنبور البيانات المزدوج فائق الدقة (Binance + Yahoo Finance)
    """
    yf_intervals = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h"}
    
    try:
        if asset == "BTCUSDT":
            binance_intervals = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "4h"}
            chosen_tf = binance_intervals.get(timeframe, "30m")
            url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={chosen_tf}&limit=100"
            response = requests.get(url, timeout=10).json()
            
            df = pd.DataFrame(response, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume', 
                'close_time', 'q_av', 'num_trades', 'taker_base', 'taker_quote', 'ignore'
            ])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            return df
        else:
            symbol_map = {"XAUUSD": "GC=F", "EURUSD": "EURUSD=X"}
            yf_symbol = symbol_map.get(asset, asset)
            chosen_tf = yf_intervals.get(timeframe, "30m")
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(interval=chosen_tf, period="5d")
            
            if df.empty:
                return None
                
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            
            if timeframe == "4h":
                time_col = 'date' if 'date' in df.columns else 'datetime'
                df[time_col] = pd.to_datetime(df[time_col])
                df.set_index(time_col, inplace=True)
                df = df.resample('4H').agg({
                    'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
                }).dropna()
                df = df.reset_index()
            return df
    except Exception as e:
        print(f"🚨 خطأ في سحب البيانات الحية: {e}")
        return None

def calculate_signals(df):
    """
    🧠 المخ الفني المستقل - نظام الـ 10 مؤشرات الرقمية المحسوبة داخلياً بالكامل
    """
    if df is None or len(df) < 50:
        return None, 0

    close = df['close']
    high = df['high']
    low = df['low']
    
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal_line
    
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    
    low_14 = low.rolling(window=14).min()
    high_14 = high.rolling(window=14).max()
    stoch_k = 100 * ((close - low_14) / (high_14 - low_14 + 1e-10))
    stoch_d = stoch_k.rolling(window=3).mean()

    pivot = (high.rolling(14).max() + low.rolling(14).min() + close) / 3
    r1 = (2 * pivot) - low.rolling(14).min()
    s1 = (2 * pivot) - high.rolling(14).max()

    c_close = close.iloc[-1]
    c_rsi = rsi.iloc[-1]
    c_macd = macd.iloc[-1]
    c_signal = signal_line.iloc[-1]
    c_hist = histogram.iloc[-1]
    c_k = stoch_k.iloc[-1]
    c_d = stoch_d.iloc[-1]
    c_r1 = r1.iloc[-1]
    c_s1 = s1.iloc[-1]
    c_ema20 = ema_20.iloc[-1]
    c_ema50 = ema_50.iloc[-1]
    c_bb_middle = bb_middle.iloc[-1]

    buy_score = 0
    sell_score = 0

    if c_ema20 > c_ema50: buy_score += 1
    else: sell_score += 1
    if c_close > c_ema50: buy_score += 1
    else: sell_score += 1

    if c_rsi > 50: buy_score += 1
    if 50 < c_rsi < 70: buy_score += 1
    if c_rsi < 50: sell_score += 1
    if 30 < c_rsi < 50: sell_score += 1

    if c_macd > c_signal: buy_score += 1
    if c_hist > 0: buy_score += 1
    if c_macd < c_signal: sell_score += 1
    if c_hist < 0: sell_score += 1

    if c_close > c_bb_middle: buy_score += 1
    else: sell_score += 1

    if c_k > c_d: buy_score += 1
    else: sell_score += 1

    atr = c_close * 0.0035
    final_score = max(buy_score, sell_score)

    if buy_score >= 8 and c_close > c_s1:
        signal = {
            "type": "BUY MARKET 📈 (شراء فوري)",
            "entry": round(c_close, 2 if c_close > 100 else 4),
            "tp": round(c_close + atr, 2 if c_close > 100 else 4),
            "sl": round(c_close - atr, 2 if c_close > 100 else 4)
        }
        return signal, final_score
    elif sell_score >= 8 and c_close < c_r1:
        signal = {
            "type": "SELL MARKET 📉 (بيع فوري)",
            "entry": round(c_close, 2 if c_close > 100 else 4),
            "tp": round(c_close - atr, 2 if c_close > 100 else 4),
            "sl": round(c_close + atr, 2 if c_close > 100 else 4)
        }
        return signal, final_score
    else:
        if buy_score > sell_score:
            signal = {
                "type": "WAIT / PENDING ⏳ (أمر شراء معلق)",
                "entry": round(c_s1, 2 if c_close > 100 else 4),
                "tp": round(c_s1 + atr, 2 if c_close > 100 else 4),
                "sl": round(c_s1 - (atr * 0.5), 2 if c_close > 100 else 4)
            }
            return signal, final_score
        else:
            signal = {
                "type": "WAIT / PENDING ⏳ (أمر بيع معلق)",
                "entry": round(c_r1, 2 if c_close > 100 else 4),
                "tp": round(c_r1 - atr, 2 if c_close > 100 else 4),
                "sl": round(c_r1 + (atr * 0.5), 2 if c_close > 100 else 4)
            }
            return signal, final_score
