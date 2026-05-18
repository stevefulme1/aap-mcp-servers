"""Tests for elastic MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"ELASTIC_HOST": "localhost"}):
            from src.servers.elastic import create_elastic_server
            server = create_elastic_server()
            assert server is not None
