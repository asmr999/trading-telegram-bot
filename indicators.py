"""
📐 وحدة حساب المؤشرات الفنية الحقيقية
كل رقم هنا محسوب رياضياً من بيانات Twelve Data الفعلية - لا يوجد أي رقم من اختراع الذكاء الاصطناعي.
"""
import os
import requests

TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

ASSET_MAP = {
    "xau": "XAU/USD", "gold": "XAU/USD",
    "btc": "BTC/USD", "bitcoin": "BTC/USD",
    "eur": "EUR/USD",
}


def _ema_series(values, period):
    """EMA قياسية لكل نقطة بالسلسلة (values[0] هو الأقدم)."""
    k = 2 / (period + 1)
    ema = [values[0]]
    for price in values[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema


def _rsi(values, period=14):
    """RSI بطريقة Wilder القياسية."""
    if len(values) <= period:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _macd(values):
    """MACD line + Signal line + Histogram."""
    ema12 = _ema_series(values, 12)
    ema26 = _ema_series(values, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal_line = _ema_series(macd_line, 9)
    histogram = macd_line[-1] - signal_line[-1]
    return round(macd_line[-1], 4), round(signal_line[-1], 4), round(histogram, 4)


def map_symbol_to_keyword(raw_text):
    """
    يحاول يطابق اسم أداة مقروء من صورة شارت (مثل 'XAUUSD' أو 'Gold Spot')
    مع مفتاح معروف عندنا بجدول ASSET_MAP. يرجع None لو ما قدر يتأكد،
    عشان ما نربط تحليل بأداة غلط.
    """
    if not raw_text:
        return None
    t = raw_text.upper().replace(" ", "").replace("/", "").replace("-", "")
    if "XAU" in t or "GOLD" in t:
        return "xau"
    if "BTC" in t or "BITCOIN" in t:
        return "btc"
    if "EUR" in t and "USD" in t:
        return "eur"
    return None


def fetch_and_compute(asset_keyword="xau"):
    """
    يرجع (indicators_dict, error_message).
    indicators_dict يحتوي كل الأرقام المحسوبة فعلياً + درجة توافق نهائية.
    """
    if not TWELVE_DATA_API_KEY:
        return None, "❌ مفتاح TWELVE_DATA_API_KEY غير مفعل."

    symbol = ASSET_MAP.get(asset_keyword.lower().strip(), "XAU/USD")

    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&apikey={TWELVE_DATA_API_KEY}&outputsize=60"
        res = requests.get(url, timeout=10).json()
        if "values" not in res:
            return None, f"❌ فشل جلب البيانات: {res.get('message', 'رد غير معروف')}"

        # القيم ترجع من الأحدث للأقدم عند Twelve Data - نعكسها عشان تصير من الأقدم للأحدث
        closes = [float(c["close"]) for c in reversed(res["values"])]
        current_price = closes[-1]

        rsi_val = _rsi(closes, 14)
        ema9 = _ema_series(closes, 9)[-1]
        ema21 = _ema_series(closes, 21)[-1]
        macd_line, signal_line, histogram = _macd(closes)

        # --- إشارات الاتجاه من كل مؤشر على حدة ---
        signals = []
        signals.append("BUY" if ema9 > ema21 else "SELL")
        signals.append("BUY" if macd_line > signal_line else "SELL")
        if rsi_val is not None:
            if rsi_val > 55:
                signals.append("BUY")
            elif rsi_val < 45:
                signals.append("SELL")
            else:
                signals.append("NEUTRAL")

        buy_votes = signals.count("BUY")
        sell_votes = signals.count("SELL")
        total = len([s for s in signals if s != "NEUTRAL"]) or 1

        if buy_votes > sell_votes:
            direction = "BUY"
            agreement = buy_votes / total
        elif sell_votes > buy_votes:
            direction = "SELL"
            agreement = sell_votes / total
        else:
            direction = "WAIT"
            agreement = 0.5

        # درجة توافق فني (مو "احتمال ربح") محصورة بين 40 و85 عشان ما توحي بضمان أبداً
        alignment_score = round(40 + agreement * 45, 1)

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "rsi": rsi_val,
            "ema9": round(ema9, 2),
            "ema21": round(ema21, 2),
            "macd_line": macd_line,
            "macd_signal": signal_line,
            "macd_histogram": histogram,
            "direction": direction,
            "alignment_score": alignment_score,
        }, None

    except Exception as e:
        return None, f"❌ خطأ أثناء الحساب: {str(e)}"


def format_indicators_for_ai(data):
    """يحول الأرقام المحسوبة لنص واضح يُعطى للذكاء الاصطناعي كمرجع - بدون أي مساحة للاختراع."""
    return (
        f"الأداة: {data['symbol']}\n"
        f"السعر الحالي: {data['current_price']}\n"
        f"RSI(14): {data['rsi']}\n"
        f"EMA9: {data['ema9']} | EMA21: {data['ema21']} ({'EMA9 فوق EMA21' if data['ema9'] > data['ema21'] else 'EMA9 تحت EMA21'})\n"
        f"MACD Line: {data['macd_line']} | Signal Line: {data['macd_signal']} | Histogram: {data['macd_histogram']}\n"
        f"الاتجاه المحسوب من توافق المؤشرات: {data['direction']}\n"
        f"درجة التوافق الفني المحسوبة رياضياً (وليست احتمال ربح): {data['alignment_score']}%"
    )
