import logging
import sys
from pathlib import Path


def setup_logging():
    """Set up logging configuration for Feast feature store."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler("logs/feast_store.log", mode="a"),
        ],
    )

    # Create logger for the feast store
    logger = logging.getLogger("feast_feature_store")
    logger.setLevel(logging.INFO)

    return logger


# Create and configure logger
logger = setup_logging()
