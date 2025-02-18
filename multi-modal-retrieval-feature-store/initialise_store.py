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
    """Run a shell command and log its description"""
    logger.info(f"=== {description} ===")
    result = subprocess.run(command, shell=True, check=False)
    if result.returncode != 0:
        logger.error(f"Error during {description}")
        sys.exit(1)
    return result


@timing_decorator
def clean_feast_data():
    """Clean up all Feast-related data"""
    logger.info("Cleaning up Feast data...")
    paths = ["data/online_store.db", "data/registry.db", "data/image_features.pq"]
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
            logger.info(f"Removed {path}")
        except Exception as e:
            logger.exception(f"Error removing {path}: {e}")


@timing_decorator
def prepare_data():
    """Prepare the feature data from embeddings.pq"""
    logger.info("Preparing feature data...")

    try:
        # Read embeddings from the mounted feature_data directory
        df = pd.read_parquet("feature_data/embeddings.pq")
        logger.info(f"Found {len(df)} records in embeddings file")

        # Prepare data for Feast
        feast_df = pd.DataFrame(
            {
                "image_id": df["image_id"],
                "image_data": df["image_data"],
                "embedding": df["embedding"],
                "image_tag": df["image_tag"],
                "event_timestamp": datetime.now(),
            }
        )

        # Save for Feast
        output_path = "data/image_features.pq"
        feast_df.to_parquet(output_path, index=False)
        logger.info(f"Saved prepared data to {output_path}")

        # Verify the saved data
        verify_df = pd.read_parquet(output_path)
        logger.info("Verified saved data:")
        logger.info(f"Columns: {verify_df.columns.tolist()}")
        logger.info(f"Number of rows: {len(verify_df)}")

        return True
    except Exception as e:
        logger.exception(f"Error preparing data: {e}")
        return False


def initialize_store():
    """Initialize and populate the feature store"""

    # Create data directory
    Path("data").mkdir(parents=True, exist_ok=True)

    # Clean up existing data
    clean_feast_data()

    # Prepare the data
    if not prepare_data():
        logger.error("Failed to prepare data")
        return

    try:
        # Apply feature definitions
        run_command("feast apply", "Applying feature definitions")

        # Initialize store
        store = FeatureStore(".")

        # Set materialization date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        logger.info(f"\nMaterializing features from {start_date} to {end_date}")

        # Materialize features
        store.materialize(
            start_date=start_date,
            end_date=end_date,
        )

        logger.info("\nFeature store initialized successfully!")
    except Exception as e:
        logger.exception(f"Error initializing store: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    initialize_store()
