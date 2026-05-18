"""MCP Server for MCP Server for Oracle Cloud Infrastructure."""

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


class OciClient(BaseClient):
    """Direct API client for MCP Server for Oracle Cloud Infrastructure."""

    def __init__(self):
        super().__init__("OCI_HOST", "OCI_API_KEY")


def create_oci_server():
    """Create and configure the MCP server."""
    server = Server("mcp-oci")
    client = OciClient()
    runner = AnsibleBridge("stevefulme1.oci")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_instances", description="List compute instances", inputSchema={"type": "object"}),
            Tool(name="list_vcns", description="List VCNs", inputSchema={"type": "object"}),
            Tool(name="list_subnets", description="List subnets", inputSchema={"type": "object"}),
            Tool(name="list_databases", description="List databases", inputSchema={"type": "object"}),
            Tool(name="list_buckets", description="List Object Storage buckets", inputSchema={"type": "object"}),
            Tool(name="list_load_balancers", description="List load balancers", inputSchema={"type": "object"}),
            Tool(name="get_compartment_usage", description="Get compartment usage", inputSchema={"type": "object"}),
            Tool(name="list_security_lists", description="List security lists", inputSchema={"type": "object"}),
            Tool(name="list_block_volumes", description="List block volumes", inputSchema={"type": "object"}),
            Tool(
                name="get_availability_domains",
                description="Get availability domains",
                inputSchema={"type": "object"},
            ),
            Tool(name="get_limits", description="Get service limits", inputSchema={"type": "object"}),
            Tool(name="create_instance", description="Create compute instance", inputSchema={"type": "object"}),
            Tool(name="create_vcn", description="Create VCN", inputSchema={"type": "object"}),
            Tool(name="create_bucket", description="Create Object Storage bucket", inputSchema={"type": "object"}),
            Tool(name="create_database", description="Create database", inputSchema={"type": "object"}),
            Tool(name="manage_security_list", description="Manage security list rules", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_instances":
            result = await read_op(client, "list_instances", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_vcns":
            result = await read_op(client, "list_vcns", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_subnets":
            result = await read_op(client, "list_subnets", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_databases":
            result = await read_op(client, "list_databases", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_buckets":
            result = await read_op(client, "list_buckets", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_load_balancers":
            result = await read_op(client, "list_load_balancers", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_compartment_usage":
            result = await read_op(client, "get_compartment_usage", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_security_lists":
            result = await read_op(client, "list_security_lists", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_block_volumes":
            result = await read_op(client, "list_block_volumes", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_availability_domains":
            result = await read_op(client, "get_availability_domains", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_limits":
            result = await read_op(client, "get_limits", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_instance":
            result = await write_op(runner, "create_instance", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_vcn":
            result = await write_op(runner, "create_vcn", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_bucket":
            result = await write_op(runner, "create_bucket", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_database":
            result = await write_op(runner, "create_database", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "manage_security_list":
            result = await write_op(runner, "manage_security_list", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_oci_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
