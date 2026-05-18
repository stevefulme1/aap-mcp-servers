"""MCP Server for MCP Server for Extreme Networks."""

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


class ExtremeClient(BaseClient):
    """Direct API client for MCP Server for Extreme Networks."""

    def __init__(self):
        super().__init__("EXTREME_HOST", "EXTREME_API_KEY")


def create_extreme_server():
    """Create and configure the MCP server."""
    server = Server("mcp-extreme")
    client = ExtremeClient()
    runner = AnsibleBridge("stevefulme1.extreme")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_vlans", description="List VLANs", inputSchema={"type": "object"}),
            Tool(name="get_interface_status", description="Get interface status", inputSchema={"type": "object"}),
            Tool(name="list_acls", description="List access control lists", inputSchema={"type": "object"}),
            Tool(name="get_bgp_neighbors", description="Get BGP neighbors", inputSchema={"type": "object"}),
            Tool(name="get_ospf_neighbors", description="Get OSPF neighbors", inputSchema={"type": "object"}),
            Tool(name="list_xiq_devices", description="List ExtremeCloud IQ devices", inputSchema={"type": "object"}),
            Tool(name="get_switch_facts", description="Get switch facts", inputSchema={"type": "object"}),
            Tool(name="get_stp_status", description="Get STP status", inputSchema={"type": "object"}),
            Tool(name="list_lag_groups", description="List LAG groups", inputSchema={"type": "object"}),
            Tool(name="get_xiq_alerts", description="Get ExtremeCloud IQ alerts", inputSchema={"type": "object"}),
            Tool(name="get_port_statistics", description="Get port statistics", inputSchema={"type": "object"}),
            Tool(name="create_vlan", description="Create VLAN", inputSchema={"type": "object"}),
            Tool(name="create_acl", description="Create ACL", inputSchema={"type": "object"}),
            Tool(name="configure_bgp_neighbor", description="Configure BGP neighbor", inputSchema={"type": "object"}),
            Tool(name="apply_firmware", description="Apply firmware update", inputSchema={"type": "object"}),
            Tool(name="backup_config", description="Backup switch config", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_vlans":
            result = await read_op(client, "list_vlans", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_interface_status":
            result = await read_op(client, "get_interface_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_acls":
            result = await read_op(client, "list_acls", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_bgp_neighbors":
            result = await read_op(client, "get_bgp_neighbors", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_ospf_neighbors":
            result = await read_op(client, "get_ospf_neighbors", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_xiq_devices":
            result = await read_op(client, "list_xiq_devices", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_switch_facts":
            result = await read_op(client, "get_switch_facts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_stp_status":
            result = await read_op(client, "get_stp_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_lag_groups":
            result = await read_op(client, "list_lag_groups", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_xiq_alerts":
            result = await read_op(client, "get_xiq_alerts", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_port_statistics":
            result = await read_op(client, "get_port_statistics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_vlan":
            result = await write_op(runner, "create_vlan", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_acl":
            result = await write_op(runner, "create_acl", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "configure_bgp_neighbor":
            result = await write_op(runner, "configure_bgp_neighbor", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "apply_firmware":
            result = await write_op(runner, "apply_firmware", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "backup_config":
            result = await write_op(runner, "backup_config", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_extreme_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
