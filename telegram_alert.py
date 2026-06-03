import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TIMEFRAME_MIN
from utils import setup_logger
log = setup_logger(__name__)


def send_alert(market_state: dict) ->None:
    active_buy = market_state.get("active_buy")
    active_buy_strike = market_state.get("active_buy_trade")
    active_sell_strike = market_state.get("active_sell_trade")
    active_sell = market_state.get("active_sell")
    market_data = market_state.get("market_data")


    if market_data is None:
        log.warning("Market data not available — skipping alert")
        return

    if active_buy is not None:

        buy_text = (
            "🟢 ACTIVE BUY SIGNAL\n"
            f"Time  : {active_buy['timestamp']}\n"
            f"High  : {active_buy['high']:.2f}\n"
            f"{active_buy_strike}\n"
        )

    else:

        buy_text = "🟢 ACTIVE BUY SIGNAL : NONE\n"

    if active_sell is not None:

        sell_text = (
            "🔴 ACTIVE SELL SIGNAL\n"
            f"Time  : {active_sell['timestamp']}\n"
            f"Low   : {active_sell['low']:.2f}\n"
            f"{active_sell_strike}\n"
        )

    else:

        sell_text = "🔴 ACTIVE SELL SIGNAL : NONE\n"
    market_text = (
        "📈 CURRENT MARKET\n"
        f"Time  : {market_data['timestamp']}\n"
        f"Close : {market_data['close']:.2f}\n"
        f"High  : {market_data['high']:.2f}\n"
        f"Low   : {market_data['low']:.2f}\n"
        # f"RSI   : {market_data['rsi']:.2f}\n"
        # f"BB_mid: {market_data['bb_mid']:.2f}\n"
    )


    message = (
        "📊 MARKET UPDATE\n\n"
        f"Symbol : {SYMBOL}\n"
        f"TF     : {TIMEFRAME_MIN} min\n\n"
        f"{buy_text}\n"
        f"{sell_text}\n"
        f"{market_text}"
    )
    


    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload={
        "chat_id" : TELEGRAM_CHAT_ID,
        "text" : message,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            log.info("Telegram alert sent ")
        else:
            log.error("Telegram failed | status=%d | %s", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        log.error("Telegram request failed: %s", e)

