"""MCP Server for MCP Server for MongoDB."""

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


class MongodbClient(BaseClient):
    """Direct API client for MCP Server for MongoDB."""

    def __init__(self):
        super().__init__("MONGODB_HOST", "MONGODB_API_KEY")


def create_mongodb_server():
    """Create and configure the MCP server."""
    server = Server("mcp-mongodb")
    client = MongodbClient()
    runner = AnsibleBridge("stevefulme1.mongodb")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="query_collection", description="Query a MongoDB collection", inputSchema={"type": "object"}),
            Tool(name="list_databases", description="List all databases", inputSchema={"type": "object"}),
            Tool(name="list_collections", description="List collections in a database", inputSchema={"type": "object"}),
            Tool(name="get_indexes", description="Get indexes for a collection", inputSchema={"type": "object"}),
            Tool(name="get_replication_status", description="Get replica set status", inputSchema={"type": "object"}),
            Tool(name="get_cluster_stats", description="Get cluster statistics", inputSchema={"type": "object"}),
            Tool(name="get_user_list", description="List database users", inputSchema={"type": "object"}),
            Tool(name="aggregate", description="Run aggregation pipeline", inputSchema={"type": "object"}),
            Tool(name="explain_query", description="Explain query execution plan", inputSchema={"type": "object"}),
            Tool(name="get_atlas_clusters", description="List Atlas clusters", inputSchema={"type": "object"}),
            Tool(name="get_atlas_alerts", description="Get Atlas alerts", inputSchema={"type": "object"}),
            Tool(
                name="get_atlas_backup_snapshots",
                description="List Atlas backup snapshots",
                inputSchema={"type": "object"},
            ),
            Tool(name="create_index", description="Create an index", inputSchema={"type": "object"}),
            Tool(name="create_user", description="Create a database user", inputSchema={"type": "object"}),
            Tool(name="drop_collection", description="Drop a collection", inputSchema={"type": "object"}),
            Tool(
                name="configure_atlas_backup",
                description="Configure Atlas backup schedule",
                inputSchema={"type": "object"},
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "query_collection":
            result = await read_op(client, "query_collection", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_databases":
            result = await read_op(client, "list_databases", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_collections":
            result = await read_op(client, "list_collections", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_indexes":
            result = await read_op(client, "get_indexes", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_replication_status":
            result = await read_op(client, "get_replication_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_stats":
            result = await read_op(client, "get_cluster_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_user_list":
            result = await read_op(client, "get_user_list", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "aggregate":
            result = await read_op(client, "aggregate", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "explain_query":
            result = await read_op(client, "explain_query", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_atlas_clusters":
            result = await read_op(client, "get_atlas_clusters", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_atlas_alerts":
            result = await read_op(client, "get_atlas_alerts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_atlas_backup_snapshots":
            result = await read_op(client, "get_atlas_backup_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_index":
            result = await write_op(runner, "create_index", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_user":
            result = await write_op(runner, "create_user", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "drop_collection":
            result = await write_op(runner, "drop_collection", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "configure_atlas_backup":
            result = await write_op(runner, "configure_atlas_backup", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_mongodb_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
