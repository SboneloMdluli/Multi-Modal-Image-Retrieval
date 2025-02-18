"""``DaskRunner`` is an ``AbstractRunner`` implementation. It can be
used to distribute execution of ``Node``s in the ``Pipeline`` across
a Dask cluster, taking into account the inter-``Node`` dependencies.
"""
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager, contextmanager
from itertools import chain
from typing import Any, Dict, Iterator, Optional

from distributed import Client, as_completed, worker_client
from kedro.framework.hooks.manager import (
    _create_hook_manager,
    _register_hooks,
    _register_hooks_entry_points,
)
from kedro.framework.project import settings
from kedro.io import AbstractDataset, DataCatalog
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.runner import AbstractRunner, run_node
from pluggy import PluginManager

logger = logging.getLogger(__name__)


class _DaskDataset(AbstractDataset):
    """``_DaskDataset`` publishes/gets named datasets to/from the Dask
    scheduler."""

    def __init__(self, name: str):
        self._name = name

    def _load(self) -> Any:
        try:
            with worker_client() as client:
                return client.get_dataset(self._name)
        except ValueError:
            # Upon successfully executing the pipeline, the runner loads
            # free outputs on the scheduler (as opposed to on a worker).
            Client.current().get_dataset(self._name)

    def _save(self, data: Any) -> None:
        with worker_client() as client:
            client.publish_dataset(data, name=self._name, override=True)

    def _exists(self) -> bool:
        return self._name in Client.current().list_datasets()

    def _release(self) -> None:
        Client.current().unpublish_dataset(self._name)

    def _describe(self) -> Dict[str, Any]:
        return dict(name=self._name)


