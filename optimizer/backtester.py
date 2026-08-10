import pandas as pd
import pandas_ta as ta

from strategy_params import StrategyParams

# Penalty score handed back when a parameter set produces zero trades.
# Without this, "never trade" would score as net_profit=0 / drawdown=0,
# which DE could misread as a perfect (infinite) risk-adjusted score.
NO_TRADE_PENALTY = -1_000_000.0


def _compute_indicators(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """Recompute BB / RSI / Supertrend using THIS trial's params (not
    config.py's fixed values — those only matter for the live bot)."""
    df = df.copy()

    sma = df["close"].rolling(params.bb_length).mean()
    std = df["close"].rolling(params.bb_length).std(ddof=0)
    df["bb_mid"] = sma
    df["bb_upper"] = sma + params.bb_std * std
    df["bb_lower"] = sma - params.bb_std * std

    df["rsi"] = ta.rsi(df["close"], length=params.rsi_length)

    st = ta.supertrend(
        df["high"], df["low"], df["close"],
        length=params.st_length, multiplier=params.st_mult,
    )
    # Find columns by prefix instead of hardcoding the format string —
    # pandas_ta's naming of the multiplier (3 vs 3.0) can vary, so this
    # is more robust than the f"SUPERT_{length}_{mult}" pattern used
    # in indicator_engine.py.
    val_col = [c for c in st.columns if c.startswith("SUPERT_")][0]
    dir_col = [c for c in st.columns if c.startswith("SUPERTd_")][0]
    df["supertrend"] = st[val_col]
    df["supertrend_dir"] = st[dir_col]

    return df


def _simulate_trades(df: pd.DataFrame, params: StrategyParams) -> list:
    """
    Walk candle-by-candle, holding at most ONE open position at a time
    (flat / long / short). This mirrors a single trader who waits for
    one trade to close before opening the next.
    """
    trades = []
    position = None  # None, or a dict describing the open trade

    for i in range(len(df)):
        row = df.iloc[i]

        # Indicators need `length` candles of history before they're valid.
        if pd.isna(row["bb_lower"]) or pd.isna(row["rsi"]) or pd.isna(row["supertrend_dir"]):
            continue

        # --- 1. If we're in a trade, check whether THIS candle hits TP or SL ---
        if position is not None:
            exit_price = None
            exit_reason = None

            if position["direction"] == "LONG":
                if row["low"] <= position["sl"]:
                    exit_price, exit_reason = position["sl"], "SL"
                elif row["high"] >= position["tp"]:
                    exit_price, exit_reason = position["tp"], "TP"
            else:  # SHORT
                if row["high"] >= position["sl"]:
                    exit_price, exit_reason = position["sl"], "SL"
                elif row["low"] <= position["tp"]:
                    exit_price, exit_reason = position["tp"], "TP"

            if exit_price is not None:
                pnl = (
                    exit_price - position["entry_price"]
                    if position["direction"] == "LONG"
                    else position["entry_price"] - exit_price
                )
                trades.append({
                    "direction": position["direction"],
                    "entry_time": position["entry_time"],
                    "entry_price": position["entry_price"],
                    "exit_time": row["timestamp"],
                    "exit_price": exit_price,
                    "exit_reason": exit_reason,
                    "pnl_points": pnl,
                })
                position = None
                # Don't also open a new trade on the same candle we just exited on.
                continue

        # --- 2. If flat, check entry conditions ---
        if position is None:
            long_signal = (
                row["close"] < row["bb_lower"]
                and row["rsi"] < 30
                and row["supertrend_dir"] == 1
            )
            short_signal = (
                row["close"] > row["bb_upper"]
                and row["rsi"] > 70
                and row["supertrend_dir"] == -1
            )

            if long_signal:
                entry_price = row["close"]
                position = {
                    "direction": "LONG",
                    "entry_time": row["timestamp"],
                    "entry_price": entry_price,
                    "tp": entry_price + params.tp_points,
                    "sl": entry_price - params.sl_points,
                }
            elif short_signal:
                entry_price = row["close"]
                position = {
                    "direction": "SHORT",
                    "entry_time": row["timestamp"],
                    "entry_price": entry_price,
                    "tp": entry_price - params.tp_points,
                    "sl": entry_price + params.sl_points,
                }

    # --- 3. If a trade is still open when data runs out, mark it to market ---
    # so we don't just throw away an in-progress trade's P&L.
    if position is not None:
        last_row = df.iloc[-1]
        exit_price = last_row["close"]
        pnl = (
            exit_price - position["entry_price"]
            if position["direction"] == "LONG"
            else position["entry_price"] - exit_price
        )
        trades.append({
            "direction": position["direction"],
            "entry_time": position["entry_time"],
            "entry_price": position["entry_price"],
            "exit_time": last_row["timestamp"],
            "exit_price": exit_price,
            "exit_reason": "EOD",
            "pnl_points": pnl,
        })

    return trades


def _compute_metrics(trades: list) -> dict:
    """Turn a list of trades into the numbers DE actually optimizes on."""
    if not trades:
        return {
            "num_trades": 0,
            "net_profit": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "objective": NO_TRADE_PENALTY,
        }

    pnls = [t["pnl_points"] for t in trades]

    # Equity curve: running total of P&L after each trade closes.
    equity_curve = []
    running = 0.0
    for pnl in pnls:
        running += pnl
        equity_curve.append(running)

    net_profit = equity_curve[-1]

    # Max drawdown: the worst peak-to-trough drop the equity curve ever saw.
    peak = equity_curve[0]
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        drawdown = peak - eq
        if drawdown > max_dd:
            max_dd = drawdown

    win_rate = sum(1 for pnl in pnls if pnl > 0) / len(pnls)

    if max_dd <= 0:
        # Never went underwater (e.g. all winning trades) — reward
        # profit directly rather than dividing by zero.
        objective = net_profit
    else:
        objective = net_profit / max_dd

    return {
        "num_trades": len(trades),
        "net_profit": net_profit,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "objective": objective,
    }


def run_backtest(df: pd.DataFrame, params: StrategyParams) -> dict:
    """
    Public entry point. Given historical candles and one StrategyParams
    configuration, returns a metrics dict (net_profit, max_drawdown,
    objective, win_rate, num_trades) plus the raw trade list.
    """
    df_with_indicators = _compute_indicators(df, params)
    trades = _simulate_trades(df_with_indicators, params)
    metrics = _compute_metrics(trades)
    metrics["trades"] = trades
    return metrics