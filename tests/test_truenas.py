"""Tests for truenas MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"TRUENAS_HOST": "localhost"}):
            from src.servers.truenas import create_truenas_server
            server = create_truenas_server()
            assert server is not None
