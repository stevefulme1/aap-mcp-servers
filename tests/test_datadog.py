"""Tests for datadog MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"DATADOG_HOST": "localhost"}):
            from src.servers.datadog import create_datadog_server
            server = create_datadog_server()
            assert server is not None
