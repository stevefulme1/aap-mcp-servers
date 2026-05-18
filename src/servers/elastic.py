"""MCP Server for MCP Server for Elastic Stack."""

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


class ElasticClient(BaseClient):
    """Direct API client for MCP Server for Elastic Stack."""

    def __init__(self):
        super().__init__("ELASTIC_HOST", "ELASTIC_API_KEY")


def create_elastic_server():
    """Create and configure the MCP server."""
    server = Server("mcp-elastic")
    client = ElasticClient()
    runner = AnsibleBridge("stevefulme1.elastic")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="search", description="Search documents across indices", inputSchema={"type": "object"}),
            Tool(
                name="get_cluster_health",
                description="Get Elasticsearch cluster health",
                inputSchema={"type": "object"},
            ),
            Tool(
                name="list_indices",
                description="List indices with size and doc count",
                inputSchema={"type": "object"},
            ),
            Tool(name="get_ilm_policy", description="Get ILM policy details", inputSchema={"type": "object"}),
            Tool(name="get_index_stats", description="Get index statistics", inputSchema={"type": "object"}),
            Tool(name="get_node_stats", description="Get cluster node statistics", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List available snapshots", inputSchema={"type": "object"}),
            Tool(name="get_watcher_alerts", description="Get recent Watcher alerts", inputSchema={"type": "object"}),
            Tool(name="list_fleet_agents", description="List Fleet managed agents", inputSchema={"type": "object"}),
            Tool(name="get_kibana_dashboards", description="List Kibana dashboards", inputSchema={"type": "object"}),
            Tool(name="search_logs", description="Search logs with KQL", inputSchema={"type": "object"}),
            Tool(name="create_index", description="Create an Elasticsearch index", inputSchema={"type": "object"}),
            Tool(name="create_ilm_policy", description="Create an ILM policy", inputSchema={"type": "object"}),
            Tool(name="create_snapshot", description="Create a snapshot", inputSchema={"type": "object"}),
            Tool(name="import_dashboard", description="Import a Kibana dashboard", inputSchema={"type": "object"}),
            Tool(name="manage_fleet_policy", description="Manage Fleet agent policy", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "search":
            result = await read_op(client, "search", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_cluster_health":
            result = await read_op(client, "get_cluster_health", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_indices":
            result = await read_op(client, "list_indices", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_ilm_policy":
            result = await read_op(client, "get_ilm_policy", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_index_stats":
            result = await read_op(client, "get_index_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_node_stats":
            result = await read_op(client, "get_node_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_snapshots":
            result = await read_op(client, "list_snapshots", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_watcher_alerts":
            result = await read_op(client, "get_watcher_alerts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_fleet_agents":
            result = await read_op(client, "list_fleet_agents", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_kibana_dashboards":
            result = await read_op(client, "get_kibana_dashboards", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "search_logs":
            result = await read_op(client, "search_logs", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_index":
            result = await write_op(runner, "create_index", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_ilm_policy":
            result = await write_op(runner, "create_ilm_policy", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_snapshot":
            result = await write_op(runner, "create_snapshot", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "import_dashboard":
            result = await write_op(runner, "import_dashboard", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "manage_fleet_policy":
            result = await write_op(runner, "manage_fleet_policy", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_elastic_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
