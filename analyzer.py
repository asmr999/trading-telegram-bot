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
        if asset == "BTCUSDT" or asset == "BTCUSD":
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
    🧠 المخ الفني المطوّر - نظام مؤشرات رياضي صلب مبني على الـ ATR الحقيقي والـ Pivot الثابت
    """
    if df is None or len(df) < 30:
        return None, 0

    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)

    # 1️⃣ حساب مؤشر الـ ATR الحقيقي لقياس Volatility السوق بدقة متناهية
    high_low = high - low
    high_cp = np.abs(high - close.shift(1))
    low_cp = np.abs(low - close.shift(1))
    tr_df = pd.DataFrame({'hl': high_low, 'hcp': high_cp, 'lcp': low_cp})
    true_range = tr_df.max(axis=1)
    atr_series = true_range.rolling(window=14).mean()
    
    c_atr = atr_series.iloc[-1]
    if np.isnan(c_atr) or c_atr <= 0:
        c_atr = close.iloc[-1] * 0.0025 # صمام أمان احتياطي

    # 2️⃣ حساب نقاط الدعم والمقاومة الكلاسيكية بناءً على الشمعة السابقة المنتهية (ثابتة وموثوقة)
    prev_high = high.iloc[-2]
    prev_low = low.iloc[-2]
    prev_close = close.iloc[-2]

    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = (2 * pivot) - prev_low
    s1 = (2 * pivot) - prev_high

    # الأسعار الحالية اللحظية
    c_close = close.iloc[-1]

    # 3️⃣ استخراج قراءات الاتجاه والزخم والسيولة
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

    c_ema20 = ema_20.iloc[-1]
    c_ema50 = ema_50.iloc[-1]
    c_rsi = rsi.iloc[-1]
    c_macd = macd.iloc[-1]
    c_signal = signal_line.iloc[-1]

    # سيستم التصويت الرقمي
    buy_score = 0
    sell_score = 0

    if c_ema20 > c_ema50: buy_score += 1
    else: sell_score += 1
    if c_close > c_ema50: buy_score += 1
    else: sell_score += 1
    if c_rsi > 50: buy_score += 1
    else: sell_score += 1
    if c_macd > c_signal: buy_score += 1
    else: sell_score += 1

    final_score = max(buy_score, sell_score)
    display_score = int((final_score / 4) * 10) # تحويل لنسبة مئوية من 10 لتظهر فخمة للمستخدم

    # 4️⃣ بناء استراتيجية القناص الاحترافية (إدارة صفقات حقيقية)
    if buy_score >= 3:
        if c_close > r1:
            signal = {
                "type": "BUY MARKET 📈 (شراء فوري)",
                "entry": round(c_close, 2 if c_close > 100 else 4),
                "tp": round(c_close + (2 * c_atr), 2 if c_close > 100 else 4), # إدارة أرباح ضعف المخاطرة 1:2
                "sl": round(c_close - c_atr, 2 if c_close > 100 else 4)
            }
        else:
            signal = {
                "type": "BUY LIMIT ⏳ (أمر شراء معلق)",
                "entry": round(s1, 2 if c_close > 100 else 4),
                "tp": round(s1 + (2 * c_atr), 2 if c_close > 100 else 4),
                "sl": round(s1 - c_atr, 2 if c_close > 100 else 4)
            }
        return signal, display_score

    else:
        if c_close < s1:
            signal = {
                "type": "SELL MARKET 📉 (بيع فوري)",
                "entry": round(c_close, 2 if c_close > 100 else 4),
                "tp": round(c_close - (2 * c_atr), 2 if c_close > 100 else 4),
                "sl": round(c_close + c_atr, 2 if c_close > 100 else 4)
            }
        else:
            signal = {
                "type": "SELL LIMIT ⏳ (أمر بيع معلق)",
                "entry": round(r1, 2 if c_close > 100 else 4),
                "tp": round(r1 - (2 * c_atr), 2 if c_close > 100 else 4),
                "sl": round(r1 + c_atr, 2 if c_close > 100 else 4)
            }
        return signal, display_score
