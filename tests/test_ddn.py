"""Tests for ddn MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"DDN_HOST": "localhost"}):
            from src.servers.ddn import create_ddn_server
            server = create_ddn_server()
            assert server is not None


class TestClient:
    def test_headers_basic_auth(self):
        with patch.dict("os.environ", {"DDN_HOST": "ddn.local", "DDN_USER": "admin", "DDN_PASSWORD": "secret"}):
            from src.servers.ddn import DDNClient
            client = DDNClient()
            headers = client._headers()
            assert headers["Authorization"].startswith("Basic ")

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"DDN_HOST": "localhost"}):
            from src.servers.ddn import DDNClient
            client = DDNClient()
            for method in ["list_filesystems", "get_filesystem_stats", "list_osts",
                           "list_mdts", "list_quotas", "get_cluster_health",
                           "list_storage_pools", "get_performance_metrics",
                           "list_clients", "list_snapshots", "get_cluster_topology"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
