from tkinter import N
from fyers_apiv3 import fyersModel
from config import CLIENT_ID, TIMEZONE, TIMEFRAME_MIN, CANDLE_LIMIT, SYMBOL
from utils import setup_logger, read_access_token
log = setup_logger(__name__)



# print(response)
def fetch_option_chain(symbol: str = SYMBOL):
    client_id = CLIENT_ID
    access_token = read_access_token()
    # Initialize the FyersModel instance with your client_id, access_token, and enable async mode
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")
    data = {
        "symbol":symbol,
        "strikecount":10,
        "timestamp": "",
        "greeks":"0"
    }
    response = fyers.optionchain(data=data);
    if response.get("s") != "ok":
        log.error("Option chain fetch failed: %s", response)
        return []
    options = [
        opt 
        for opt in response["data"]["optionsChain"]
        if opt["option_type"] in ["CE", "PE"]
    ]
    log.info("Option chain fetched successfully!!")
    return options



def  select_option(options: list, signal_type: str): # options is a list of dictionaries containing option data
    option_type = (
        "CE" if signal_type == "BUY" else "PE"
    )
    print("Signal Type:", signal_type)
    print("Option Type:", option_type)
    candidates = [
        opt
        for opt in options
        if (
        
            opt["option_type"] == option_type
            and 300<= opt["ltp"] <=350

            )
        ]
    # print("Candidate Types:")
    # for c in candidates[:10]:
    #     print(c["option_type"], c["strike_price"], c["ltp"])
    
    if not candidates:
        return None

    best = min(
        candidates,
        key = lambda opt: abs(opt["ltp"] - 300)
    )
    return {
        "strike": best["strike_price"],
        "premium": best["ltp"],
        "symbol" : best["symbol"],
    

    }

def get_trade_setup( signal_type: str, symbol: str = SYMBOL):
    options = fetch_option_chain(symbol)
    if not options:
        return None
    trade_setup = select_option(options, signal_type)
    return trade_setup


# print(get_trade_setup("BUY", SYMBOL))
# print(get_trade_setup("SELL", SYMBOL))