"""Tests for weka MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"WEKA_HOST": "localhost"}):
            from src.servers.weka import create_weka_server
            server = create_weka_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"WEKA_HOST": "localhost"}):
            from src.servers.weka import WekaClient
            client = WekaClient()
            for method in ["list_filesystems", "get_filesystem_stats", "list_quotas",
                           "list_snapshots", "get_cluster_status", "list_nfs_exports",
                           "list_s3_buckets", "get_tiering_status", "list_drives",
                           "get_events", "list_containers"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
