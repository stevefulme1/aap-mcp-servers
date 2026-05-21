"""Tests for mssql MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"MSSQL_HOST": "localhost"}):
            from src.servers.mssql import create_mssql_server
            server = create_mssql_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"MSSQL_HOST": "localhost"}):
            from src.servers.mssql import MSSQLClient
            client = MSSQLClient()
            for method in ["execute_query", "list_databases", "get_database_info",
                           "get_ag_status", "get_agent_jobs", "get_logins",
                           "get_tde_status", "get_backup_history", "get_wait_stats",
                           "get_blocking_queries", "get_azure_sql_metrics"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
