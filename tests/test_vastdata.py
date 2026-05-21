"""Tests for vastdata MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"VASTDATA_HOST": "localhost"}):
            from src.servers.vastdata import create_vastdata_server
            server = create_vastdata_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"VASTDATA_HOST": "localhost"}):
            from src.servers.vastdata import VastDataClient
            client = VastDataClient()
            for method in ["list_clusters", "get_cluster_stats", "list_views",
                           "list_quotas", "list_snapshots", "list_users",
                           "get_capacity", "list_protection_policies",
                           "list_s3_policies", "get_audit_log", "get_cluster_overview"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
