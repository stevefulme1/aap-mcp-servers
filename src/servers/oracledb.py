"""MCP Server for Oracle Database (oracledb driver)."""

import asyncio
import json
import logging
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge

logger = logging.getLogger(__name__)

try:
    import oracledb
    HAS_ORACLEDB = True
except ImportError:
    HAS_ORACLEDB = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class OracleDBClient(BaseClient):
    """Direct client for Oracle Database via python-oracledb.

    Uses thin mode by default (no Oracle Client needed).
    """

    def __init__(self):
        self.host = os.environ.get("ORACLEDB_HOST", "localhost")
        self.port = int(os.environ.get("ORACLEDB_PORT", "1521"))
        self.user = os.environ.get("ORACLEDB_USER", "system")
        self.password = os.environ.get("ORACLEDB_PASSWORD", "")
        self.service = os.environ.get("ORACLEDB_SERVICE", "ORCLPDB1")
        self.api_key = ""  # not used

    def _connect(self):
        if not HAS_ORACLEDB:
            raise RuntimeError("oracledb not installed")
        dsn = f"{self.host}:{self.port}/{self.service}"
        return oracledb.connect(user=self.user, password=self.password, dsn=dsn)

    def _exec(self, sql, params_list=None):
        """Execute read-only SQL, return list of dicts."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                if params_list:
                    cur.execute(sql, params_list)
                else:
                    cur.execute(sql)
                cols = [c[0].lower() for c in cur.description] if cur.description else []
                rows = [dict(zip(cols, row)) for row in cur.fetchall()]
                return rows
        finally:
            conn.close()

    # -- read operations --

    def execute_query(self, params):
        sql = params.get("query", "SELECT 1 FROM DUAL")
        rows = self._exec(sql)
        return {"results": rows, "row_count": len(rows)}

    def list_tablespaces(self, params):
        rows = self._exec("""
            SELECT tablespace_name, status, contents, extent_management,
                   ROUND(SUM(bytes)/1024/1024) AS size_mb
            FROM dba_data_files
            JOIN dba_tablespaces USING (tablespace_name)
            GROUP BY tablespace_name, status, contents, extent_management
            ORDER BY tablespace_name
        """)
        return {"tablespaces": rows}

    def get_dataguard_status(self, params):
        rows = self._exec("""
            SELECT database_role, protection_mode, protection_level,
                   switchover_status, open_mode
            FROM v$database
        """)
        return rows[0] if rows else {"error": "Cannot read Data Guard status"}

    def get_rac_status(self, params):
        rows = self._exec("""
            SELECT inst_id, instance_name, host_name, status, database_status
            FROM gv$instance ORDER BY inst_id
        """)
        return {"instances": rows}

    def get_rman_backup_status(self, params):
        rows = self._exec("""
            SELECT session_key, input_type, status, start_time, end_time,
                   ROUND(output_bytes/1024/1024) AS output_mb
            FROM v$rman_backup_job_details
            WHERE ROWNUM <= 20
            ORDER BY start_time DESC
        """)
        return {"backups": rows}

    def list_pdbs(self, params):
        rows = self._exec("""
            SELECT pdb_id, pdb_name, status, open_mode, con_id
            FROM dba_pdbs ORDER BY pdb_name
        """)
        return {"pdbs": rows}

    def get_awr_report(self, params):
        rows = self._exec("""
            SELECT snap_id, begin_interval_time, end_interval_time
            FROM dba_hist_snapshot
            WHERE ROWNUM <= 10
            ORDER BY snap_id DESC
        """)
        return {"snapshots": rows}

    def get_active_sessions(self, params):
        rows = self._exec("""
            SELECT sid, serial#, username, status, sql_id,
                   event, wait_class, seconds_in_wait
            FROM v$session
            WHERE type = 'USER' AND status = 'ACTIVE'
            ORDER BY seconds_in_wait DESC
        """)
        return {"sessions": rows}

    def get_alert_log(self, params):
        limit = params.get("limit", 50)
        rows = self._exec(f"""
            SELECT originating_timestamp, message_text, message_level
            FROM v$diag_alert_ext
            WHERE ROWNUM <= {limit}
            ORDER BY originating_timestamp DESC
        """)
        return {"alerts": rows}

    def list_users(self, params):
        rows = self._exec("""
            SELECT username, account_status, default_tablespace,
                   created, profile
            FROM dba_users ORDER BY username
        """)
        return {"users": rows}

    def get_audit_trail(self, params):
        rows = self._exec("""
            SELECT username, action_name, obj_name, timestamp, returncode
            FROM dba_audit_trail
            WHERE ROWNUM <= 50
            ORDER BY timestamp DESC
        """)
        return {"audit": rows}


def create_oracledb_server():
    server = Server("mcp-oracledb")
    client = OracleDBClient()
    runner = AnsibleBridge("stevefulme1.oracledb")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="execute_query",
                description="Execute SQL query (read-only)",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "SQL query"}},
                    "required": ["query"],
                },
            ),
            Tool(name="list_tablespaces", description="List tablespaces", inputSchema={"type": "object"}),
            Tool(name="get_dataguard_status", description="Get Data Guard status", inputSchema={"type": "object"}),
            Tool(name="get_rac_status", description="Get RAC cluster status", inputSchema={"type": "object"}),
            Tool(name="get_rman_backup_status", description="Get RMAN backup status", inputSchema={"type": "object"}),
            Tool(name="list_pdbs", description="List pluggable databases", inputSchema={"type": "object"}),
            Tool(name="get_awr_report", description="Generate AWR report", inputSchema={"type": "object"}),
            Tool(name="get_active_sessions", description="Get active sessions", inputSchema={"type": "object"}),
            Tool(name="get_alert_log", description="Get alert log entries", inputSchema={"type": "object", "properties": {"limit": {"type": "integer"}}}),
            Tool(name="list_users", description="List database users", inputSchema={"type": "object"}),
            Tool(name="get_audit_trail", description="Get audit trail", inputSchema={"type": "object"}),
            Tool(name="create_tablespace", description="Create tablespace (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "size": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_user", description="Create database user (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "password": {"type": "string"}, "default_tablespace": {"type": "string"}}, "required": ["name"]}),
            Tool(name="run_rman_backup", description="Run RMAN backup (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}, "type": {"type": "string"}}, "required": ["database"]}),
            Tool(name="switchover_dataguard", description="Switchover Data Guard (via Ansible)", inputSchema={"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}),
            Tool(name="clone_pdb", description="Clone PDB (via Ansible)", inputSchema={"type": "object", "properties": {"source_pdb": {"type": "string"}, "target_pdb": {"type": "string"}}, "required": ["source_pdb", "target_pdb"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "execute_query", "list_tablespaces", "get_dataguard_status",
            "get_rac_status", "get_rman_backup_status", "list_pdbs",
            "get_awr_report", "get_active_sessions", "get_alert_log",
            "list_users", "get_audit_trail",
        }
        write_tools = {"create_tablespace", "create_user", "run_rman_backup", "switchover_dataguard", "clone_pdb"}
        if name in read_tools:
            result = await read_op(client, name, arguments)
        elif name in write_tools:
            result = await write_op(runner, name, arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    return server


def main():
    logging.basicConfig(level=logging.INFO)
    server = create_oracledb_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
