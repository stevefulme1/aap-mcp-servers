"""MCP Server for CoreWeave GPU Cloud."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class CoreweaveClient(BaseClient):
    """Direct API client for CoreWeave GPU Cloud."""

    def __init__(self):
        super().__init__("COREWEAVE_HOST", "COREWEAVE_API_KEY")


def create_coreweave_server():
    """Create and configure the CoreWeave GPU Cloud MCP server."""
    server = create_server("mcp-coreweave")
    client = CoreweaveClient()
    runner = AnsibleBridge("stevefulme1.coreweave")

    @server.tool()
    async def list_virtual_servers(params: dict) -> str:
        """List virtual servers"""
        result = await read_op(client, "list_virtual_servers", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_gpu_availability(params: dict) -> str:
        """Check GPU availability by type"""
        result = await read_op(client, "get_gpu_availability", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_inference_services(params: dict) -> str:
        """List inference services"""
        result = await read_op(client, "list_inference_services", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_vpcs(params: dict) -> str:
        """List VPCs"""
        result = await read_op(client, "list_vpcs", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_storage_volumes(params: dict) -> str:
        """List storage volumes"""
        result = await read_op(client, "list_storage_volumes", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_node_pools(params: dict) -> str:
        """List node pools"""
        result = await read_op(client, "list_node_pools", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_workload_metrics(params: dict) -> str:
        """Get workload metrics"""
        result = await read_op(client, "get_workload_metrics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_namespaces(params: dict) -> str:
        """List namespaces"""
        result = await read_op(client, "list_namespaces", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_jobs(params: dict) -> str:
        """List running jobs"""
        result = await read_op(client, "list_jobs", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_billing_summary(params: dict) -> str:
        """Get billing summary"""
        result = await read_op(client, "get_billing_summary", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_gpu_inventory(params: dict) -> str:
        """Get full GPU inventory"""
        result = await read_op(client, "get_gpu_inventory", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_virtual_server(params: dict) -> str:
        """Create a virtual server"""
        result = await write_op(runner, "create_virtual_server", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def deploy_inference_service(params: dict) -> str:
        """Deploy an inference service"""
        result = await write_op(runner, "deploy_inference_service", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_vpc(params: dict) -> str:
        """Create a VPC"""
        result = await write_op(runner, "create_vpc", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_storage_volume(params: dict) -> str:
        """Create storage volume"""
        result = await write_op(runner, "create_storage_volume", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def scale_workload(params: dict) -> str:
        """Scale a workload"""
        result = await write_op(runner, "scale_workload", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the CoreWeave GPU Cloud MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_coreweave_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
