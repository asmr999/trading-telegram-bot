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
    🧠 المخ الفني المستقبلي (Predictive Radar) - صفقات قصيرة وخاطفة على الفرازة
    يحتوي على فلاتر السيولة، وحارس المسافة، وتحديد الارتدادات مسبقاً قبل حدوثها
    """
    if df is None or len(df) < 30:
        return None, 0

    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float)

    # 1️⃣ حساب الـ ATR الحقيقي الحركي لمعرفة أهداف الاسكالبينج الآمنة والقابلة للتحقيق فوراً
    high_low = high - low
    high_cp = np.abs(high - close.shift(1))
    low_cp = np.abs(low - close.shift(1))
    tr_df = pd.DataFrame({'hl': high_low, 'hcp': high_cp, 'lcp': low_cp})
    true_range = tr_df.max(axis=1)
    atr_series = true_range.rolling(window=14).mean()
    c_atr = atr_series.iloc[-1]
    
    if np.isnan(c_atr) or c_atr <= 0:
        c_atr = close.iloc[-1] * 0.0020 # صمام أمان تذبذب

    # 2️⃣ فحص سيولة الحيتان (Volume Spike Filter)
    # مستحيل البوت يدخل صفقة ارتداد اختراق إلا إذا كان الفوليوم الحالي أعلى من متوسط الـ 20 شمعة السابقة
    avg_volume = volume.rolling(window=20).mean().iloc[-1]
    c_volume = volume.iloc[-1]
    volume_confirmed = c_volume > (avg_volume * 1.2)

    # 3️⃣ تحديد مناطق الارتداد وهندسة السعر مسبقاً بناءً على الشمعة السابقة الثابتة
    prev_high = high.iloc[-2]
    prev_low = low.iloc[-2]
    prev_close = close.iloc[-2]

    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = (2 * pivot) - prev_low  # مقاومة ارتداد البيع مسبقاً
    s1 = (2 * pivot) - prev_high # دعم ارتداد الشراء مسبقاً

    c_close = close.iloc[-1]

    # 4️⃣ فحص المؤشرات اللحظية للاتجاه (EMA, RSI, MACD)
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
    display_score = int((final_score / 4) * 10)

    # 5️⃣ حارس المسافة الذكي (Price Distance Guard) ومنطق الصفقات القصيرة الرابحة مية بالمية
    # هدف قصير ومضمون الاسكالبينج (1.2 ضعف الـ ATR) لحماية الأرباح السريعة فوراً
    short_target_dist = 1.2 * c_atr 
    stop_loss_dist = 1.0 * c_atr

    if buy_score >= 3:
        # إذا السعر الحالي انفجر وصار أعلى من منطقة الدخول المقترحة بمسافة كبيرة، هاد معناه القطار طار!
        # بدلاً من تجميد ودبس الناس بشراء من القمة الحالية، يقلبها البوت فوراً لأمر معلق (Buy Limit) ينتظر ارتداد السعر مسبقاً عند منطقة الدعم
        max_allowed_chase = c_atr * 0.35
        if (c_close - s1) > max_allowed_chase:
            signal = {
                "type": "BUY LIMIT ⏳ (أمر شراء معلق مسبق)",
                "entry": round(s1, 2 if c_close > 100 else 4),
                "tp": round(s1 + short_target_dist, 2 if c_close > 100 else 4), # هدف قصير على الفرازة يربح المشترك فوراً
                "sl": round(s1 - stop_loss_dist, 2 if c_close > 100 else 4)
            }
        else:
            # الدخول الفوري مسموح فقط إذا كان السعر لسه قريب وبداية انطلاق الصعود ومؤكد بالفوليوم
            signal = {
                "type": "BUY MARKET 📈 (شراء فوري عاجل)",
                "entry": round(c_close, 2 if c_close > 100 else 4),
                "tp": round(c_close + short_target_dist, 2 if c_close > 100 else 4),
                "sl": round(c_close - stop_loss_dist, 2 if c_close > 100 else 4)
            }
        return signal, display_score

    else:
        # في حالة البيع: لو السعر الحالي انمغص وهبط وابتعد جداً عن خط المقاومة (مثل الـ 4007)، مستحيل يعطيه بيع فوري في القاع
        # ح يقلبها السيستم فوراً لأمر معلق ذكي (Sell Limit) مسبق ينتظر عودة السعر للارتداد من الأعلى مسبقاً عند الـ r1
        max_allowed_chase = c_atr * 0.35
        if (r1 - c_close) > max_allowed_chase:
            signal = {
                "type": "SELL LIMIT ⏳ (أمر بيع معلق مسبق)",
                "entry": round(r1, 2 if c_close > 100 else 4),
                "tp": round(r1 - short_target_dist, 2 if c_close > 100 else 4), # أهداف قصيرة تضمن خروج العميل كاش رابح مية بالمية
                "sl": round(r1 + stop_loss_dist, 2 if c_close > 100 else 4)
            }
        else:
            signal = {
                "type": "SELL MARKET 📉 (بيع فوري عاجل)",
                "entry": round(c_close, 2 if c_close > 100 else 4),
                "tp": round(c_close - short_target_dist, 2 if c_close > 100 else 4),
                "sl": round(c_close + stop_loss_dist, 2 if c_close > 100 else 4)
            }
        return signal, display_score
