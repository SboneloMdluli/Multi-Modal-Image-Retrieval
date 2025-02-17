import logging
import time
from typing import Any

from kedro.framework.hooks import hook_impl
from kedro.pipeline.node import Node


class TimingHook:
    """Hook for timing node execution."""

    def __init__(self):
        self._timings: dict[str, float] = {}
        self._logger = logging.getLogger(__name__)

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

    @hook_impl
    def after_pipeline_run(self) -> None:
        """Hook to be called after a pipeline runs."""
        total_time = sum(time.time() - t for t in self._timings.values())
        self._logger.info(f"Total pipeline run time: {total_time:.2f} seconds")
