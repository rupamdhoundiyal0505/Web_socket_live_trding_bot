from dataclasses import dataclass, fields


@dataclass
class StrategyParams:
    """
    One concrete configuration of the strategy.
    Every field here is something DE is allowed to tune.
    """
    bb_length: int
    bb_std: float
    rsi_length: int
    st_length: int
    st_mult: float
    tp_points: float
    sl_points: float


# Order matters: this list's order must exactly match the order DE's
# vector is built/read in. We derive PARAM_NAMES from the dataclass
# itself so the two can never silently drift out of sync.
PARAM_NAMES = [f.name for f in fields(StrategyParams)]

# (min, max) search range for each param, in the SAME order as PARAM_NAMES.
# These are starting-point guesses — we'll likely tighten/widen them once
# we see real backtest behaviour.
PARAM_BOUNDS = [
    (10, 50),     # bb_length   : Bollinger Band lookback (candles)
    (1.0, 3.0),   # bb_std      : Bollinger Band std-dev multiplier
    (5, 30),      # rsi_length  : RSI lookback (candles)
    (5, 20),      # st_length   : Supertrend ATR lookback (candles)
    (1.0, 5.0),   # st_mult     : Supertrend ATR multiplier
    (10, 200),    # tp_points   : take-profit distance, in index points
    (10, 200),    # sl_points   : stop-loss distance, in index points
]
# DE only ever produces floats, so we round these after the fact.
INTEGER_PARAMS = {"bb_length", "rsi_length", "st_length"}


def params_from_vector(vector) -> StrategyParams:
    """
    Convert a raw DE vector (list/array of floats, in PARAM_BOUNDS order)
    into a usable, named StrategyParams object.
    """
    if len(vector) != len(PARAM_NAMES):
        raise ValueError(
            f"Expected vector of length {len(PARAM_NAMES)}, got {len(vector)}"
        )

    kwargs = {}
    for name, value in zip(PARAM_NAMES, vector):
        if name in INTEGER_PARAMS:
            kwargs[name] = int(round(value))
        else:
            kwargs[name] = float(value)

    return StrategyParams(**kwargs)


def vector_from_params(params: StrategyParams) -> list:
    """
    The reverse of params_from_vector. Mainly useful for tests/debugging,
    or for seeding DE with a known-decent starting guess.
    """
    return [getattr(params, name) for name in PARAM_NAMES]