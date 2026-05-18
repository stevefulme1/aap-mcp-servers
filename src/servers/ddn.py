"""MCP Server for DDN Storage."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class DdnClient(BaseClient):
    """Direct API client for DDN Storage."""

    def __init__(self):
        super().__init__("DDN_HOST", "DDN_API_KEY")


def create_ddn_server():
    """Create and configure the DDN Storage MCP server."""
    server = create_server("mcp-ddn")
    client = DdnClient()
    runner = AnsibleBridge("stevefulme1.ddn")

    @server.tool()
    async def list_filesystems(params: dict) -> str:
        """List Lustre filesystems"""
        result = await read_op(client, "list_filesystems", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_filesystem_stats(params: dict) -> str:
        """Get filesystem stats"""
        result = await read_op(client, "get_filesystem_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_osts(params: dict) -> str:
        """List Object Storage Targets"""
        result = await read_op(client, "list_osts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_mdts(params: dict) -> str:
        """List Metadata Targets"""
        result = await read_op(client, "list_mdts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_quotas(params: dict) -> str:
        """List quotas"""
        result = await read_op(client, "list_quotas", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_health(params: dict) -> str:
        """Get cluster health"""
        result = await read_op(client, "get_cluster_health", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_storage_pools(params: dict) -> str:
        """List storage pools"""
        result = await read_op(client, "list_storage_pools", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_performance_metrics(params: dict) -> str:
        """Get performance metrics"""
        result = await read_op(client, "get_performance_metrics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_clients(params: dict) -> str:
        """List connected clients"""
        result = await read_op(client, "list_clients", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_snapshots(params: dict) -> str:
        """List snapshots"""
        result = await read_op(client, "list_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_topology(params: dict) -> str:
        """Get cluster topology"""
        result = await read_op(client, "get_cluster_topology", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_filesystem(params: dict) -> str:
        """Create Lustre filesystem"""
        result = await write_op(runner, "create_filesystem", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_storage_pool(params: dict) -> str:
        """Create storage pool"""
        result = await write_op(runner, "create_storage_pool", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def set_quota(params: dict) -> str:
        """Set quota"""
        result = await write_op(runner, "set_quota", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_snapshot(params: dict) -> str:
        """Create snapshot"""
        result = await write_op(runner, "create_snapshot", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def configure_replication(params: dict) -> str:
        """Configure replication"""
        result = await write_op(runner, "configure_replication", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the DDN Storage MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_ddn_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
