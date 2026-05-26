import pandas as pd
from utils import setup_logger
log=setup_logger(__name__)

# implement prev signal validity logic afterwards
def generate_signal(df: pd.DataFrame) -> str:
    last = df.iloc[-1]
    if pd.isna(last["bb_upper"]):
        log.warning("Indicators not ready yet — returning HOLD")
        return "HOLD"

    rsi      = last["rsi"]
    st_dir   = last["supertrend_dir"]
    close    = last["close"]
    bb_upper = last["bb_upper"]
    bb_mid   = last["bb_mid"]
    bb_lower = last["bb_lower"]
    low = last["close"]
    high = last["high"]

    log.info(
        "Signal checking | close=%.2f RSI=%.1f ST=%d BB=%.2f/%.2f/%.2f",
        close, rsi, st_dir,
        bb_lower, bb_mid, bb_upper,
    )

    buy = (
        
    )
    sell = (
        
    )
    if buy:
        log.info("Signal -> BUY")
        return "BUY"
    if sell:
        log.info("Signal -> SELL")
        return "SELL"
    
    log.info("latest added is not a signal candle")
    return "HOLD"




