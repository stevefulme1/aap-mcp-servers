"""MCP Server for Oracle Database."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class OracledbClient(BaseClient):
    """Direct API client for Oracle Database."""

    def __init__(self):
        super().__init__("ORACLEDB_HOST", "ORACLEDB_API_KEY")


def create_oracledb_server():
    """Create and configure the Oracle Database MCP server."""
    server = create_server("mcp-oracledb")
    client = OracledbClient()
    runner = AnsibleBridge("stevefulme1.oracledb")

    @server.tool()
    async def execute_query(params: dict) -> str:
        """Execute SQL query (read-only)"""
        result = await read_op(client, "execute_query", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_tablespaces(params: dict) -> str:
        """List tablespaces"""
        result = await read_op(client, "list_tablespaces", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_dataguard_status(params: dict) -> str:
        """Get Data Guard status"""
        result = await read_op(client, "get_dataguard_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_rac_status(params: dict) -> str:
        """Get RAC cluster status"""
        result = await read_op(client, "get_rac_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_rman_backup_status(params: dict) -> str:
        """Get RMAN backup status"""
        result = await read_op(client, "get_rman_backup_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_pdbs(params: dict) -> str:
        """List pluggable databases"""
        result = await read_op(client, "list_pdbs", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_awr_report(params: dict) -> str:
        """Generate AWR report"""
        result = await read_op(client, "get_awr_report", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_active_sessions(params: dict) -> str:
        """Get active sessions"""
        result = await read_op(client, "get_active_sessions", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_alert_log(params: dict) -> str:
        """Get alert log entries"""
        result = await read_op(client, "get_alert_log", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_users(params: dict) -> str:
        """List database users"""
        result = await read_op(client, "list_users", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_audit_trail(params: dict) -> str:
        """Get audit trail"""
        result = await read_op(client, "get_audit_trail", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_tablespace(params: dict) -> str:
        """Create tablespace"""
        result = await write_op(runner, "create_tablespace", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_user(params: dict) -> str:
        """Create database user"""
        result = await write_op(runner, "create_user", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def run_rman_backup(params: dict) -> str:
        """Run RMAN backup"""
        result = await write_op(runner, "run_rman_backup", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def switchover_dataguard(params: dict) -> str:
        """Switchover Data Guard"""
        result = await write_op(runner, "switchover_dataguard", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def clone_pdb(params: dict) -> str:
        """Clone PDB"""
        result = await write_op(runner, "clone_pdb", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Oracle Database MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_oracledb_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
