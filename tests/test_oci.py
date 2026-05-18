"""Tests for oci MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"OCI_HOST": "localhost"}):
            from src.servers.oci import create_oci_server
            server = create_oci_server()
            assert server is not None
