import pandas as pd
from config import BB_LENGTH, BB_LOWER_STD





def bb_calculation(df):

    bb_df = df.copy()
    bb_df["sma"]= (
        bb_df["close"].rolling(BB_LENGTH).mean()
    )

    bb_df["std_ddof0"]=(
        bb_df["close"].rolling(BB_LENGTH).std(ddof=0)

    )

    bb_df["upper_ddof0"] = (
        bb_df["sma"]
        + BB_LOWER_STD * bb_df["std_ddof0"]
    )

    bb_df["lower_ddof0"]= (
        bb_df["sma"]
        - BB_LOWER_STD * bb_df["std_ddof0"]
    )

    last = bb_df.iloc[-1]
    print(last.tolist())

    return {
        "bb_mid" : last["sma"],
        "bb_upper" : last["upper_ddof0"],
        "bb_lower" : last["lower_ddof0"]
    }
    










