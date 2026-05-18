"""MCP Server for Microsoft SQL Server."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class MssqlClient(BaseClient):
    """Direct API client for Microsoft SQL Server."""

    def __init__(self):
        super().__init__("MSSQL_HOST", "MSSQL_API_KEY")


def create_mssql_server():
    """Create and configure the Microsoft SQL Server MCP server."""
    server = create_server("mcp-mssql")
    client = MssqlClient()
    runner = AnsibleBridge("stevefulme1.mssql")

    @server.tool()
    async def execute_query(params: dict) -> str:
        """Execute T-SQL query (read-only)"""
        result = await read_op(client, "execute_query", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_databases(params: dict) -> str:
        """List databases"""
        result = await read_op(client, "list_databases", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_database_info(params: dict) -> str:
        """Get database details"""
        result = await read_op(client, "get_database_info", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_ag_status(params: dict) -> str:
        """Get Always On AG status"""
        result = await read_op(client, "get_ag_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_agent_jobs(params: dict) -> str:
        """List SQL Agent jobs"""
        result = await read_op(client, "get_agent_jobs", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_logins(params: dict) -> str:
        """List server logins"""
        result = await read_op(client, "get_logins", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_tde_status(params: dict) -> str:
        """Get TDE encryption status"""
        result = await read_op(client, "get_tde_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_backup_history(params: dict) -> str:
        """Get backup history"""
        result = await read_op(client, "get_backup_history", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_wait_stats(params: dict) -> str:
        """Get wait statistics"""
        result = await read_op(client, "get_wait_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_blocking_queries(params: dict) -> str:
        """Get blocking queries"""
        result = await read_op(client, "get_blocking_queries", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_azure_sql_metrics(params: dict) -> str:
        """Get Azure SQL metrics"""
        result = await read_op(client, "get_azure_sql_metrics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_database(params: dict) -> str:
        """Create database"""
        result = await write_op(runner, "create_database", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_login(params: dict) -> str:
        """Create server login"""
        result = await write_op(runner, "create_login", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def run_agent_job(params: dict) -> str:
        """Run SQL Agent job"""
        result = await write_op(runner, "run_agent_job", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def configure_tde(params: dict) -> str:
        """Configure TDE encryption"""
        result = await write_op(runner, "configure_tde", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def backup_database(params: dict) -> str:
        """Backup database"""
        result = await write_op(runner, "backup_database", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Microsoft SQL Server MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_mssql_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
