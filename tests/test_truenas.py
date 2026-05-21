"""Tests for truenas MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"TRUENAS_HOST": "localhost"}):
            from src.servers.truenas import create_truenas_server
            server = create_truenas_server()
            assert server is not None


class TestClient:
    def test_headers_bearer(self):
        with patch.dict("os.environ", {"TRUENAS_HOST": "nas.local", "TRUENAS_API_KEY": "tok123"}):
            from src.servers.truenas import TrueNASClient
            client = TrueNASClient()
            headers = client._headers()
            assert headers["Authorization"] == "Bearer tok123"

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"TRUENAS_HOST": "localhost"}):
            from src.servers.truenas import TrueNASClient
            client = TrueNASClient()
            for method in ["list_pools", "list_datasets", "list_snapshots",
                           "list_smb_shares", "list_nfs_shares", "list_iscsi_targets",
                           "get_system_info", "list_replication_tasks", "list_users",
                           "get_alerts", "get_pool_status"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
