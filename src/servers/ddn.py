"""MCP Server for MCP Server for DDN Storage."""

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


class DdnClient(BaseClient):
    """Direct API client for MCP Server for DDN Storage."""

    def __init__(self):
        super().__init__("DDN_HOST", "DDN_API_KEY")


def create_ddn_server():
    """Create and configure the MCP server."""
    server = Server("mcp-ddn")
    client = DdnClient()
    runner = AnsibleBridge("stevefulme1.ddn")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_filesystems", description="List Lustre filesystems", inputSchema={"type": "object"}),
            Tool(name="get_filesystem_stats", description="Get filesystem stats", inputSchema={"type": "object"}),
            Tool(name="list_osts", description="List Object Storage Targets", inputSchema={"type": "object"}),
            Tool(name="list_mdts", description="List Metadata Targets", inputSchema={"type": "object"}),
            Tool(name="list_quotas", description="List quotas", inputSchema={"type": "object"}),
            Tool(name="get_cluster_health", description="Get cluster health", inputSchema={"type": "object"}),
            Tool(name="list_storage_pools", description="List storage pools", inputSchema={"type": "object"}),
            Tool(name="get_performance_metrics", description="Get performance metrics", inputSchema={"type": "object"}),
            Tool(name="list_clients", description="List connected clients", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="get_cluster_topology", description="Get cluster topology", inputSchema={"type": "object"}),
            Tool(name="create_filesystem", description="Create Lustre filesystem", inputSchema={"type": "object"}),
            Tool(name="create_storage_pool", description="Create storage pool", inputSchema={"type": "object"}),
            Tool(name="set_quota", description="Set quota", inputSchema={"type": "object"}),
            Tool(name="create_snapshot", description="Create snapshot", inputSchema={"type": "object"}),
            Tool(name="configure_replication", description="Configure replication", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_filesystems":
            result = await read_op(client, "list_filesystems", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_filesystem_stats":
            result = await read_op(client, "get_filesystem_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_osts":
            result = await read_op(client, "list_osts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_mdts":
            result = await read_op(client, "list_mdts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_quotas":
            result = await read_op(client, "list_quotas", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_health":
            result = await read_op(client, "get_cluster_health", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_storage_pools":
            result = await read_op(client, "list_storage_pools", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_performance_metrics":
            result = await read_op(client, "get_performance_metrics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_clients":
            result = await read_op(client, "list_clients", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_snapshots":
            result = await read_op(client, "list_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_topology":
            result = await read_op(client, "get_cluster_topology", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_filesystem":
            result = await write_op(runner, "create_filesystem", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_storage_pool":
            result = await write_op(runner, "create_storage_pool", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "set_quota":
            result = await write_op(runner, "set_quota", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_snapshot":
            result = await write_op(runner, "create_snapshot", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "configure_replication":
            result = await write_op(runner, "configure_replication", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_ddn_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
