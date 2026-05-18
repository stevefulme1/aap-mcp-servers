"""Tests for extreme MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"EXTREME_HOST": "localhost"}):
            from src.servers.extreme import create_extreme_server
            server = create_extreme_server()
            assert server is not None
