"""Tests for mssql MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"MSSQL_HOST": "localhost"}):
            from src.servers.mssql import create_mssql_server
            server = create_mssql_server()
            assert server is not None
