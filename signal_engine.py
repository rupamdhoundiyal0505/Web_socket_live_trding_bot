import pandas as pd
from utils import setup_logger
from option_selector import get_trade_setup
log=setup_logger(__name__)

_active_buy_signal = None
_active_sell_signal = None
_active_buy_trade = None
_active_sell_trade = None

def _create_signal(candle, signal_type: str) -> None:
    return{
        "type": signal_type,
        "timestamp": candle["timestamp"],
        "high": candle["high"],
        "low": candle["low"],
        "close": candle["close"],
        "rsi": candle["rsi"],
        "supertrend_dir": candle["supertrend_dir"],
        "bb_lower": candle["bb_lower"],
        "bb_mid": candle["bb_mid"],
        "bb_upper": candle["bb_upper"],
    }
# implement prev signal validity logic afterwards
def generate_signal(df: pd.DataFrame) -> str:
    global _active_buy_signal, _active_sell_signal, _active_buy_trade, _active_sell_trade


    last = df.iloc[-1]
    if pd.isna(last["bb_upper"]) or pd.isna(last["bb_lower"]):
        log.warning("Indicators not ready yet — returning HOLD")
        return "HOLD"

    rsi      = last["rsi"]
    st_dir   = last["supertrend_dir"]
    close    = last["close"]
    bb_upper = last["bb_upper"]
    bb_mid   = last["bb_mid"]
    bb_lower = last["bb_lower"]
    low = last["low"]
    high = last["high"]

    log.info(
        "Signal checking | close=%.2f RSI=%.1f ST=%d BB=%.2f/%.2f/%.2f",
        close, rsi, st_dir,
        bb_lower, bb_mid, bb_upper,
    )

 
    # trade_setup = None

    #**********
    # WRITE LOGIC HERE BELOW
    #*********
    if bb_lower >= high:
        _active_buy_signal = _create_signal(last, "BUY")
        _active_buy_trade= get_trade_setup("BUY")
        log.info("Signal -> BUY")

    if bb_upper <= low:
        _active_sell_signal = _create_signal(last, "SELL")
        _active_sell_trade = get_trade_setup("SELL")
        log.info("Signal -> SELL")


    
    if _active_buy_signal is not None:
        if close < _active_buy_signal["low"]:
            _active_buy_signal = None
            _active_buy_trade = None

    if _active_sell_signal is not None:
        if close > _active_sell_signal["high"]:
            _active_sell_signal = None
            _active_sell_trade= None


    market_state = {
        "active_buy": _active_buy_signal,
        "active_sell": _active_sell_signal,
        "active_buy_trade": _active_buy_trade,
        "active_sell_trade": _active_sell_trade,
        "market_data": {
            "timestamp": last["timestamp"],
            "close": close,
            "high": high,
            "low": low,
            "rsi": rsi,
            "bb_mid": bb_mid,
        }
    }
    return market_state

    
   




