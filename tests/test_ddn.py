"""Tests for ddn MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"DDN_HOST": "localhost"}):
            from src.servers.ddn import create_ddn_server
            server = create_ddn_server()
            assert server is not None
