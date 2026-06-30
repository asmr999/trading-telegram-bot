import pandas as pd
import numpy as np
import requests
import yfinance as yf

def get_live_data(asset, timeframe):
    """
    🌐 صنبور البيانات المزدوج فائق الدقة (Binance + Yahoo Finance)
    يجلب الشموع الحية حقيقياً وبدون أي تأخير لتغذية الرادار
    """
    yf_intervals = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h"}
    
    try:
        # 🟢 منصة بايننس (Binance) للعملات الرقمية
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

        # 🟢 منصة ياهو فايننس العالمية للذهب والفوركس
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
    يقوم بالتحليل السوقي الصافي (شراء / بيع / انتظار معلق) بناءً على حركة السعر الحقيقية
    """
    if df is None or len(df) < 50:
        return None, 0

    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    # --- [حساب الـ 10 مؤشرات الفنية داخلياً بالملّي] ---
    
    # 1 & 2: المتوسطات المتحركة الأسية EMA
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    
    # 3 & 4: مؤشر القوة النسبية RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    # 5 & 6: مؤشر الماكد MACD والسيولة
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal_line
    
    # 7 & 8: حدود البولنجر باند Bollinger Bands
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    
    # 9 & 10: مؤشر الاستوكاستك Stochastic ونقاط الدعم اللحظية Pivot
    low_14 = low.rolling(window=14).min()
    high_14 = high.rolling(window=14).max()
    stoch_k = 100 * ((close - low_14) / (high_14 - low_14 + 1e-10))
    stoch_d = stoch_k.rolling(window=3).mean()

    pivot = (high.rolling(14).max() + low.rolling(14).min() + close) / 3
    r1 = (2 * pivot) - low.rolling(14).min()
    s1 = (2 * pivot) - high.rolling(14).max()

    # جلب القيم الحية لآخر شمعة أغلقت الحين
    c_close = close.iloc[-1]
    c_rsi = rsi.iloc[-1]
    c_macd = macd.iloc[-1]
    c_hist = histogram.iloc[-1]
    c_k = stoch_k.iloc[-1]
    c_d = stoch_d.iloc[-1]
    c_r1 = r1.iloc[-1]
    c_s1 = s1.iloc[-1]

    # سيستم التصويت الرقمي الصارم (كل مؤشر يوافق يعطي 1 نقطة حقيقية)
    buy_score = 0
    sell_score = 0

    # 1️⃣ تصويت الاتجاه (EMA):
    if ema_20.iloc[-1] > ema_50.iloc[-1]: buy_score += 1
    else: sell_score += 1
    if c_close > ema_50.iloc[-1]: buy_score += 1
    else: sell_score += 1

    # 2️⃣ تصويت الزخم (RSI):
    if c_rsi > 50: buy_score += 1
    if c_rsi < 70 and c_rsi > 50: buy_score += 1
    if c_rsi < 50: sell_score += 1
    if c_rsi > 30 and c_rsi < 50: sell_score += 1

    # 3️⃣ تصويت السيولة (MACD):
    if c_macd > signal_line: buy_score += 1
    if c_hist > 0: buy_score += 1
    if c_macd < signal_line: sell_score += 1
    if c_hist < 0: sell_score += 1

    # 4️⃣ تصويت الانفجار السعري (Bollinger):
    if c_close > bb_middle.iloc[-1]: buy_score += 1
    else: sell_score += 1

    # 5️⃣ تصويت الانعكاس والارتداد (Stochastic):
    if c_k > c_d: buy_score += 1
    else: sell_score += 1

    # حساب حجم الحركة لضرب الأهداف بدقة
    atr = c_close * 0.0035
    final_score = max(buy_score, sell_score)

    # 📈 اتخاذ القرار بناءً على التحليل السوقي الداخلي البحت (يشترط 8 نقاط فما فوق من الـ 10)
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

    # ⏳ إذا كان السوق متذبذب ولم يحقق الـ 8 نقاط الصارمة، نتحول تلقائياً لأوامر الانتظار المعلقة
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
