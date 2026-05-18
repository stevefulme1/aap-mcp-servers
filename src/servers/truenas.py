"""MCP Server for TrueNAS."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class TruenasClient(BaseClient):
    """Direct API client for TrueNAS."""

    def __init__(self):
        super().__init__("TRUENAS_HOST", "TRUENAS_API_KEY")


def create_truenas_server():
    """Create and configure the TrueNAS MCP server."""
    server = create_server("mcp-truenas")
    client = TruenasClient()
    runner = AnsibleBridge("stevefulme1.truenas")

    @server.tool()
    async def list_pools(params: dict) -> str:
        """List ZFS pools"""
        result = await read_op(client, "list_pools", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_datasets(params: dict) -> str:
        """List datasets"""
        result = await read_op(client, "list_datasets", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_snapshots(params: dict) -> str:
        """List snapshots"""
        result = await read_op(client, "list_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_smb_shares(params: dict) -> str:
        """List SMB shares"""
        result = await read_op(client, "list_smb_shares", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_nfs_shares(params: dict) -> str:
        """List NFS shares"""
        result = await read_op(client, "list_nfs_shares", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_iscsi_targets(params: dict) -> str:
        """List iSCSI targets"""
        result = await read_op(client, "list_iscsi_targets", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_system_info(params: dict) -> str:
        """Get system information"""
        result = await read_op(client, "get_system_info", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_replication_tasks(params: dict) -> str:
        """List replication tasks"""
        result = await read_op(client, "list_replication_tasks", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_users(params: dict) -> str:
        """List users"""
        result = await read_op(client, "list_users", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_alerts(params: dict) -> str:
        """Get active alerts"""
        result = await read_op(client, "get_alerts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_pool_status(params: dict) -> str:
        """Get detailed pool status"""
        result = await read_op(client, "get_pool_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_dataset(params: dict) -> str:
        """Create ZFS dataset"""
        result = await write_op(runner, "create_dataset", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_snapshot(params: dict) -> str:
        """Create snapshot"""
        result = await write_op(runner, "create_snapshot", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_smb_share(params: dict) -> str:
        """Create SMB share"""
        result = await write_op(runner, "create_smb_share", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_nfs_share(params: dict) -> str:
        """Create NFS share"""
        result = await write_op(runner, "create_nfs_share", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def configure_replication(params: dict) -> str:
        """Configure replication"""
        result = await write_op(runner, "configure_replication", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the TrueNAS MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_truenas_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
