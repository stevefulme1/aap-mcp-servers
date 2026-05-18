"""MCP Server for VAST Data."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class VastdataClient(BaseClient):
    """Direct API client for VAST Data."""

    def __init__(self):
        super().__init__("VASTDATA_HOST", "VASTDATA_API_KEY")


def create_vastdata_server():
    """Create and configure the VAST Data MCP server."""
    server = create_server("mcp-vastdata")
    client = VastdataClient()
    runner = AnsibleBridge("stevefulme1.vastdata")

    @server.tool()
    async def list_clusters(params: dict) -> str:
        """List VAST clusters"""
        result = await read_op(client, "list_clusters", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_stats(params: dict) -> str:
        """Get cluster statistics"""
        result = await read_op(client, "get_cluster_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_views(params: dict) -> str:
        """List views (exports)"""
        result = await read_op(client, "list_views", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_quotas(params: dict) -> str:
        """List quotas"""
        result = await read_op(client, "list_quotas", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_snapshots(params: dict) -> str:
        """List snapshots"""
        result = await read_op(client, "list_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_users(params: dict) -> str:
        """List users"""
        result = await read_op(client, "list_users", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_capacity(params: dict) -> str:
        """Get capacity summary"""
        result = await read_op(client, "get_capacity", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_protection_policies(params: dict) -> str:
        """List protection policies"""
        result = await read_op(client, "list_protection_policies", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_s3_policies(params: dict) -> str:
        """List S3 lifecycle policies"""
        result = await read_op(client, "list_s3_policies", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_audit_log(params: dict) -> str:
        """Get audit log"""
        result = await read_op(client, "get_audit_log", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_overview(params: dict) -> str:
        """Get cluster overview"""
        result = await read_op(client, "get_cluster_overview", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_view(params: dict) -> str:
        """Create a view"""
        result = await write_op(runner, "create_view", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_quota(params: dict) -> str:
        """Create quota"""
        result = await write_op(runner, "create_quota", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_snapshot(params: dict) -> str:
        """Create snapshot"""
        result = await write_op(runner, "create_snapshot", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_protection_policy(params: dict) -> str:
        """Create protection policy"""
        result = await write_op(runner, "create_protection_policy", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_user(params: dict) -> str:
        """Create user"""
        result = await write_op(runner, "create_user", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the VAST Data MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_vastdata_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
