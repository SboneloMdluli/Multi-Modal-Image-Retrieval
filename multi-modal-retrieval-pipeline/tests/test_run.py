"""
This module contains example tests for a Kedro project.
Tests should be placed in ``src/tests``, in modules that mirror your
project's structure, and in files named test_*.py.
"""
from pathlib import Path

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project

# The tests below are here for the demonstration purpose
# and should be replaced with the ones testing the project
# functionality


class TestKedroRun:
    def test_kedro_run(self):
        # Get the project root directory (2 levels up from the test file)
        project_path = Path(__file__).parent.parent
        bootstrap_project(project_path)

        with KedroSession.create(project_path=project_path) as session:
            assert session.run() is not None
