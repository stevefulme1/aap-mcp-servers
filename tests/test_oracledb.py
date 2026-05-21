"""Tests for oracledb MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"ORACLEDB_HOST": "localhost"}):
            from src.servers.oracledb import create_oracledb_server
            server = create_oracledb_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"ORACLEDB_HOST": "localhost"}):
            from src.servers.oracledb import OracleDBClient
            client = OracleDBClient()
            for method in ["execute_query", "list_tablespaces", "get_dataguard_status",
                           "get_rac_status", "get_rman_backup_status", "list_pdbs",
                           "get_awr_report", "get_active_sessions", "get_alert_log",
                           "list_users", "get_audit_trail"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
