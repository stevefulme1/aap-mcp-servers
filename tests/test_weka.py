"""Tests for weka MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"WEKA_HOST": "localhost"}):
            from src.servers.weka import create_weka_server
            server = create_weka_server()
            assert server is not None
