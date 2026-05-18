"""Tests for oracledb MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"ORACLEDB_HOST": "localhost"}):
            from src.servers.oracledb import create_oracledb_server
            server = create_oracledb_server()
            assert server is not None
