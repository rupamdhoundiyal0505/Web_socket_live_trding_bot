import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TIMEFRAME_MIN
from utils import setup_logger
log = setup_logger(__name__)
_prev_signal = "HOLD"
def _format_message(signal: str, df) -> str:
    last = df.iloc[-1]
    emoji = {
        "BUY"  : "🟢",
        "SELL" : "🔴",
        "HOLD" : "🟡"
    }.get(signal, "⚪")
    direction = "Bullish ↑" if last["supertrend_dir"] == 1 else "Bearish ↓"

    return (
        f"{emoji} *{signal}* — {SYMBOL}\n"
        f"🕐 {last['timestamp'].strftime('%d-%b %H:%M')} | TF: {TIMEFRAME_MIN}min\n\n"
        f"💰 Close : `{last['close']:.2f}`\n"
        f"📊 RSI   : `{last['rsi']:.1f}`\n"
        f"📈 ST Dir: `{direction}`\n"
        f"🎯 BB    : `{last['bb_lower']:.2f}` / `{last['bb_mid']:.2f}` / `{last['bb_upper']:.2f}`\n"
    )

def send_alert(signal: str, df) ->None:
    global _prev_signal

    if signal == _prev_signal:
        log.debug("Signal unchanged (%s) — skipping alert", signal)
        return

    message = _format_message(signal, df)
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload={
        "chat_id" : TELEGRAM_CHAT_ID,
        "text" : message,
        "parse_mode" : "Markdown",
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            log.info("Telegram alert sent → %s", signal)
        else:
            log.error("Telegram failed | status=%d | %s", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        log.error("Telegram request failed: %s", e)

    _prev_signal = signal

