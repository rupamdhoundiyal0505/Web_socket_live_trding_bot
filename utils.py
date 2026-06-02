import logging
import logging.handlers

from config import TOKEN_FILE

# Create logger
#     ↓
# Define formatting style
#     ↓
# Create console handler
#     ↓
# Create file handler
#     ↓
# Attach handlers to logger
#     ↓
# Return logger

# Logging Levels
# DEBUG     → detailed info
# INFO      → normal events
# WARNING   → something suspicious
# ERROR     → failure happened
# CRITICAL  → major crash

# Concept

# If level is:

# logging.INFO

# Then DEBUG logs are ignored.
# Python logging works like a global registry system.
def setup_logger(name: str, level=logging.DEBUG)-> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(level)
    
    formatter = logging.Formatter(
        fmt = "%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S"
    )
    stream = logging.StreamHandler()
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(formatter)

    # stream = logging.StreamHandler()
    # stream.setLevel(logging.DEBUG)
    # stream.setFormatter(formatter)

    file = logging.handlers.RotatingFileHandler(
        filename= "bot.log",
        maxBytes=5*1024*1024,
        backupCount=3
    )

    file.setLevel(logging.INFO)
    file.setFormatter(formatter)

    if not log.handlers:
        log.addHandler(stream)
        log.addHandler(file)

    return log


def read_access_token()-> str:
    log = setup_logger(__name__)
    try:
        with open(TOKEN_FILE , "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(
            f" '{TOKEN_FILE}' not found"
            f"Place your access token in {TOKEN_FILE}"
            f"in the same folder as main.py"
        )
    if not token:
        raise ValueError(
            f"'{TOKEN_FILE}' is empty "
            f"Paste your fyers access token into it"
        )

    log.info("Accesss token loaded....")
    return token

