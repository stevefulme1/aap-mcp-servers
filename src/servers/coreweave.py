"""MCP Server for MCP Server for CoreWeave GPU Cloud."""

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


class CoreweaveClient(BaseClient):
    """Direct API client for MCP Server for CoreWeave GPU Cloud."""

    def __init__(self):
        super().__init__("COREWEAVE_HOST", "COREWEAVE_API_KEY")


def create_coreweave_server():
    """Create and configure the MCP server."""
    server = Server("mcp-coreweave")
    client = CoreweaveClient()
    runner = AnsibleBridge("stevefulme1.coreweave")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_virtual_servers", description="List virtual servers", inputSchema={"type": "object"}),
            Tool(
                name="get_gpu_availability",
                description="Check GPU availability by type",
                inputSchema={"type": "object"},
            ),
            Tool(name="list_inference_services", description="List inference services", inputSchema={"type": "object"}),
            Tool(name="list_vpcs", description="List VPCs", inputSchema={"type": "object"}),
            Tool(name="list_storage_volumes", description="List storage volumes", inputSchema={"type": "object"}),
            Tool(name="list_node_pools", description="List node pools", inputSchema={"type": "object"}),
            Tool(name="get_workload_metrics", description="Get workload metrics", inputSchema={"type": "object"}),
            Tool(name="list_namespaces", description="List namespaces", inputSchema={"type": "object"}),
            Tool(name="list_jobs", description="List running jobs", inputSchema={"type": "object"}),
            Tool(name="get_billing_summary", description="Get billing summary", inputSchema={"type": "object"}),
            Tool(name="get_gpu_inventory", description="Get full GPU inventory", inputSchema={"type": "object"}),
            Tool(name="create_virtual_server", description="Create a virtual server", inputSchema={"type": "object"}),
            Tool(
                name="deploy_inference_service",
                description="Deploy an inference service",
                inputSchema={"type": "object"},
            ),
            Tool(name="create_vpc", description="Create a VPC", inputSchema={"type": "object"}),
            Tool(name="create_storage_volume", description="Create storage volume", inputSchema={"type": "object"}),
            Tool(name="scale_workload", description="Scale a workload", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "list_virtual_servers":
            result = await read_op(client, "list_virtual_servers", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_gpu_availability":
            result = await read_op(client, "get_gpu_availability", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_inference_services":
            result = await read_op(client, "list_inference_services", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_vpcs":
            result = await read_op(client, "list_vpcs", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_storage_volumes":
            result = await read_op(client, "list_storage_volumes", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_node_pools":
            result = await read_op(client, "list_node_pools", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_workload_metrics":
            result = await read_op(client, "get_workload_metrics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_namespaces":
            result = await read_op(client, "list_namespaces", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_jobs":
            result = await read_op(client, "list_jobs", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_billing_summary":
            result = await read_op(client, "get_billing_summary", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_gpu_inventory":
            result = await read_op(client, "get_gpu_inventory", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_virtual_server":
            result = await write_op(runner, "create_virtual_server", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "deploy_inference_service":
            result = await write_op(runner, "deploy_inference_service", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_vpc":
            result = await write_op(runner, "create_vpc", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_storage_volume":
            result = await write_op(runner, "create_storage_volume", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "scale_workload":
            result = await write_op(runner, "scale_workload", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_coreweave_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
