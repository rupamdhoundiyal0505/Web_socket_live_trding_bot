import pytz
import pandas as pd
from datetime import datetime, timedelta

from config import TIMEZONE, TIMEFRAME_MIN, SYMBOL
from utils import setup_logger

log = setup_logger(__name__)
IST = pytz.timezone(TIMEZONE)


class CandleBuilder:
    def __init__(self, on_candle_close = None,  symbol:str = SYMBOL , timeframe_min: int = TIMEFRAME_MIN):
        self.symbol = symbol
        self.timeframe_min = timeframe_min

        self.temp_ltps = []
        self.candle_start = None
        self.on_candle_close= on_candle_close

        self.candles_df = pd.DataFrame(
            columns=["timestamp","open","high","low","close"]
        )

        log.info(
            "CandleBuilder initialized | symbol=%s | timeframe=%dmin",
            self.symbol, self.timeframe_min
        )

    def add_tick(self, message: dict) -> None:
        ltp = message.get("ltp") # get returns None avoid crsh if key is missing
        ts = message.get("exch_feed_time")
        

        if ltp is None or ts is None:
            log.debug("Incomplete tick skipped: %s", message)
            return
        current_bucket = self._get_candle_bucket(ts)
        if self.candle_start is None:
            self.candle_start = current_bucket
            log.info(
                "First tick | LTP:%.2f | window opened @ %s IST",
                ltp,
                self._to_ist(ts).strftime("%H:%M:%S")
            )
      

        if current_bucket != self.candle_start:
            self._close_candle(current_bucket)

        self.temp_ltps.append(ltp)


    def _close_candle(self, current_ts: int) -> None:
        if not self.temp_ltps:
            log.warning("Empty window- no ticks collected, skipping candle")
            self._reset_window(current_ts)
            return
        o = self.temp_ltps[0]
        h = max(self.temp_ltps)
        l = min(self.temp_ltps)
        c = self.temp_ltps[-1]

        candle_time = self._to_ist(self.candle_start)
        new_candle = {
            "timestamp" : candle_time,
            "open" : o,
            "high" : h,
            "low" : l,
            "close" : c,
        }
        self.candles_df = pd.concat(
            [self.candles_df, pd.DataFrame([new_candle])],
            ignore_index=True

        )

        log.info(
            "CANDLE ✓ | %s | O:%.2f H:%.2f L:%.2f C:%.2f | total=%d",
            candle_time.strftime("%d-%b %H:%M"),
            o,h,l,c,
            len(self.candles_df)
        )
        self._reset_window(current_ts)
        if self.on_candle_close is not None:
            self.on_candle_close(self.candles_df)

    def _get_candle_bucket(self,unix_ts: int) -> int:
        dt=self._to_ist(unix_ts)

        market_open = dt.replace(
            hour=9, minute=15, second=0, microsecond=0
        )

        minutes_since_open = (dt - market_open).total_seconds() // 60
        bucket_index = (
            minutes_since_open // self.timeframe_min
        )
        bucket_start = (
            market_open + timedelta(minutes=bucket_index * self.timeframe_min)
        )

        # aligned_minute = (
        #     dt.minute // self.timeframe_min
        # )* self.timeframe_min
        # bucket = dt.replace(minute=aligned_minute, second=0, microsecond=0)
        return int(bucket_start.timestamp())

    def _reset_window(self, new_start_ts: int) -> None:
        self.temp_ltps = []
        self.candle_start = new_start_ts
        log.debug(
            "Window reset | new window @ %s IST",
            self._to_ist(new_start_ts).strftime("%H:%M:%S")
        )
    
    def get_candles(self) -> pd.DataFrame:
        return self.candles_df.copy()

    def set_candles(self, df: pd.DataFrame) -> None:
        self.candles_df = df.copy()

        log.info(
            "Historical candles loaded | count=%d | first=%s | last=%s",
            len(df),
            df["timestamp"].iloc[0],
            df["timestamp"].iloc[-1],

        )
    def _to_ist(self, unix_ts: int) -> datetime:
        return datetime.fromtimestamp(unix_ts, tz=IST)
