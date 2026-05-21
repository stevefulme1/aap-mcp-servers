"""Tests for elastic MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"ELASTIC_HOST": "localhost"}):
            from src.servers.elastic import create_elastic_server
            server = create_elastic_server()
            assert server is not None


class TestClient:
    def test_headers_basic_auth(self):
        with patch.dict("os.environ", {"ELASTIC_HOST": "es.local", "ELASTIC_USER": "elastic", "ELASTIC_PASSWORD": "pass123"}):
            from src.servers.elastic import ElasticClient
            client = ElasticClient()
            headers = client._headers()
            assert headers["Authorization"].startswith("Basic ")

    def test_headers_api_key(self):
        with patch.dict("os.environ", {"ELASTIC_HOST": "es.local", "ELASTIC_API_KEY": "myapikey"}):
            from src.servers.elastic import ElasticClient
            client = ElasticClient()
            headers = client._headers()
            assert headers["Authorization"] == "ApiKey myapikey"

    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"ELASTIC_HOST": "localhost"}):
            from src.servers.elastic import ElasticClient
            client = ElasticClient()
            for method in ["search", "get_cluster_health", "list_indices",
                           "get_ilm_policy", "get_index_stats", "get_node_stats",
                           "list_snapshots", "get_watcher_alerts", "list_fleet_agents",
                           "get_kibana_dashboards", "search_logs"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
