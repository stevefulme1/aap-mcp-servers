"""Tests for coreweave MCP server."""
from unittest.mock import patch


class TestServer:
    def test_server_creates(self):
        with patch.dict("os.environ", {"COREWEAVE_HOST": "localhost"}):
            from src.servers.coreweave import create_coreweave_server
            server = create_coreweave_server()
            assert server is not None


class TestClient:
    def test_client_has_read_methods(self):
        with patch.dict("os.environ", {"COREWEAVE_HOST": "localhost"}):
            from src.servers.coreweave import CoreWeaveClient
            client = CoreWeaveClient()
            for method in ["list_virtual_servers", "get_gpu_availability",
                           "list_inference_services", "list_vpcs",
                           "list_storage_volumes", "list_node_pools",
                           "get_workload_metrics", "list_namespaces",
                           "list_jobs", "get_billing_summary", "get_gpu_inventory"]:
                assert callable(getattr(client, method, None)), f"Missing method: {method}"
