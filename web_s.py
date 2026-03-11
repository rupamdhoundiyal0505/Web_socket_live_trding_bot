from pickle import TRUE
from fyers_apiv3.FyersWebsocket import data_ws
import logging

#CONSTANTS 

CLIENT_ID = "KUC4376MFF-100"
TOKEN_FILE = "access_token.txt"
SYMBOL = "NSE:NIFTY-EQ"


logging.basicConfig(
    level=logging.INFO,
    format="%(acttime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log=logging.getLogger(__name__)


# READ ACCESS TOKEN

def read_access_token(filepath: str) -> str:
    with open(filepath, "r") as f:
        token = f.read().strip()
    if not token:
        raise ValueError(f"Token file is empty!!")
    return token

def on_meesage(message: dict) -> None:
    if isinstance(message, dict) and 'ltp' in message:
        log.info(
            "tick %-20s LTP: %8.2f H: %8.2f L: %8.2f",
            message.get("symbol", "?"), #.get to avoid crsh and 0 ? are safe fallback vals
            message.get("ltp", 0), # last traded price for that symbol tick data
            message.get("high", 0), # Day open price
            message.get("low", 0), # Lowest price so far
        )
            
    else:
        log.info("MSG %s", message)
def on_error(message: dict) -> None:
    log.error("Websocket error: %s", message)
def on_close(message: dict) -> None:
    log.warning("Websocket closed: %s", message)
def on_open(message: dict) -> None:
    log.info("WEBSOCKET CONNECTED :")
    log.info("Subscribed to %s", SYMBOL)
    fyers_ws.subscribe(
        symbols = [SYMBOL],
        data_type = "SymbolUpdate",
    )
    fyers_ws.keep_running()#Tells the SDK's internal event loop to keep listening for incoming ticks. Without this, on_open finishes and the connection goes idle — no more ticks received.
# Fyers sends time as "tt": 1718000123 — this is a Unix timestamp: number of seconds since January 1, 1970.

def main():
    global fyers_ws
    access_token= read_access_token(TOKEN_FILE)
    full_token=f"{CLIENT_ID}:{access_token}" #format fyers want
    fyers_ws = data_ws.FyersDataSocket(
        access_token=full_token,
        log_path="",
        litemode=False,
        write_to_file=False, #don't dump raw tick JSON to disk 
        reconnect=TRUE, # if WiFi drops for 2 seconds, SDK reconnects automatically
        on_connect=on_open,
        on_close=on_close,
        on_error=on_error,
        on_message=on_meesage,
    )
    log.info("Connecting to Fyers websocket...")
    fyers_ws.connect() # its a blocking fxn lines after this are unreachable
    # opens a TCP socket
    # fyers will call now on_open

if __name__=="__main__":
    main()

