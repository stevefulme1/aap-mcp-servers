"""MCP Server for MCP Server for TrueNAS."""

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge

logger = logging.getLogger(__name__)


async def read_op(client, operation, params):
    """Execute a read operation (direct API)."""
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    """Execute a write operation (through Ansible)."""
    return await runner.execute(operation, params)


class TruenasClient(BaseClient):
    """Direct API client for MCP Server for TrueNAS."""

    def __init__(self):
        super().__init__("TRUENAS_HOST", "TRUENAS_API_KEY")


def create_truenas_server():
    """Create and configure the MCP server."""
    server = Server("mcp-truenas")
    client = TruenasClient()
    runner = AnsibleBridge("stevefulme1.truenas")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_pools", description="List ZFS pools", inputSchema={"type": "object"}),
            Tool(name="list_datasets", description="List datasets", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="list_smb_shares", description="List SMB shares", inputSchema={"type": "object"}),
            Tool(name="list_nfs_shares", description="List NFS shares", inputSchema={"type": "object"}),
            Tool(name="list_iscsi_targets", description="List iSCSI targets", inputSchema={"type": "object"}),
            Tool(name="get_system_info", description="Get system information", inputSchema={"type": "object"}),
            Tool(name="list_replication_tasks", description="List replication tasks", inputSchema={"type": "object"}),
            Tool(name="list_users", description="List users", inputSchema={"type": "object"}),
            Tool(name="get_alerts", description="Get active alerts", inputSchema={"type": "object"}),
            Tool(name="get_pool_status", description="Get detailed pool status", inputSchema={"type": "object"}),
            Tool(name="create_dataset", description="Create ZFS dataset", inputSchema={"type": "object"}),
            Tool(name="create_snapshot", description="Create snapshot", inputSchema={"type": "object"}),
            Tool(name="create_smb_share", description="Create SMB share", inputSchema={"type": "object"}),
            Tool(name="create_nfs_share", description="Create NFS share", inputSchema={"type": "object"}),
            Tool(name="configure_replication", description="Configure replication", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_pools":
            result = await read_op(client, "list_pools", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_datasets":
            result = await read_op(client, "list_datasets", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_snapshots":
            result = await read_op(client, "list_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_smb_shares":
            result = await read_op(client, "list_smb_shares", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_nfs_shares":
            result = await read_op(client, "list_nfs_shares", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_iscsi_targets":
            result = await read_op(client, "list_iscsi_targets", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_system_info":
            result = await read_op(client, "get_system_info", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_replication_tasks":
            result = await read_op(client, "list_replication_tasks", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_users":
            result = await read_op(client, "list_users", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_alerts":
            result = await read_op(client, "get_alerts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_pool_status":
            result = await read_op(client, "get_pool_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_dataset":
            result = await write_op(runner, "create_dataset", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_snapshot":
            result = await write_op(runner, "create_snapshot", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_smb_share":
            result = await write_op(runner, "create_smb_share", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_nfs_share":
            result = await write_op(runner, "create_nfs_share", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "configure_replication":
            result = await write_op(runner, "configure_replication", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_truenas_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
