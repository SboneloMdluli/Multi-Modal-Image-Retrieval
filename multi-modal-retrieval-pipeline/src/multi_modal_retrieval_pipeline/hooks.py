import logging
import logging.config
import time
from pathlib import Path
from typing import Any

from kedro.framework.hooks import hook_impl
from kedro.pipeline.node import Node


class PipelineLoggingHook:
    """Hook for logging pipeline execution."""

    @hook_impl
    def before_pipeline_run(self) -> None:
        """Hook to be called before the pipeline runs.
        Sets up logging configuration.
        """
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure logging
        logging_config = {
            "version": 1,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": "logs/pipeline.log",
                    "mode": "a",
                },
            },
            "loggers": {
                "multi_modal_retrieval_pipeline": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False,
                }
            },
            "root": {"level": "INFO", "handlers": ["console", "file"]},
        }
        logging.config.dictConfig(logging_config)

    @hook_impl
    def before_node_run(self, node: Node) -> None:
        """Hook to be called before a node runs."""
        self._timings[node.name] = time.time()
        logger = logging.getLogger(__name__)
        logger.info(f"Starting execution of node: {node.name}")

    @hook_impl
    def after_node_run(
        self, node: Node, inputs: dict[str, Any], outputs: dict[str, Any]
    ) -> None:
        """Hook to be called after a node runs."""
        end_time = time.time()
        start_time = self._timings.pop(node.name)
        duration = end_time - start_time

        logger = logging.getLogger(__name__)
        logger.info(
            f"Finished execution of node: {node.name} " f"(took {duration:.2f} seconds)"
        )

    def __init__(self):
        self._timings = {}
