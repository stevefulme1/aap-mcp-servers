"""MCP Server for MCP Server for Oracle Database."""

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


class OracledbClient(BaseClient):
    """Direct API client for MCP Server for Oracle Database."""

    def __init__(self):
        super().__init__("ORACLEDB_HOST", "ORACLEDB_API_KEY")


def create_oracledb_server():
    """Create and configure the MCP server."""
    server = Server("mcp-oracledb")
    client = OracledbClient()
    runner = AnsibleBridge("stevefulme1.oracledb")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="execute_query", description="Execute SQL query (read-only)", inputSchema={"type": "object"}),
            Tool(name="list_tablespaces", description="List tablespaces", inputSchema={"type": "object"}),
            Tool(name="get_dataguard_status", description="Get Data Guard status", inputSchema={"type": "object"}),
            Tool(name="get_rac_status", description="Get RAC cluster status", inputSchema={"type": "object"}),
            Tool(name="get_rman_backup_status", description="Get RMAN backup status", inputSchema={"type": "object"}),
            Tool(name="list_pdbs", description="List pluggable databases", inputSchema={"type": "object"}),
            Tool(name="get_awr_report", description="Generate AWR report", inputSchema={"type": "object"}),
            Tool(name="get_active_sessions", description="Get active sessions", inputSchema={"type": "object"}),
            Tool(name="get_alert_log", description="Get alert log entries", inputSchema={"type": "object"}),
            Tool(name="list_users", description="List database users", inputSchema={"type": "object"}),
            Tool(name="get_audit_trail", description="Get audit trail", inputSchema={"type": "object"}),
            Tool(name="create_tablespace", description="Create tablespace", inputSchema={"type": "object"}),
            Tool(name="create_user", description="Create database user", inputSchema={"type": "object"}),
            Tool(name="run_rman_backup", description="Run RMAN backup", inputSchema={"type": "object"}),
            Tool(name="switchover_dataguard", description="Switchover Data Guard", inputSchema={"type": "object"}),
            Tool(name="clone_pdb", description="Clone PDB", inputSchema={"type": "object"}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "execute_query":
            result = await read_op(client, "execute_query", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_tablespaces":
            result = await read_op(client, "list_tablespaces", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_dataguard_status":
            result = await read_op(client, "get_dataguard_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_rac_status":
            result = await read_op(client, "get_rac_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_rman_backup_status":
            result = await read_op(client, "get_rman_backup_status", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_pdbs":
            result = await read_op(client, "list_pdbs", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_awr_report":
            result = await read_op(client, "get_awr_report", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_active_sessions":
            result = await read_op(client, "get_active_sessions", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_alert_log":
            result = await read_op(client, "get_alert_log", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "list_users":
            result = await read_op(client, "list_users", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "get_audit_trail":
            result = await read_op(client, "get_audit_trail", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_tablespace":
            result = await write_op(runner, "create_tablespace", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "create_user":
            result = await write_op(runner, "create_user", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "run_rman_backup":
            result = await write_op(runner, "run_rman_backup", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "switchover_dataguard":
            result = await write_op(runner, "switchover_dataguard", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        if name == "clone_pdb":
            result = await write_op(runner, "clone_pdb", arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_oracledb_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
