import pandas as pd
import numpy as np
import yfinance as yf
import datetime

def get_live_data(asset, timeframe):
    """
    🌐 صنبور البيانات العالمي الموحد المفتوح (Yahoo Finance)
    سحب الشموع الحية بأعلى دقة وبدون أي حظر جيو-سحابي
    """
    yf_intervals = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h"}
    
    try:
        symbol_map = {
            "XAUUSD": "GC=F", 
            "EURUSD": "EURUSD=X",
            "BTCUSDT": "BTC-USD",
            "BTCUSD": "BTC-USD"
        }
        
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
        print(f"🚨 خطأ في سحب البيانات الحية لـ {asset}: {e}")
        return None

def calculate_signals(df, asset_name="XAUUSD"):
    """
    🧠 رادار القناص المؤسسي (Ultra-Precision Sniper Radar)
    مدمج فيه: 10 مؤشرات فنية + فلاتر السوبر تريند + الفيبوناتشي الذهبي + فلتر الجلسات الصارم لقطع العشوائية مية بالمية
    """
    if df is None or len(df) < 30:
        return None, 0

    # 🛑 [البوابة الأولى: فلتر جلسات السيولة الحوتية الصارم]
    if "BTC" not in asset_name.upper():
        current_utc_hour = datetime.datetime.utcnow().hour
        # السماح فقط بفترة نشاط بورصات لندن ونيويورك (من 07:00 صباحاً إلى 21:00 مساءً بتوقيت UTC)
        if not (7 <= current_utc_hour <= 21):
            print(f"🛡️ تم حظر فحص {asset_name} تلقائياً: السوق حالياً في منطقة الساعات الميتة وضعف السيولة البنكية.")
            return None, 0

    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float)

    # 1️⃣ حساب الـ ATR ومعدل حركية السوق الواقعية لتأمين الأهداف
    high_low = high - low
    high_cp = np.abs(high - close.shift(1))
    low_cp = np.abs(low - close.shift(1))
    tr_df = pd.DataFrame({'hl': high_low, 'hcp': high_cp, 'lcp': low_cp})
    true_range = tr_df.max(axis=1)
    atr_series = true_range.rolling(window=14).mean()
    c_atr = atr_series.iloc[-1]
    
    if np.isnan(c_atr) or c_atr <= 0:
        c_atr = close.iloc[-1] * 0.0020 

    # 2️⃣ [البوابة الثانية: معادلة السوبر تريند المؤسسية الذكية]
    hl2 = (high + low) / 2
    bus = hl2 + 3 * atr_series
    bls = hl2 - 3 * atr_series
    final_upper = np.zeros(len(df))
    final_lower = np.zeros(len(df))
    st_trend = np.zeros(len(df))
    
    for i in range(1, len(df)):
        final_upper[i] = bus.iloc[i] if bus.iloc[i] < final_upper[i-1] or close.iloc[i-1] > final_upper[i-1] else final_upper[i-1]
        final_lower[i] = bls.iloc[i] if bls.iloc[i] > final_lower[i-1] or close.iloc[i-1] < final_lower[i-1] else final_lower[i-1]
        st_trend[i] = 1 if close.iloc[i] > final_upper[i] else (-1 if close.iloc[i] < final_lower[i] else st_trend[i-1])
    
    c_supertrend = st_trend[-1]

    # 3️⃣ [البوابة الثالثة: مستويات الفيبوناتشي الديناميكية لآخر موجة سعرك]
    max_h = high.rolling(window=30).max().iloc[-1]
    min_l = low.rolling(window=30).min().iloc[-1]
    wave_height = max_h - min_l
    fib_50 = min_l + 0.50 * wave_height    
    fib_618 = min_l + 0.618 * wave_height  

    # 4️⃣ فحص سيولة الحيتان الكاشفة (Volume Spike)
    avg_volume = volume.rolling(window=20).mean().iloc[-1]
    c_volume = volume.iloc[-1]
    volume_confirmed = c_volume > (avg_volume * 1.1)

    # 5️⃣ تشغيل الـ 10 مؤشرات الفنية الكلاسيكية للزخم والترند
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

    c_close = close.iloc[-1]
    buy_score = 0
    sell_score = 0

    if ema_20.iloc[-1] > ema_50.iloc[-1]: buy_score += 1
    else: sell_score += 1
    if c_close > ema_50.iloc[-1]: buy_score += 1
    else: sell_score += 1
    if rsi.iloc[-1] > 50: buy_score += 1
    else: sell_score += 1
    if macd.iloc[-1] > signal_line.iloc[-1]: buy_score += 1
    else: sell_score += 1

    final_score = max(buy_score, sell_score)
    display_score = int((final_score / 4) * 10)

    short_target_dist = 1.0 * c_atr 
    stop_loss_dist = 1.0 * c_atr
    decimal_places = 2 if c_close > 100 else 4

    # 6️⃣ الفلترة النهائية القاطعة للعشوائية (التطابق الكامل والشامل)
    if buy_score >= 3 and c_supertrend == 1 and volume_confirmed:
        max_chase = c_atr * 0.30
        if (c_close - fib_618) > max_chase:
            signal = {
                "type": "BUY LIMIT ⏳ (أمر شراء معلق مسبق)",
                "entry": round(fib_618, decimal_places), 
                "tp": round(fib_618 + short_target_dist, decimal_places), 
                "sl": round(fib_618 - stop_loss_dist, decimal_places)
            }
        else:
            signal = {
                "type": "BUY MARKET 📈 (شراء فوري عاجل)",
                "entry": round(c_close, decimal_places),
                "tp": round(c_close + short_target_dist, decimal_places),
                "sl": round(c_close - stop_loss_dist, decimal_places)
            }
        return signal, display_score

    elif sell_score >= 3 and c_supertrend == -1 and volume_confirmed:
        max_chase = c_atr * 0.30
        if (fib_50 - c_close) > max_chase:
            signal = {
                "type": "SELL LIMIT ⏳ (أمر بيع معلق مسبق)",
                "entry": round(fib_50, decimal_places), 
                "tp": round(fib_50 - short_target_dist, decimal_places),
                "sl": round(fib_50 + stop_loss_dist, decimal_places)
            }
        else:
            signal = {
                "type": "SELL MARKET 📉 (بيع فوري عاجل)",
                "entry": round(c_close, decimal_places),
                "tp": round(c_close - short_target_dist, decimal_places),
                "sl": round(c_close + stop_loss_dist, decimal_places)
            }
        return signal, display_score

    return None, 0
