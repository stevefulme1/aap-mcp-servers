"""Tests for mongodb MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"MONGODB_HOST": "localhost"}):
            from src.servers.mongodb import create_mongodb_server
            server = create_mongodb_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"MONGODB_HOST": "localhost"}):
            from src.servers.mongodb import MongoDBClient
            client = MongoDBClient()
            for method in ["query_collection", "list_databases", "list_collections",
                           "get_indexes", "get_replication_status", "get_cluster_stats",
                           "get_user_list", "aggregate", "explain_query",
                           "get_atlas_clusters", "get_atlas_alerts", "get_atlas_backup_snapshots"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
