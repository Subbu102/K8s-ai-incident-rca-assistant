"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import Generator

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_pod_details():
    """Sample pod details for testing."""
    return {
        "pod_name": "test-pod-123",
        "namespace": "test-namespace",
        "phase": "Failed",
        "restart_count": 3,
        "node": "node-1"
    }


@pytest.fixture
def sample_error_logs():
    """Sample error logs for testing."""
    return """
2024-01-10T10:05:23Z ERROR Connection timeout connecting to database
2024-01-10T10:05:24Z ERROR Connection refused at localhost:5432
2024-01-10T10:05:25Z ERROR Failed to initialize database connection
    at DBConnector.connect (src/db.py:45)
    at Application.start (src/main.py:23)
Stack Trace: Connection timeout after 30 seconds
2024-01-10T10:05:26Z WARNING Retrying connection (attempt 2/3)
2024-01-10T10:05:27Z ERROR FATAL: Connection refused
"""
