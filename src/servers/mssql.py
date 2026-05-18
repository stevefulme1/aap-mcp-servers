"""MCP Server for MCP Server for Microsoft SQL Server."""

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


class MssqlClient(BaseClient):
    """Direct API client for MCP Server for Microsoft SQL Server."""

    def __init__(self):
        super().__init__("MSSQL_HOST", "MSSQL_API_KEY")


def create_mssql_server():
    """Create and configure the MCP server."""
    server = Server("mcp-mssql")
    client = MssqlClient()
    runner = AnsibleBridge("stevefulme1.mssql")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="execute_query", description="Execute T-SQL query (read-only)", inputSchema={"type": "object"}),
            Tool(name="list_databases", description="List databases", inputSchema={"type": "object"}),
            Tool(name="get_database_info", description="Get database details", inputSchema={"type": "object"}),
            Tool(name="get_ag_status", description="Get Always On AG status", inputSchema={"type": "object"}),
            Tool(name="get_agent_jobs", description="List SQL Agent jobs", inputSchema={"type": "object"}),
            Tool(name="get_logins", description="List server logins", inputSchema={"type": "object"}),
            Tool(name="get_tde_status", description="Get TDE encryption status", inputSchema={"type": "object"}),
            Tool(name="get_backup_history", description="Get backup history", inputSchema={"type": "object"}),
            Tool(name="get_wait_stats", description="Get wait statistics", inputSchema={"type": "object"}),
            Tool(name="get_blocking_queries", description="Get blocking queries", inputSchema={"type": "object"}),
            Tool(name="get_azure_sql_metrics", description="Get Azure SQL metrics", inputSchema={"type": "object"}),
            Tool(name="create_database", description="Create database", inputSchema={"type": "object"}),
            Tool(name="create_login", description="Create server login", inputSchema={"type": "object"}),
            Tool(name="run_agent_job", description="Run SQL Agent job", inputSchema={"type": "object"}),
            Tool(name="configure_tde", description="Configure TDE encryption", inputSchema={"type": "object"}),
            Tool(name="backup_database", description="Backup database", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "execute_query":
            result = await read_op(client, "execute_query", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_databases":
            result = await read_op(client, "list_databases", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_database_info":
            result = await read_op(client, "get_database_info", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_ag_status":
            result = await read_op(client, "get_ag_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_agent_jobs":
            result = await read_op(client, "get_agent_jobs", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_logins":
            result = await read_op(client, "get_logins", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_tde_status":
            result = await read_op(client, "get_tde_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_backup_history":
            result = await read_op(client, "get_backup_history", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_wait_stats":
            result = await read_op(client, "get_wait_stats", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_blocking_queries":
            result = await read_op(client, "get_blocking_queries", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_azure_sql_metrics":
            result = await read_op(client, "get_azure_sql_metrics", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_database":
            result = await write_op(runner, "create_database", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_login":
            result = await write_op(runner, "create_login", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "run_agent_job":
            result = await write_op(runner, "run_agent_job", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "configure_tde":
            result = await write_op(runner, "configure_tde", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "backup_database":
            result = await write_op(runner, "backup_database", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_mssql_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
