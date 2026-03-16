import pandas as pd
import pandas_ta as ta
from config import BB_LENGTH, BB_STD, RSI_LENGTH, ST_LENGTH, ST_MULTIPLIER
from utils import setup_logger

log = setup_logger(__name__)
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    min_candles = max(BB_LENGTH, RSI_LENGTH, ST_LENGTH)
    if len(df) < min_candles:
        log.warning(
            "Not enough candles | have=%d | need=%d | skipping indicators",
            len(df), min_candles
        )
        return df

    df["rsi"] = ta.rsi(
        df["close"],
        length = RSI_LENGTH,
    )

    st = ta.supertrend(
        df["high"],
        df["low"],
        df["close"],
        length=ST_LENGTH,
        multiplier=ST_MULTIPLIER
    )
    bb = ta.bands(
        df["close"],
        length = BB_LENGTH,
        std = BB_STD
    )
    df["bb_upper"] = bb[f"BBU_{BB_LENGTH}_{BB_STD}"]
    df["bb_mid"]   = bb[f"BBM_{BB_LENGTH}_{BB_STD}"]
    df["bb_lower"] = bb[f"BBL_{BB_LENGTH}_{BB_STD}"]

    df["supertrend"] = st[f"SUPERT_{ST_LENGTH}_{ST_MULTIPLIER}"]
    df["supertrend_dir"] = st[f"SUPERTd_{ST_LENGTH}_{ST_MULTIPLIER}"]



    log.info(
        "Indicators calculated | RSI=%.1f | ST_dir=%d | BB=%.2f/%.2f/%.2f",
        df["rsi"].iloc[-1],
        df["supertrend_dir"].iloc[-1],
        df["bb_lower"].iloc[-1],
        df["bb_mid"].iloc[-1],
        df["bb_upper"].iloc[-1],

    )
    return df