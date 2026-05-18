"""Tests for coreweave MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"COREWEAVE_HOST": "localhost"}):
            from src.servers.coreweave import create_coreweave_server
            server = create_coreweave_server()
            assert server is not None
