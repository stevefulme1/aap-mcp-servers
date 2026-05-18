"""MCP Server for MCP Server for WekaIO Storage."""

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


class WekaClient(BaseClient):
    """Direct API client for MCP Server for WekaIO Storage."""

    def __init__(self):
        super().__init__("WEKA_HOST", "WEKA_API_KEY")


def create_weka_server():
    """Create and configure the MCP server."""
    server = Server("mcp-weka")
    client = WekaClient()
    runner = AnsibleBridge("stevefulme1.weka")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_filesystems", description="List Weka filesystems", inputSchema={"type": "object"}),
            Tool(name="get_filesystem_stats", description="Get filesystem statistics", inputSchema={"type": "object"}),
            Tool(name="list_quotas", description="List filesystem quotas", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="get_cluster_status", description="Get Weka cluster status", inputSchema={"type": "object"}),
            Tool(name="list_nfs_exports", description="List NFS exports", inputSchema={"type": "object"}),
            Tool(name="list_s3_buckets", description="List S3-compatible buckets", inputSchema={"type": "object"}),
            Tool(name="get_tiering_status", description="Get tiering status", inputSchema={"type": "object"}),
            Tool(name="list_drives", description="List cluster drives", inputSchema={"type": "object"}),
            Tool(name="get_events", description="Get recent events", inputSchema={"type": "object"}),
            Tool(name="list_containers", description="List containers", inputSchema={"type": "object"}),
            Tool(name="create_filesystem", description="Create a filesystem", inputSchema={"type": "object"}),
            Tool(name="create_snapshot", description="Create a snapshot", inputSchema={"type": "object"}),
            Tool(name="set_quota", description="Set filesystem quota", inputSchema={"type": "object"}),
            Tool(name="create_nfs_export", description="Create NFS export", inputSchema={"type": "object"}),
            Tool(name="create_s3_bucket", description="Create S3 bucket", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_filesystems":
            result = await read_op(client, "list_filesystems", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_filesystem_stats":
            result = await read_op(client, "get_filesystem_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_quotas":
            result = await read_op(client, "list_quotas", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_snapshots":
            result = await read_op(client, "list_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_status":
            result = await read_op(client, "get_cluster_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_nfs_exports":
            result = await read_op(client, "list_nfs_exports", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_s3_buckets":
            result = await read_op(client, "list_s3_buckets", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_tiering_status":
            result = await read_op(client, "get_tiering_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_drives":
            result = await read_op(client, "list_drives", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_events":
            result = await read_op(client, "get_events", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_containers":
            result = await read_op(client, "list_containers", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_filesystem":
            result = await write_op(runner, "create_filesystem", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_snapshot":
            result = await write_op(runner, "create_snapshot", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "set_quota":
            result = await write_op(runner, "set_quota", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_nfs_export":
            result = await write_op(runner, "create_nfs_export", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_s3_bucket":
            result = await write_op(runner, "create_s3_bucket", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_weka_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
