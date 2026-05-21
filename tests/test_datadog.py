"""Tests for datadog MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"DATADOG_HOST": "localhost"}):
            from src.servers.datadog import create_datadog_server
            server = create_datadog_server()
            assert server is not None


class TestClient:
    def test_headers_use_dd_keys(self):
        with patch.dict("os.environ", {"DATADOG_HOST": "api.datadoghq.com", "DATADOG_API_KEY": "aaa", "DATADOG_APP_KEY": "bbb"}):
            from src.servers.datadog import DatadogClient
            client = DatadogClient()
            headers = client._headers()
            assert headers["DD-API-KEY"] == "aaa"
            assert headers["DD-APPLICATION-KEY"] == "bbb"
            assert "Authorization" not in headers

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"DATADOG_HOST": "localhost"}):
            from src.servers.datadog import DatadogClient
            client = DatadogClient()
            for method in ["list_monitors", "get_monitor_details", "query_metrics",
                           "list_dashboards", "get_slo_status", "search_events",
                           "list_synthetics", "get_host_tags", "list_incidents",
                           "get_downtime_schedule"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
