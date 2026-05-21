"""Tests for newrelic MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"NEWRELIC_HOST": "localhost"}):
            from src.servers.newrelic import create_newrelic_server
            server = create_newrelic_server()
            assert server is not None


class TestClient:
    def test_headers_use_api_key(self):
        with patch.dict("os.environ", {"NEWRELIC_HOST": "api.newrelic.com", "NEWRELIC_API_KEY": "NRAK-xxx"}):
            from src.servers.newrelic import NewRelicClient
            client = NewRelicClient()
            headers = client._headers()
            assert headers["API-Key"] == "NRAK-xxx"

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"NEWRELIC_HOST": "localhost"}):
            from src.servers.newrelic import NewRelicClient
            client = NewRelicClient()
            for method in ["nrql_query", "list_alert_policies", "get_alert_violations",
                           "list_dashboards", "get_entity_details", "list_synthetics",
                           "get_sli_status", "list_workloads", "get_apm_summary",
                           "get_infra_hosts"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
