"""MCP Server for WekaIO Storage."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class WekaClient(BaseClient):
    """Direct API client for WekaIO Storage."""

    def __init__(self):
        super().__init__("WEKA_HOST", "WEKA_API_KEY")


def create_weka_server():
    """Create and configure the WekaIO Storage MCP server."""
    server = create_server("mcp-weka")
    client = WekaClient()
    runner = AnsibleBridge("stevefulme1.weka")

    @server.tool()
    async def list_filesystems(params: dict) -> str:
        """List Weka filesystems"""
        result = await read_op(client, "list_filesystems", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_filesystem_stats(params: dict) -> str:
        """Get filesystem statistics"""
        result = await read_op(client, "get_filesystem_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_quotas(params: dict) -> str:
        """List filesystem quotas"""
        result = await read_op(client, "list_quotas", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_snapshots(params: dict) -> str:
        """List snapshots"""
        result = await read_op(client, "list_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_status(params: dict) -> str:
        """Get Weka cluster status"""
        result = await read_op(client, "get_cluster_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_nfs_exports(params: dict) -> str:
        """List NFS exports"""
        result = await read_op(client, "list_nfs_exports", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_s3_buckets(params: dict) -> str:
        """List S3-compatible buckets"""
        result = await read_op(client, "list_s3_buckets", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_tiering_status(params: dict) -> str:
        """Get tiering status"""
        result = await read_op(client, "get_tiering_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_drives(params: dict) -> str:
        """List cluster drives"""
        result = await read_op(client, "list_drives", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_events(params: dict) -> str:
        """Get recent events"""
        result = await read_op(client, "get_events", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_containers(params: dict) -> str:
        """List containers"""
        result = await read_op(client, "list_containers", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_filesystem(params: dict) -> str:
        """Create a filesystem"""
        result = await write_op(runner, "create_filesystem", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_snapshot(params: dict) -> str:
        """Create a snapshot"""
        result = await write_op(runner, "create_snapshot", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def set_quota(params: dict) -> str:
        """Set filesystem quota"""
        result = await write_op(runner, "set_quota", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_nfs_export(params: dict) -> str:
        """Create NFS export"""
        result = await write_op(runner, "create_nfs_export", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_s3_bucket(params: dict) -> str:
        """Create S3 bucket"""
        result = await write_op(runner, "create_s3_bucket", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the WekaIO Storage MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_weka_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
