"""MCP Server for MCP Server for New Relic."""

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


class NewrelicClient(BaseClient):
    """Direct API client for MCP Server for New Relic."""

    def __init__(self):
        super().__init__("NEWRELIC_HOST", "NEWRELIC_API_KEY")


def create_newrelic_server():
    """Create and configure the MCP server."""
    server = Server("mcp-newrelic")
    client = NewrelicClient()
    runner = AnsibleBridge("stevefulme1.newrelic")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="nrql_query", description="Run NRQL query", inputSchema={"type": "object"}),
            Tool(name="list_alert_policies", description="List alert policies", inputSchema={"type": "object"}),
            Tool(name="get_alert_violations", description="Get alert violations", inputSchema={"type": "object"}),
            Tool(name="list_dashboards", description="List dashboards", inputSchema={"type": "object"}),
            Tool(name="get_entity_details", description="Get entity details", inputSchema={"type": "object"}),
            Tool(name="list_synthetics", description="List Synthetic monitors", inputSchema={"type": "object"}),
            Tool(name="get_sli_status", description="Get SLI/SLO status", inputSchema={"type": "object"}),
            Tool(name="list_workloads", description="List workloads", inputSchema={"type": "object"}),
            Tool(name="get_apm_summary", description="Get APM summary", inputSchema={"type": "object"}),
            Tool(name="get_infra_hosts", description="List infrastructure hosts", inputSchema={"type": "object"}),
            Tool(name="create_alert_policy", description="Create alert policy", inputSchema={"type": "object"}),
            Tool(name="create_alert_condition", description="Create alert condition", inputSchema={"type": "object"}),
            Tool(name="create_dashboard", description="Create dashboard", inputSchema={"type": "object"}),
            Tool(
                name="create_synthetic_monitor",
                description="Create Synthetic monitor",
                inputSchema={"type": "object"},
            ),
            Tool(name="create_workload", description="Create workload", inputSchema={"type": "object"}),
            Tool(name="tag_entity", description="Tag an entity", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "nrql_query":
            result = await read_op(client, "nrql_query", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_alert_policies":
            result = await read_op(client, "list_alert_policies", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_alert_violations":
            result = await read_op(client, "get_alert_violations", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_dashboards":
            result = await read_op(client, "list_dashboards", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_entity_details":
            result = await read_op(client, "get_entity_details", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_synthetics":
            result = await read_op(client, "list_synthetics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_sli_status":
            result = await read_op(client, "get_sli_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_workloads":
            result = await read_op(client, "list_workloads", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_apm_summary":
            result = await read_op(client, "get_apm_summary", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_infra_hosts":
            result = await read_op(client, "get_infra_hosts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_alert_policy":
            result = await write_op(runner, "create_alert_policy", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_alert_condition":
            result = await write_op(runner, "create_alert_condition", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_dashboard":
            result = await write_op(runner, "create_dashboard", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_synthetic_monitor":
            result = await write_op(runner, "create_synthetic_monitor", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_workload":
            result = await write_op(runner, "create_workload", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "tag_entity":
            result = await write_op(runner, "tag_entity", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_newrelic_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
