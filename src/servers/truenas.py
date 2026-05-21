"""MCP Server for TrueNAS storage platform."""

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
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class TrueNASClient(BaseClient):
    """Direct API client for TrueNAS.

    Uses Bearer token auth.  Base URL: http(s)://{host}/api/v2.0
    """

    def __init__(self):
        self.host = os.environ.get("TRUENAS_HOST", "localhost")
        self.api_key = os.environ.get("TRUENAS_API_KEY", "")
        self.scheme = os.environ.get("TRUENAS_SCHEME", "http")
        self.verify_ssl = os.environ.get("TRUENAS_VERIFY_SSL", "false").lower() == "true"

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _tn_get(self, path, params=None):
        url = f"{self.scheme}://{self.host}/api/v2.0{path}"
        resp = requests.get(url, headers=self._headers(), params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def list_pools(self, params):
        return self._tn_get("/pool")

    def list_datasets(self, params):
        return self._tn_get("/pool/dataset")

    def list_snapshots(self, params):
        return self._tn_get("/zfs/snapshot")

    def list_smb_shares(self, params):
        return self._tn_get("/sharing/smb")

    def list_nfs_shares(self, params):
        return self._tn_get("/sharing/nfs")

    def list_iscsi_targets(self, params):
        return self._tn_get("/iscsi/target")

    def get_system_info(self, params):
        return self._tn_get("/system/info")

    def list_replication_tasks(self, params):
        return self._tn_get("/replication")

    def list_users(self, params):
        return self._tn_get("/user")

    def get_alerts(self, params):
        return self._tn_get("/alert/list")

    def get_pool_status(self, params):
        pool_id = params.get("id", "")
        if pool_id:
            return self._tn_get(f"/pool/id/{pool_id}")
        return self._tn_get("/pool")


def create_truenas_server():
    server = Server("mcp-truenas")
    client = TrueNASClient()
    runner = AnsibleBridge("stevefulme1.truenas")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_pools", description="List ZFS pools", inputSchema={"type": "object"}),
            Tool(name="list_datasets", description="List datasets", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="list_smb_shares", description="List SMB shares", inputSchema={"type": "object"}),
            Tool(name="list_nfs_shares", description="List NFS shares", inputSchema={"type": "object"}),
            Tool(name="list_iscsi_targets", description="List iSCSI targets", inputSchema={"type": "object"}),
            Tool(name="get_system_info", description="Get system information", inputSchema={"type": "object"}),
            Tool(name="list_replication_tasks", description="List replication tasks", inputSchema={"type": "object"}),
            Tool(name="list_users", description="List users", inputSchema={"type": "object"}),
            Tool(name="get_alerts", description="Get active alerts", inputSchema={"type": "object"}),
            Tool(
                name="get_pool_status",
                description="Get detailed pool status",
                inputSchema={
                    "type": "object",
                    "properties": {"id": {"type": "string", "description": "Pool ID"}},
                },
            ),
            Tool(name="create_dataset", description="Create ZFS dataset (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_snapshot", description="Create snapshot (via Ansible)", inputSchema={"type": "object", "properties": {"dataset": {"type": "string"}, "name": {"type": "string"}}, "required": ["dataset", "name"]}),
            Tool(name="create_smb_share", description="Create SMB share (via Ansible)", inputSchema={"type": "object", "properties": {"path": {"type": "string"}, "name": {"type": "string"}}, "required": ["path", "name"]}),
            Tool(name="create_nfs_share", description="Create NFS share (via Ansible)", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
            Tool(name="configure_replication", description="Configure replication (via Ansible)", inputSchema={"type": "object", "properties": {"source_dataset": {"type": "string"}, "target_dataset": {"type": "string"}}, "required": ["source_dataset", "target_dataset"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_pools", "list_datasets", "list_snapshots", "list_smb_shares",
            "list_nfs_shares", "list_iscsi_targets", "get_system_info",
            "list_replication_tasks", "list_users", "get_alerts", "get_pool_status",
        }
        write_tools = {"create_dataset", "create_snapshot", "create_smb_share", "create_nfs_share", "configure_replication"}
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
    server = create_truenas_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
