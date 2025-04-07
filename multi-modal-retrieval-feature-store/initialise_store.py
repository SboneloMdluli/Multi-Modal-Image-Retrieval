import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import logging_config
import pandas as pd
from feast import FeatureStore
from utils import timing_decorator

logger = logging_config.logger


def run_command(command, description):
    """Run a shell command and log its description."""
    logger.info("=== %s ===", description)
    result = subprocess.run(command, shell=True, check=False)
    if result.returncode != 0:
        logger.error("Error during %s", description)
        sys.exit(1)
    return result


@timing_decorator
def clean_feast_data() -> None:
    """Clean up all Feast-related data."""
    logger.info("Cleaning up Feast data...")
    paths = [
        "data/online_store.db",
        "data/registry.db",
        "data/image_features.pq",
    ]
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
            logger.info("Removed %s", path)
        except Exception as e:
            logger.exception("Error removing %s: %s", path, e)


@timing_decorator
def prepare_data() -> bool | None:
    """Prepare the feature data from embeddings.pq."""
    logger.info("Preparing feature data...")

    try:
        # Read embeddings from the mounted feature_data directory
        df = pd.read_parquet("feature_data/embeddings.pq", engine="pyarrow")
        logger.info("Found %d records in embeddings file", len(df))

        feast_df = pd.DataFrame(
            {
                "image_id": df["image_id"],
                "image_data": df["image_data"],
                "embedding": df["embedding"],
                "image_tag": df["image_tag"],
                "event_timestamp": datetime.now(),
            },
        )

        # Save for Feast
        output_path = "data/image_features.pq"
        feast_df.to_parquet(output_path, index=False)
        logger.info("Saved prepared data to %s", output_path)

        # Verify the saved data
        verify_df = pd.read_parquet(output_path)
        logger.info("Verified saved data:")
        logger.info("Columns: %s", verify_df.columns.tolist())
        logger.info("Number of rows: %d", len(verify_df))

        return True
    except Exception as e:
        logger.exception("Error preparing data: %s", e)
        return False


def initialize_store() -> None:
    """Initialize and populate the feature store."""
    try:
        # Apply feature definitions
        run_command("feast apply", "Applying feature definitions")

        # Initialize store
        store = FeatureStore(".")

        # Set materialization date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        logger.info(
            "\nMaterializing features from %s to %s", start_date, end_date
        )

        # Materialize features
        store.materialize(
            start_date=start_date,
            end_date=end_date,
        )

        logger.info("\nFeature store initialized successfully!")
    except Exception as e:
        logger.exception("Error initializing store: %s", e)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    initialize_store()
