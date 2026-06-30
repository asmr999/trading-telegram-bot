import pandas as pd
import numpy as np

def get_live_data(asset, timeframe):
    """ دالة جلب البيانات الحية من المنصة الخاصة بك """
    pass

def calculate_signals(df):
    """
    🧠 المخ الفني الخارق - نظام الـ 10 مؤشرات المستقلة (شراء / بيع / انتظار معلق)
    """
    if df is None or len(df) < 60:
        return None, 0

    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    # 1. المتوسطات الأسية EMA
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    
    # 2. مؤشر RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    # 3. مؤشر MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal_line
    
    # 4. Bollinger Bands
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    
    # 5. Stochastic
    low_14 = low.rolling(window=14).min()
    high_14 = high.rolling(window=14).max()
    stoch_k = 100 * ((close - low_14) / (high_14 - low_14 + 1e-10))
    stoch_d = stoch_k.rolling(window=3).mean()

    # حساب نقاط الدعم والمقاومة اللحظية (Pivot Points) لتحديد أوامر الانتظار المعلقة
    pivot = (high.rolling(14).max() + low.rolling(14).min() + close) / 3
    r1 = (2 * pivot) - low.rolling(14).min()
    s1 = (2 * pivot) - high.rolling(14).max()

    c_close = close.iloc[-1]
    c_rsi = rsi.iloc[-1]
    c_macd = macd.iloc[-1]
    c_hist = histogram.iloc[-1]
    c_k = stoch_k.iloc[-1]
    c_d = stoch_d.iloc[-1]
    c_r1 = r1.iloc[-1]
    c_s1 = s1.iloc[-1]

    buy_score = 0
    sell_score = 0

    # فحص توافق المؤشرات الـ 10
    if ema_20.iloc[-1] > ema_50.iloc[-1]: buy_score += 1
    else: sell_score += 1

    if 50 < c_rsi < 70: buy_score += 1
    elif 30 < c_rsi < 50: sell_score += 1

    if c_macd > 0 and c_hist > 0: buy_score += 1
    elif c_macd < 0 and c_hist < 0: sell_score += 1

    if c_close > bb_middle.iloc[-1]: buy_score += 1
    elif c_close < bb_middle.iloc[-1]: sell_score += 1

    if c_k > c_d and c_k < 80: buy_score += 1
    elif c_k < c_d and c_k > 20: sell_score += 1

    # تحديد القرار بناءً على قوة التصويت الفني
    atr = c_close * 0.0035

    # 1. حالة الشراء الفوري القوي
    if buy_score >= 8 and c_close > c_s1:
        signal = {
            "type": "BUY MARKET 📈 (شراء فوري الحين)",
            "entry": round(c_close, 4),
            "tp": round(c_close + atr, 4),
            "sl": round(c_close - atr, 4)
        }
        return signal, buy_score

    # 2. حالة البيع الفوري القوي
    elif sell_score >= 8 and c_close < c_r1:
        signal = {
            "type": "SELL MARKET 📉 (بيع فوري الحين)",
            "entry": round(c_close, 4),
            "tp": round(c_close - atr, 4),
            "sl": round(c_close + atr, 4)
        }
        return signal, sell_score

    # 3. حالة الانتظار والأوامر المعلقة (السوق في منطقة عرضية أو حيرة ارتدادية)
    else:
        # إذا كان الاتجاه يميل للشراء ولكن السعر مرتفع، ننتظر هبوطه للدعم (Buy Limit)
        if buy_score > sell_score:
            signal = {
                "type": "WAIT / PENDING ⏳ (أمر شراء معلق)",
                "entry": round(c_s1, 4), # الدخول من منطقة الدعم الحقيقية
                "tp": round(c_s1 + atr, 4),
                "sl": round(c_s1 - (atr * 0.5), 4)
            }
            return signal, buy_score
        # إذا كان الاتجاه يميل للبيع ولكن السعر منخفض، ننتظر صعوده للمقاومة (Sell Limit)
        else:
            signal = {
                "type": "WAIT / PENDING ⏳ (أمر بيع معلق)",
                "entry": round(c_r1, 4), # الدخول من منطقة المقاومة الحقيقية
                "tp": round(c_r1 - atr, 4),
                "sl": round(c_r1 + (atr * 0.5), 4)
            }
            return signal, sell_score
