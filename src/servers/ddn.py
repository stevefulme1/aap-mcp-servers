"""MCP Server for DDN Storage (Lustre/EXAScaler)."""

import asyncio
import json
import logging
import os
from base64 import b64encode

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


class DDNClient(BaseClient):
    """Direct API client for DDN Storage.

    Uses Basic auth.  Base URL: https://{host}/api/v2
    """

    def __init__(self):
        self.host = os.environ.get("DDN_HOST", "localhost")
        self.api_key = os.environ.get("DDN_API_KEY", "")
        self.username = os.environ.get("DDN_USER", "admin")
        self.password = os.environ.get("DDN_PASSWORD", "")
        self.verify_ssl = os.environ.get("DDN_VERIFY_SSL", "true").lower() == "true"

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.username and self.password:
            cred = b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _ddn_get(self, path, params=None):
        url = f"https://{self.host}/api/v2{path}"
        resp = requests.get(url, headers=self._headers(), params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def list_filesystems(self, params):
        return self._ddn_get("/filesystem")

    def get_filesystem_stats(self, params):
        fs_name = params.get("name", "")
        if fs_name:
            return self._ddn_get(f"/filesystem/{fs_name}/stats")
        return self._ddn_get("/filesystem/stats")

    def list_osts(self, params):
        return self._ddn_get("/ost")

    def list_mdts(self, params):
        return self._ddn_get("/mdt")

    def list_quotas(self, params):
        return self._ddn_get("/quota")

    def get_cluster_health(self, params):
        return self._ddn_get("/cluster/health")

    def list_storage_pools(self, params):
        return self._ddn_get("/pool")

    def get_performance_metrics(self, params):
        return self._ddn_get("/metrics/performance")

    def list_clients(self, params):
        return self._ddn_get("/client")

    def list_snapshots(self, params):
        return self._ddn_get("/snapshot")

    def get_cluster_topology(self, params):
        return self._ddn_get("/cluster/topology")


def create_ddn_server():
    server = Server("mcp-ddn")
    client = DDNClient()
    runner = AnsibleBridge("stevefulme1.ddn")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_filesystems", description="List Lustre filesystems", inputSchema={"type": "object"}),
            Tool(name="get_filesystem_stats", description="Get filesystem stats", inputSchema={"type": "object", "properties": {"name": {"type": "string", "description": "Filesystem name"}}}),
            Tool(name="list_osts", description="List Object Storage Targets", inputSchema={"type": "object"}),
            Tool(name="list_mdts", description="List Metadata Targets", inputSchema={"type": "object"}),
            Tool(name="list_quotas", description="List quotas", inputSchema={"type": "object"}),
            Tool(name="get_cluster_health", description="Get cluster health", inputSchema={"type": "object"}),
            Tool(name="list_storage_pools", description="List storage pools", inputSchema={"type": "object"}),
            Tool(name="get_performance_metrics", description="Get performance metrics", inputSchema={"type": "object"}),
            Tool(name="list_clients", description="List connected clients", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="get_cluster_topology", description="Get cluster topology", inputSchema={"type": "object"}),
            Tool(name="create_filesystem", description="Create Lustre filesystem (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_storage_pool", description="Create storage pool (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            Tool(name="set_quota", description="Set quota (via Ansible)", inputSchema={"type": "object", "properties": {"filesystem": {"type": "string"}, "user": {"type": "string"}, "limit": {"type": "string"}}, "required": ["filesystem"]}),
            Tool(name="create_snapshot", description="Create snapshot (via Ansible)", inputSchema={"type": "object", "properties": {"filesystem": {"type": "string"}, "name": {"type": "string"}}, "required": ["filesystem", "name"]}),
            Tool(name="configure_replication", description="Configure replication (via Ansible)", inputSchema={"type": "object", "properties": {"source": {"type": "string"}, "target": {"type": "string"}}, "required": ["source", "target"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_filesystems", "get_filesystem_stats", "list_osts",
            "list_mdts", "list_quotas", "get_cluster_health",
            "list_storage_pools", "get_performance_metrics", "list_clients",
            "list_snapshots", "get_cluster_topology",
        }
        write_tools = {"create_filesystem", "create_storage_pool", "set_quota", "create_snapshot", "configure_replication"}
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
    server = create_ddn_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
