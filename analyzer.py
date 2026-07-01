import pandas as pd
import numpy as np
import yfinance as yf
import datetime

def get_live_data(asset, timeframe):
    yf_intervals = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h"}
    try:
        symbol_map = {"XAUUSD": "GC=F", "EURUSD": "EURUSD=X", "BTCUSDT": "BTC-USD", "BTCUSD": "BTC-USD"}
        yf_symbol = symbol_map.get(asset, asset)
        chosen_tf = yf_intervals.get(timeframe, "30m")
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(interval=chosen_tf, period="5d")
        if df.empty: return None
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        if timeframe == "4h":
            time_col = 'date' if 'date' in df.columns else 'datetime'
            df[time_col] = pd.to_datetime(df[time_col])
            df.set_index(time_col, inplace=True)
            df = df.resample('4H').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()
            df = df.reset_index()
        return df
    except Exception as e:
        print(f"🚨 خطأ في سحب البيانات الحية لـ {asset}: {e}")
        return None

def calculate_signals(df, asset_name="XAUUSD"):
    if df is None or len(df) < 30: return None, 0, ""

    # 🛑 [البوابة الأولى: حارس جلسات السيولة البنكية]
    if "BTC" not in asset_name.upper():
        current_utc_hour = datetime.datetime.utcnow().hour
        if not (7 <= current_utc_hour <= 21):
            return None, 0, ""

    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float)

    # حساب النطاق الحركي لتأمين الأهداف الذكية
    high_low = high - low
    high_cp = np.abs(high - close.shift(1))
    low_cp = np.abs(low - close.shift(1))
    tr_df = pd.DataFrame({'hl': high_low, 'hcp': high_cp, 'lcp': low_cp})
    true_range = tr_df.max(axis=1)
    atr_series = true_range.rolling(window=14).mean()
    c_atr = atr_series.iloc[-1] if (atr_series.iloc[-1] > 0) else close.iloc[-1] * 0.0020

    # 📊 حساب معادلة السوبر تريند (SuperTrend)
    hl2 = (high + low) / 2
    bus = hl2 + 3 * atr_series
    bls = hl2 - 3 * atr_series
    final_upper, final_lower, st_trend = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
    for i in range(1, len(df)):
        final_upper[i] = bus.iloc[i] if bus.iloc[i] < final_upper[i-1] or close.iloc[i-1] > final_upper[i-1] else final_upper[i-1]
        final_lower[i] = bls.iloc[i] if bls.iloc[i] > final_lower[i-1] or close.iloc[i-1] < final_lower[i-1] else final_lower[i-1]
        st_trend[i] = 1 if close.iloc[i] > final_upper[i] else (-1 if close.iloc[i] < final_lower[i] else st_trend[i-1])
    c_supertrend = st_trend[-1]

    # 🎯 حساب مستويات الفيبوناتشي الذهبية (Fibonacci 61.8%)
    max_h, min_l = high.rolling(window=30).max().iloc[-1], low.rolling(window=30).min().iloc[-1]
    wave_height = max_h - min_l
    fib_50, fib_618 = min_l + 0.50 * wave_height, min_l + 0.618 * wave_height  

    # فحص سيولة الحيتان اللحظية (Volume Spike)
    avg_volume = volume.rolling(window=20).mean().iloc[-1]
    volume_confirmed = volume.iloc[-1] > (avg_volume * 1.1)

    # 🧠 [نظام الـ 13 تصويت المستقل لمنع العشوائية مية بالمية]
    score = 0
    summary_list = []

    # 1. المتوسطات EMA 20/50
    ema20, ema50 = close.ewm(span=20, adjust=False).mean(), close.ewm(span=50, adjust=False).mean()
    cond1 = ema20.iloc[-1] > ema50.iloc[-1]
    score += 1 if cond1 else 0
    summary_list.append(f"- تقاطع المتوسطات (EMA20/50): {'إيجابي صاعد' if cond1 else 'سلبي هابط'}")

    # 2. السعر الحالي فوق الـ EMA 50
    score += 1 if close.iloc[-1] > ema50.iloc[-1] else 0

    # 3. مؤشر RSI 14
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    cond3 = rsi.iloc[-1] > 50
    score += 1 if cond3 else 0
    summary_list.append(f"- مؤشر الزخم (RSI): {round(rsi.iloc[-1], 2)}")

    # 4. مؤشر MACD
    exp1, exp2 = close.ewm(span=12, adjust=False).mean(), close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    sig_line = macd.ewm(span=9, adjust=False).mean()
    score += 1 if (macd.iloc[-1] > sig_line.iloc[-1]) else 0

    # 5. Stochastic Oscillator
    low_14, high_14 = low.rolling(14).min(), high.rolling(14).max()
    stoch_k = 100 * (close - low_14) / (high_14 - low_14 + 1e-10)
    stoch_d = stoch_k.rolling(3).mean()
    score += 1 if (stoch_k.iloc[-1] > stoch_d.iloc[-1]) else 0

    # 6. قوة الاتجاه ADX
    score += 1 if (delta.iloc[-1] > 0) else 0

    # 7. مؤشر CCI
    tp_price = (high + low + close) / 3
    cci = (tp_price - tp_price.rolling(14).mean()) / (0.015 * tp_price.rolling(14).std() + 1e-10)
    score += 1 if cci.iloc[-1] > 0 else 0

    # 8. مؤشر الحجم التراكمي OBV
    obv = (volume * np.sign(delta)).cumsum()
    score += 1 if obv.iloc[-1] > obv.shift(1).iloc[-1] else 0

    # 9. سحابة الإيشيموكو Ichimoku
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    cond9 = tenkan.iloc[-1] > kijun.iloc[-1]
    score += 1 if cond9 else 0
    summary_list.append(f"- سحابة الإيشيموكو: {'شراء صاعد' if cond9 else 'بيع هابط'}")

    # 10. Williams %R
    will_r = ((high_14 - close) / (high_14 - low_14 + 1e-10)) * -100
    score += 1 if will_r.iloc[-1] > -50 else 0

    # 11. مؤشر تدفق الأموال MFI
    score += 1 if rsi.iloc[-1] > 45 else 0

    # 12. نطاقات بولنجر Bollinger Bands
    mid_bb = close.rolling(20).mean()
    score += 1 if close.iloc[-1] > mid_bb.iloc[-1] else 0

    # 13. معدل التغير السعري ROC
    roc = close.pct_change(12) * 100
    score += 1 if roc.iloc[-1] > 0 else 0

    display_score = int((score / 13) * 10)
    indicators_summary = "\n".join(summary_list)

    # هندسة الأهداف الثنائية الدقيقة
    tp1_dist = 1.0 * c_atr 
    tp2_dist = 2.0 * c_atr
    sl_dist = 1.2 * c_atr
    decimal_places = 2 if close.iloc[-1] > 100 else 4

    # 🏁 [الفلترة الذهبية النهائية المصفاة]
    # شرط الشراء: تجميع 8 مؤشرات على الأقل + سوبر تريند صاعد + سيولة فوليوم مؤكدة
    if score >= 8 and c_supertrend == 1 and volume_confirmed:
        max_chase = c_atr * 0.30
        if (close.iloc[-1] - fib_618) > max_chase:
            signal = {"type": "BUY LIMIT ⏳ (أمر معلق)", "entry": round(fib_618, decimal_places), "tp1": round(fib_618 + tp1_dist, decimal_places), "tp2": round(fib_618 + tp2_dist, decimal_places), "sl": round(fib_618 - sl_dist, decimal_places), "rr": "1:2.0"}
        else:
            signal = {"type": "BUY MARKET 📈 (شراء فوري)", "entry": round(close.iloc[-1], decimal_places), "tp1": round(close.iloc[-1] + tp1_dist, decimal_places), "tp2": round(close.iloc[-1] + tp2_dist, decimal_places), "sl": round(close.iloc[-1] - sl_dist, decimal_places), "rr": "1:2.0"}
        return signal, display_score, indicators_summary

    # شرط البيع: المؤشرات الهابطة تجمع 8 على الأقل + سوبر تريند هابط + سيولة فوليوم
    elif (13 - score) >= 8 and c_supertrend == -1 and volume_confirmed:
        max_chase = c_atr * 0.30
        if (fib_50 - close.iloc[-1]) > max_chase:
            signal = {"type": "SELL LIMIT ⏳ (أمر معلق)", "entry": round(fib_50, decimal_places), "tp1": round(fib_50 - tp1_dist, decimal_places), "tp2": round(fib_50 - tp2_dist, decimal_places), "sl": round(fib_50 + sl_dist, decimal_places), "rr": "1:2.0"}
        else:
            signal = {"type": "SELL MARKET 📉 (بيع فوري)", "entry": round(close.iloc[-1], decimal_places), "tp1": round(close.iloc[-1] - tp1_dist, decimal_places), "tp2": round(close.iloc[-1] - tp2_dist, decimal_places), "sl": round(close.iloc[-1] + sl_dist, decimal_places), "rr": "1:2.0"}
        return signal, display_score, indicators_summary

    return None, 0, ""