class DaskRunner(AbstractRunner):
    """DaskRunner for distributed computation."""

    def __init__(self, client_args: Dict[str, Any] = None, is_async: bool = False):
        """Initialize with Dask client arguments."""
        super().__init__(is_async=is_async)
        self._client_args = client_args or {}
        self._client = None

    def _initialize_client(self):
        """Initialize Dask client with error handling."""
        if self._client is None:
            try:
                logger.info("Initializing Dask client with args: %s", self._client_args)
                self._client = Client(**self._client_args)
                logger.info("Dask client initialized successfully: %s", self._client)
            except Exception as e:
                logger.error("Failed to initialize Dask client: %s", str(e))
                raise

    def create_default_dataset(self, ds_name: str) -> _DaskDataset:
        """Factory method for creating the default dataset for the runner.

        Args:
            ds_name: Name of the missing dataset.

        Returns:
            An instance of ``_DaskDataset`` to be used for all
            unregistered datasets.
        """
        return _DaskDataset(ds_name)

    @staticmethod
    def _run_node(
        node: Node,
        catalog: DataCatalog,
        is_async: bool = False,
        session_id: str = None,
        *dependencies: Node,
    ) -> Node:
        """Run a single `Node` with inputs from and outputs to the `catalog`.

        Args:
            node: The ``Node`` to run.
            catalog: A ``DataCatalog`` containing the node's inputs and outputs.
            is_async: If True, the node inputs and outputs are loaded and saved
                asynchronously with threads. Defaults to False.
            session_id: The session id of the pipeline run.
            dependencies: The upstream ``Node``s to allow Dask to handle
                dependency tracking.

        Returns:
            The node argument.
        """
        hook_manager = _create_hook_manager()
        _register_hooks(hook_manager, settings.HOOKS)
        _register_hooks_entry_points(hook_manager, settings.DISABLE_HOOKS_FOR_PLUGINS)

        # Load inputs in chunks to reduce memory usage
        inputs = {}
        for input_name in node.inputs:
            dataset = catalog._get_dataset(input_name)
            if hasattr(dataset, "read_chunked"):
                # For datasets that support chunked reading
                inputs[input_name] = dataset.read_chunked()
            else:
                inputs[input_name] = catalog.load(input_name)

        # Run the node
        outputs = node.run(inputs)

        # Save outputs in chunks when possible
        for output_name, output_value in outputs.items():
            dataset = catalog._get_dataset(output_name)
            if hasattr(dataset, "write_chunked"):
                # For datasets that support chunked writing
                dataset.write_chunked(output_value)
            else:
                catalog.save(output_name, output_value)

        return node

    def _run(
        self,
        pipeline: Pipeline,
        catalog: DataCatalog,
        hook_manager: PluginManager,
        session_id: str = None,
    ) -> None:
        """Run the pipeline with Dask."""
        try:
            self._initialize_client()
            logger.info("Starting pipeline execution with Dask")

            nodes = pipeline.nodes
            load_counts = Counter(chain.from_iterable(n.inputs for n in nodes))
            node_dependencies = pipeline.node_dependencies
            node_futures = {}

            client = Client.current()

            # Process nodes in batches to control memory usage
            batch_size = 10  # Adjust based on your system's capabilities
            for i in range(0, len(nodes), batch_size):
                batch_nodes = nodes[i : i + batch_size]
                batch_futures = {}

                for node in batch_nodes:
                    dependencies = (
                        node_futures[dependency]
                        for dependency in node_dependencies[node]
                        if dependency in node_futures
                    )
                    batch_futures[node] = client.submit(
                        DaskRunner._run_node,
                        node,
                        catalog,
                        self._is_async,
                        session_id,
                        *dependencies,
                        pure=False,  # Prevent caching of large intermediate results
                    )

                # Wait for batch completion and release memory
                for i, (_, node) in enumerate(
                    as_completed(batch_futures.values(), with_results=True)
                ):
                    self._logger.info("Completed node: %s", node.name)

                    # Release memory for completed node
                    for dataset in node.inputs:
                        load_counts[dataset] -= 1
                        if (
                            load_counts[dataset] < 1
                            and dataset not in pipeline.inputs()
                        ):
                            catalog.release(dataset)
                    for dataset in node.outputs:
                        if (
                            load_counts[dataset] < 1
                            and dataset not in pipeline.outputs()
                        ):
                            catalog.release(dataset)

                # Update node_futures with completed batch
                node_futures.update(batch_futures)

                # Force garbage collection after each batch
                client.run_on_scheduler(
                    lambda dask_scheduler: dask_scheduler.validate_state()
                )

        except Exception as e:
            logger.error("Pipeline execution failed: %s", str(e))
            raise
        finally:
            if self._client is not None:
                logger.info("Closing Dask client")
                self._client.close()
                self._client = None

    def run_only_missing(
        self, pipeline: Pipeline, catalog: DataCatalog
    ) -> Dict[str, Any]:
        """Run only the missing outputs from the ``Pipeline`` using the
        datasets provided by ``catalog``, and save results back to the
        same objects.

        Args:
            pipeline: The ``Pipeline`` to run.
            catalog: The ``DataCatalog`` from which to fetch data.
        Raises:
            ValueError: Raised when ``Pipeline`` inputs cannot be
                satisfied.

        Returns:
            Any node outputs that cannot be processed by the
            ``DataCatalog``. These are returned in a dictionary, where
            the keys are defined by the node outputs.
        """
        free_outputs = pipeline.outputs() - set(catalog.list())
        missing = {ds for ds in catalog.list() if not catalog.exists(ds)}
        to_build = free_outputs | missing
        to_rerun = pipeline.only_nodes_with_outputs(*to_build) + pipeline.from_inputs(
            *to_build
        )

        # We also need any missing datasets that are required to run the
        # `to_rerun` pipeline, including any chains of missing datasets.
        unregistered_ds = pipeline.datasets() - set(catalog.list())
        # Some of the unregistered datasets could have been published to
        # the scheduler in a previous run, so we need not recreate them.
        missing_unregistered_ds = {
            ds_name
            for ds_name in unregistered_ds
            if not self.create_default_dataset(ds_name).exists()
        }
        output_to_unregistered = pipeline.only_nodes_with_outputs(
            *missing_unregistered_ds
        )
        input_from_unregistered = to_rerun.inputs() & missing_unregistered_ds
        to_rerun += output_to_unregistered.to_outputs(*input_from_unregistered)

        # We need to add any previously-published, unregistered datasets
        # to the catalog passed to the `run` method, so that it does not
        # think that the `to_rerun` pipeline's inputs are not satisfied.
        catalog = catalog.shallow_copy()
        for ds_name in unregistered_ds - missing_unregistered_ds:
            catalog.add(ds_name, self.create_default_dataset(ds_name))

        return self.run(to_rerun, catalog)

    def _get_executor(self) -> AbstractContextManager[ThreadPoolExecutor]:
        """Create a new ThreadPoolExecutor.

        Returns:
            ThreadPoolExecutor wrapped in a context manager.
        """

        @contextmanager
        def _executor_manager() -> Iterator[ThreadPoolExecutor]:
            with ThreadPoolExecutor(max_workers=None) as executor:
                yield executor

        return _executor_manager()
