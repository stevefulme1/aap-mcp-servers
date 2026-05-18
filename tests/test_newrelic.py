"""Tests for newrelic MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"NEWRELIC_HOST": "localhost"}):
            from src.servers.newrelic import create_newrelic_server
            server = create_newrelic_server()
            assert server is not None
