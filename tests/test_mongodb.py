"""Tests for mongodb MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"MONGODB_HOST": "localhost"}):
            from src.servers.mongodb import create_mongodb_server
            server = create_mongodb_server()
            assert server is not None
