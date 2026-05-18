"""MCP Server for MCP Server for Datadog."""

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


class DatadogClient(BaseClient):
    """Direct API client for MCP Server for Datadog."""

    def __init__(self):
        super().__init__("DATADOG_HOST", "DATADOG_API_KEY")


def create_datadog_server():
    """Create and configure the MCP server."""
    server = Server("mcp-datadog")
    client = DatadogClient()
    runner = AnsibleBridge("stevefulme1.datadog")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_monitors", description="List Datadog monitors", inputSchema={"type": "object"}),
            Tool(name="get_monitor_details", description="Get monitor details", inputSchema={"type": "object"}),
            Tool(name="query_metrics", description="Query metric timeseries", inputSchema={"type": "object"}),
            Tool(name="list_dashboards", description="List dashboards", inputSchema={"type": "object"}),
            Tool(name="get_slo_status", description="Get SLO status", inputSchema={"type": "object"}),
            Tool(name="search_events", description="Search events", inputSchema={"type": "object"}),
            Tool(name="list_synthetics", description="List Synthetic tests", inputSchema={"type": "object"}),
            Tool(name="get_host_tags", description="Get host tags", inputSchema={"type": "object"}),
            Tool(name="list_incidents", description="List incidents", inputSchema={"type": "object"}),
            Tool(name="get_downtime_schedule", description="Get downtime schedule", inputSchema={"type": "object"}),
            Tool(name="create_monitor", description="Create a monitor", inputSchema={"type": "object"}),
            Tool(name="create_dashboard", description="Create a dashboard", inputSchema={"type": "object"}),
            Tool(name="create_slo", description="Create an SLO", inputSchema={"type": "object"}),
            Tool(name="schedule_downtime", description="Schedule a downtime", inputSchema={"type": "object"}),
            Tool(name="mute_monitor", description="Mute a monitor", inputSchema={"type": "object"}),
            Tool(name="create_incident", description="Create an incident", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_monitors":
            result = await read_op(client, "list_monitors", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_monitor_details":
            result = await read_op(client, "get_monitor_details", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "query_metrics":
            result = await read_op(client, "query_metrics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_dashboards":
            result = await read_op(client, "list_dashboards", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_slo_status":
            result = await read_op(client, "get_slo_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "search_events":
            result = await read_op(client, "search_events", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_synthetics":
            result = await read_op(client, "list_synthetics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_host_tags":
            result = await read_op(client, "get_host_tags", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_incidents":
            result = await read_op(client, "list_incidents", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_downtime_schedule":
            result = await read_op(client, "get_downtime_schedule", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_monitor":
            result = await write_op(runner, "create_monitor", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_dashboard":
            result = await write_op(runner, "create_dashboard", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_slo":
            result = await write_op(runner, "create_slo", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "schedule_downtime":
            result = await write_op(runner, "schedule_downtime", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "mute_monitor":
            result = await write_op(runner, "mute_monitor", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_incident":
            result = await write_op(runner, "create_incident", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_datadog_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
