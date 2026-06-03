from fyers_apiv3.FyersWebsocket import data_ws
from config import CANDLE_LIMIT, CLIENT_ID, SYMBOL, TIMEFRAME_MIN
from utils import setup_logger, read_access_token
from candle_builder import CandleBuilder
from history_loader import fetch_historical_candles
from indicator_engine import calculate_indicators
from signal_engine import generate_signal
from telegram_alert import send_alert

log = setup_logger(__name__)
builder = None
fyers_ws = None


def on_message(message: dict) -> None:
    if isinstance(message, dict) and "ltp" in message:
        builder.add_tick(message)
    else:
        log.debug("Non price message: %s", message)

def on_error(message: dict) -> None:
    log.error("WebSocket error :%s", message)

def on_close(message: dict) -> None:
    log.warning("Web socket close %s", message)
    candles = builder.get_candles()
    if not candles.empty:
        log.info("Candles collected:\n%s", candles.to_string())


def on_open() -> None:
    log.info("Websocket Connected")
    fyers_ws.subscribe(
        symbols=[SYMBOL],
        data_type="SymbolUpdate",
    )
    fyers_ws.keep_running()

def on_candle_close(df):
    df = builder.get_candles()
    print(f"Candles shape: {df.shape}") 
    df = calculate_indicators(df)
    print(f"Columns after indicators: {df.columns.tolist()}")  # what columns exist
    print(f"Last row:\n{df.iloc[-1]}")  
    signal_state = generate_signal(df)
    # print(f"Signal state: {signal_state}")
    send_alert(signal_state)
    df.to_csv("testing.csv")


def main(timeframe_min: int = TIMEFRAME_MIN):
    global builder, fyers_ws
    log.info("   Fyers Signal Bot — Starting    ")
    log.info("Symbol    : %s", SYMBOL)
    log.info("Timeframe : %d min", timeframe_min)

    builder = CandleBuilder(
        on_candle_close=on_candle_close,
        symbol = SYMBOL,
        timeframe_min = timeframe_min
    )
    df = fetch_historical_candles(
        symbol= SYMBOL,
        timeframe_min=timeframe_min,
        limit = CANDLE_LIMIT,
    )
    builder.set_candles(df)
    access_token = read_access_token()
    full_token = f"{CLIENT_ID}:{access_token}"

    fyers_ws = data_ws.FyersDataSocket(
        access_token  = full_token,
        log_path      = "",
        litemode      = False,
        write_to_file = False,
        reconnect     = True,
        on_connect    = on_open,
        on_close      = on_close,
        on_error      = on_error,
        on_message    = on_message,

    )
    log.info("Connecting to Fyers WebSocket...")
    fyers_ws.connect()


if __name__ == "__main__":
    main()