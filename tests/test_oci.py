"""Tests for oci MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"OCI_HOST": "localhost"}):
            from src.servers.oci import create_oci_server
            server = create_oci_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"OCI_HOST": "localhost"}):
            from src.servers.oci import OCIClient
            client = OCIClient()
            for method in ["list_instances", "list_vcns", "list_subnets",
                           "list_databases", "list_buckets", "list_load_balancers",
                           "get_compartment_usage", "list_security_lists",
                           "list_block_volumes", "get_availability_domains", "get_limits"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
