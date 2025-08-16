"""Tests for the main module."""

import pytest

from main import hello_world


class TestMain:
    """Test cases for main module functions."""

    def test_hello_world(self) -> None:
        """Test that hello_world returns the expected string."""
        result = hello_world()
        assert result == "Hello, World!"

    def test_hello_world_type(self) -> None:
        """Test that hello_world returns a string."""
        result = hello_world()
        assert isinstance(result, str)

    @pytest.mark.slow
    def test_hello_world_performance(self) -> None:
        """Test that hello_world executes quickly."""
        import time

        start_time = time.time()
        hello_world()
        execution_time = time.time() - start_time
        assert execution_time < 0.1  # Should execute in less than 100ms
