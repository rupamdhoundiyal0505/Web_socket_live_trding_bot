import pandas as pd
import pandas_ta as ta
from config import BB_LENGTH, BB_LOWER_STD, BB_UPPER_STD, RSI_LENGTH, ST_LENGTH, ST_MULTIPLIER
from utils import setup_logger
from bb_cal import bb_calculation


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
    # bb = ta.bbands(
    #     df["close"],
    #     length = BB_LENGTH,
    #     lower_std = BB_LOWER_STD,
    #     upper_std = BB_UPPER_STD,
    # )
    # print("BB columns: using std as 1.0", bb.columns.tolist())   # ← add this
    # print("BB_LENGTH:", BB_LENGTH, "BB_STD:", BB_STD)  # ← add this
    bb= bb_calculation(df)
    df["bb_lower"] = bb["bb_lower"]  # first column  = BBL
    df["bb_mid"]   = bb["bb_mid"] # second column = BBM
    df["bb_upper"] = bb["bb_upper"] # third column  = BBU
    

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