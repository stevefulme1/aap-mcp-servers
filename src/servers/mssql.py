"""MCP Server for Microsoft SQL Server (pymssql driver)."""

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
    import pymssql
    HAS_PYMSSQL = True
except ImportError:
    HAS_PYMSSQL = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class MSSQLClient(BaseClient):
    """Direct client for Microsoft SQL Server via pymssql.

    Not REST-based -- uses pymssql for T-SQL queries.
    """

    def __init__(self):
        self.host = os.environ.get("MSSQL_HOST", "localhost")
        self.port = int(os.environ.get("MSSQL_PORT", "1433"))
        self.user = os.environ.get("MSSQL_USER", "sa")
        self.password = os.environ.get("MSSQL_PASSWORD", "")
        self.database = os.environ.get("MSSQL_DATABASE", "master")
        self.api_key = ""  # not used

    def _connect(self, database=None):
        if not HAS_PYMSSQL:
            raise RuntimeError("pymssql not installed")
        return pymssql.connect(
            server=self.host, port=self.port,
            user=self.user, password=self.password,
            database=database or self.database,
            as_dict=True,
        )

    def _exec(self, sql, database=None):
        """Execute read-only SQL and return rows."""
        conn = self._connect(database)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        finally:
            conn.close()

    # -- read operations --

    def execute_query(self, params):
        sql = params.get("query", "SELECT 1 AS ok")
        db = params.get("database")
        rows = self._exec(sql, database=db)
        return {"results": rows, "row_count": len(rows)}

    def list_databases(self, params):
        rows = self._exec("SELECT name, state_desc, recovery_model_desc FROM sys.databases ORDER BY name")
        return {"databases": rows}

    def get_database_info(self, params):
        db = params.get("database", self.database)
        rows = self._exec(f"""
            SELECT name, state_desc, recovery_model_desc,
                   CAST(SUM(size)*8/1024 AS INT) AS size_mb
            FROM sys.databases d
            JOIN sys.master_files f ON d.database_id = f.database_id
            WHERE d.name = '{db}'
            GROUP BY d.name, d.state_desc, d.recovery_model_desc
        """)
        return rows[0] if rows else {"error": "Database not found"}

    def get_ag_status(self, params):
        rows = self._exec("""
            SELECT ag.name AS ag_name, ags.primary_replica,
                   ar.replica_server_name, ars.role_desc,
                   ars.synchronization_health_desc
            FROM sys.availability_groups ag
            JOIN sys.dm_hadr_availability_group_states ags ON ag.group_id = ags.group_id
            JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
            JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id
        """)
        return {"availability_groups": rows}

    def get_agent_jobs(self, params):
        rows = self._exec("""
            SELECT j.name, j.enabled, jh.run_status, jh.run_date, jh.run_time
            FROM msdb.dbo.sysjobs j
            LEFT JOIN (
                SELECT job_id, run_status, run_date, run_time,
                       ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY run_date DESC, run_time DESC) rn
                FROM msdb.dbo.sysjobhistory WHERE step_id = 0
            ) jh ON j.job_id = jh.job_id AND jh.rn = 1
            ORDER BY j.name
        """)
        return {"jobs": rows}

    def get_logins(self, params):
        rows = self._exec("SELECT name, type_desc, is_disabled, create_date FROM sys.server_principals WHERE type IN ('S','U','G') ORDER BY name")
        return {"logins": rows}

    def get_tde_status(self, params):
        rows = self._exec("""
            SELECT d.name, dek.encryption_state, dek.key_algorithm, dek.key_length
            FROM sys.dm_database_encryption_keys dek
            JOIN sys.databases d ON dek.database_id = d.database_id
        """)
        return {"tde_databases": rows}

    def get_backup_history(self, params):
        db = params.get("database", "")
        where = f"WHERE database_name = '{db}'" if db else ""
        rows = self._exec(f"""
            SELECT TOP 20 database_name, type, backup_start_date, backup_finish_date,
                   CAST(backup_size/1024/1024 AS INT) AS size_mb
            FROM msdb.dbo.backupset {where}
            ORDER BY backup_finish_date DESC
        """)
        return {"backups": rows}

    def get_wait_stats(self, params):
        rows = self._exec("""
            SELECT TOP 20 wait_type,
                   waiting_tasks_count,
                   wait_time_ms,
                   signal_wait_time_ms
            FROM sys.dm_os_wait_stats
            WHERE wait_type NOT LIKE '%SLEEP%'
            ORDER BY wait_time_ms DESC
        """)
        return {"wait_stats": rows}

    def get_blocking_queries(self, params):
        rows = self._exec("""
            SELECT r.session_id, r.blocking_session_id, r.wait_type,
                   r.wait_time, t.text AS query_text
            FROM sys.dm_exec_requests r
            CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
            WHERE r.blocking_session_id <> 0
        """)
        return {"blocking": rows}

    def get_azure_sql_metrics(self, params):
        """Get Azure SQL DTU/CPU metrics (only works on Azure SQL DB)."""
        rows = self._exec("""
            SELECT TOP 20 end_time, avg_cpu_percent, avg_data_io_percent,
                   avg_log_write_percent, avg_memory_usage_percent
            FROM sys.dm_db_resource_stats
            ORDER BY end_time DESC
        """)
        return {"metrics": rows}


def create_mssql_server():
    server = Server("mcp-mssql")
    client = MSSQLClient()
    runner = AnsibleBridge("stevefulme1.mssql")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="execute_query",
                description="Execute T-SQL query (read-only)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "T-SQL query to execute"},
                        "database": {"type": "string", "description": "Database to connect to"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(name="list_databases", description="List databases", inputSchema={"type": "object"}),
            Tool(name="get_database_info", description="Get database details", inputSchema={"type": "object", "properties": {"database": {"type": "string"}}, "required": ["database"]}),
            Tool(name="get_ag_status", description="Get Always On AG status", inputSchema={"type": "object"}),
            Tool(name="get_agent_jobs", description="List SQL Agent jobs", inputSchema={"type": "object"}),
            Tool(name="get_logins", description="List server logins", inputSchema={"type": "object"}),
            Tool(name="get_tde_status", description="Get TDE encryption status", inputSchema={"type": "object"}),
            Tool(name="get_backup_history", description="Get backup history", inputSchema={"type": "object", "properties": {"database": {"type": "string"}}}),
            Tool(name="get_wait_stats", description="Get wait statistics", inputSchema={"type": "object"}),
            Tool(name="get_blocking_queries", description="Get blocking queries", inputSchema={"type": "object"}),
            Tool(name="get_azure_sql_metrics", description="Get Azure SQL metrics", inputSchema={"type": "object"}),
            Tool(name="create_database", description="Create database (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_login", description="Create server login (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "password": {"type": "string"}}, "required": ["name"]}),
            Tool(name="run_agent_job", description="Run SQL Agent job (via Ansible)", inputSchema={"type": "object", "properties": {"job_name": {"type": "string"}}, "required": ["job_name"]}),
            Tool(name="configure_tde", description="Configure TDE encryption (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}}, "required": ["database"]}),
            Tool(name="backup_database", description="Backup database (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}, "path": {"type": "string"}}, "required": ["database"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "execute_query", "list_databases", "get_database_info",
            "get_ag_status", "get_agent_jobs", "get_logins", "get_tde_status",
            "get_backup_history", "get_wait_stats", "get_blocking_queries",
            "get_azure_sql_metrics",
        }
        write_tools = {"create_database", "create_login", "run_agent_job", "configure_tde", "backup_database"}
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
    server = create_mssql_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
