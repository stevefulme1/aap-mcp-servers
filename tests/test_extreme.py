"""Tests for extreme MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"EXTREME_HOST": "localhost"}):
            from src.servers.extreme import create_extreme_server
            server = create_extreme_server()
            assert server is not None


class TestClient:
    def test_headers_bearer(self):
        with patch.dict("os.environ", {"EXTREME_HOST": "api.extremecloudiq.com", "EXTREME_API_KEY": "tok"}):
            from src.servers.extreme import ExtremeClient
            client = ExtremeClient()
            headers = client._headers()
            assert headers["Authorization"] == "Bearer tok"

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"EXTREME_HOST": "localhost"}):
            from src.servers.extreme import ExtremeClient
            client = ExtremeClient()
            for method in ["list_vlans", "get_interface_status", "list_acls",
                           "get_bgp_neighbors", "get_ospf_neighbors",
                           "list_xiq_devices", "get_switch_facts", "get_stp_status",
                           "list_lag_groups", "get_xiq_alerts", "get_port_statistics"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
