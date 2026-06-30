import numpy as np
import pandas as pd

try:
    # تعريف المتغيرات الأساسية لحساب المؤشرات بأمان
    high = df['high']
    low = df['low']
    
    tp = (df['low'] + df['close']) / 3
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    cci = (tp - tp.rolling(window=20).mean()) / (0.015 * mad + 1e-9)
    if (is_uptrend and cci.iloc[-1] > 50) or (not is_uptrend and cci.iloc[-1] < -50): score += 1

    # 9. MFI 14
    tpd = tp.diff()
    rmf = tp * df['volume']
    pmf = rmf.where(tpd > 0, 0).rolling(window=14).sum()
    nmf = rmf.where(tpd < 0, 0).rolling(window=14).sum()
    mfi = 100 - (100 / (1 + (pmf / (nmf + 1e-9))))
    if (is_uptrend and mfi.iloc[-1] < 50) or (not is_uptrend and mfi.iloc[-1] > 50): score += 1

    # 10. Parabolic SAR
    psar = [0.0] * len(df)
    bull, af, ep, psar[0] = True, 0.02, high[0], low[0]
    for i in range(1, len(df)):
        psar[i] = psar[i-1] + af * (ep - psar[i-1])
        if bull:
            if low[i] < psar[i]: 
                bull, psar[i], ep, af = False, ep, low[i], 0.02
            else:
                if high[i] > ep: ep, af = high[i], min(af + 0.02, 0.2)
                psar[i] = min(psar[i], high[i-1], high[i-2] if i > 1 else high[i-1])
        else:
            if high[i] > psar[i]: 
                bull, psar[i], ep, af = True, ep, high[i], 0.02
            else:
                if low[i] < ep: ep, af = low[i], min(af + 0.02, 0.2)
                psar[i] = max(psar[i], low[i-1], low[i-2] if i > 1 else low[i-1])

except Exception as e:
    print(f"Error in analyzer: {e}")
