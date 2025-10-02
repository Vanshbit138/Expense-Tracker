"""
Tests for the run_server module.
"""


class TestRunServer:
    """Test cases for run_server script."""

    def test_run_server_module_imports(self):
        """Test that run_server module imports correctly."""
        import run_server

        assert hasattr(run_server, "uvicorn")

    def test_uvicorn_module_available(self):
        """Test that uvicorn module is available."""
        import uvicorn

        assert uvicorn is not None
