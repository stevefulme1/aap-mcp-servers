"""Tests for vastdata MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"VASTDATA_HOST": "localhost"}):
            from src.servers.vastdata import create_vastdata_server
            server = create_vastdata_server()
            assert server is not None
