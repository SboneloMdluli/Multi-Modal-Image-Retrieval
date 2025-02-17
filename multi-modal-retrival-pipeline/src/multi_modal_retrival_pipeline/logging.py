import logging
import sys
import time
from pathlib import Path
from typing import Any

from kedro.framework.hooks import hook_impl
from kedro.pipeline.node import Node


# Create and configure the logger
def setup_logger():
    """Set up and return the logger instance"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Configure formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create logger
    logger = logging.getLogger("multi_modal_retrival_pipeline")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler("logs/pipeline.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent duplicate logs
    logger.propagate = False

    return logger


# Create the logger instance
logger = setup_logger()


class PipelineLoggingHook:
    """Hook for logging pipeline execution."""

    def __init__(self):
        self._timings: dict[str, float] = {}
        self._logger = logger  # Use the same logger instance

    @hook_impl
    def before_pipeline_run(self, run_params: dict[str, Any]) -> None:
        """Hook to be called before a pipeline runs."""
        self._logger.info("=" * 80)
        self._logger.info("Starting pipeline run")
        self._logger.info(f"Run parameters: {run_params}")

    @hook_impl
    def before_node_run(self, node: Node) -> None:
        """Hook to be called before a node runs."""
        self._timings[node.name] = time.time()
        self._logger.info(f"Starting node: {node.name}")

    @hook_impl
    def after_node_run(self, node: Node, inputs: dict[str, Any], outputs: Any) -> None:
        """Hook to be called after a node runs."""
        run_time = time.time() - self._timings[node.name]
        self._logger.info(f"Completed node: {node.name} (took: {run_time:.2f} seconds)")
        self._logger.info(f"Node inputs: {list(inputs.keys())}")
        self._logger.info(
            f"Node outputs: {outputs if isinstance(outputs, (list, str)) else type(outputs)}"
        )

    @hook_impl
    def after_pipeline_run(self) -> None:
        """Hook to be called after a pipeline runs."""
        total_time = sum(time.time() - t for t in self._timings.values())
        self._logger.info(f"Pipeline completed (total time: {total_time:.2f} seconds)")
        self._logger.info("=" * 80)

    @hook_impl
    def on_pipeline_error(self, error: Exception) -> None:
        """Hook to be called when a pipeline fails."""
        self._logger.error(f"Pipeline failed with error: {str(error)}", exc_info=True)
        self._logger.info("=" * 80)


# Export both the logger and the hook
__all__ = ["logger", "PipelineLoggingHook"]
