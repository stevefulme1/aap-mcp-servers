"""MCP Server for MCP Server for VAST Data."""

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


class VastdataClient(BaseClient):
    """Direct API client for MCP Server for VAST Data."""

    def __init__(self):
        super().__init__("VASTDATA_HOST", "VASTDATA_API_KEY")


def create_vastdata_server():
    """Create and configure the MCP server."""
    server = Server("mcp-vastdata")
    client = VastdataClient()
    runner = AnsibleBridge("stevefulme1.vastdata")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_clusters", description="List VAST clusters", inputSchema={"type": "object"}),
            Tool(name="get_cluster_stats", description="Get cluster statistics", inputSchema={"type": "object"}),
            Tool(name="list_views", description="List views (exports)", inputSchema={"type": "object"}),
            Tool(name="list_quotas", description="List quotas", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="list_users", description="List users", inputSchema={"type": "object"}),
            Tool(name="get_capacity", description="Get capacity summary", inputSchema={"type": "object"}),
            Tool(
                name="list_protection_policies",
                description="List protection policies",
                inputSchema={"type": "object"},
            ),
            Tool(name="list_s3_policies", description="List S3 lifecycle policies", inputSchema={"type": "object"}),
            Tool(name="get_audit_log", description="Get audit log", inputSchema={"type": "object"}),
            Tool(name="get_cluster_overview", description="Get cluster overview", inputSchema={"type": "object"}),
            Tool(name="create_view", description="Create a view", inputSchema={"type": "object"}),
            Tool(name="create_quota", description="Create quota", inputSchema={"type": "object"}),
            Tool(name="create_snapshot", description="Create snapshot", inputSchema={"type": "object"}),
            Tool(
                name="create_protection_policy",
                description="Create protection policy",
                inputSchema={"type": "object"},
            ),
            Tool(name="create_user", description="Create user", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_clusters":
            result = await read_op(client, "list_clusters", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_stats":
            result = await read_op(client, "get_cluster_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_views":
            result = await read_op(client, "list_views", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_quotas":
            result = await read_op(client, "list_quotas", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_snapshots":
            result = await read_op(client, "list_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_users":
            result = await read_op(client, "list_users", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_capacity":
            result = await read_op(client, "get_capacity", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_protection_policies":
            result = await read_op(client, "list_protection_policies", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_s3_policies":
            result = await read_op(client, "list_s3_policies", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_audit_log":
            result = await read_op(client, "get_audit_log", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_overview":
            result = await read_op(client, "get_cluster_overview", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_view":
            result = await write_op(runner, "create_view", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_quota":
            result = await write_op(runner, "create_quota", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_snapshot":
            result = await write_op(runner, "create_snapshot", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_protection_policy":
            result = await write_op(runner, "create_protection_policy", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_user":
            result = await write_op(runner, "create_user", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_vastdata_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
