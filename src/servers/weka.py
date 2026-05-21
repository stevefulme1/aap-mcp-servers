"""MCP Server for WekaIO Storage."""

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


class WekaClient(BaseClient):
    """Direct API client for Weka.

    Uses Bearer token auth.  Base URL: https://{host}:14000/api/v2
    """

    def __init__(self):
        self.host = os.environ.get("WEKA_HOST", "localhost")
        self.port = os.environ.get("WEKA_PORT", "14000")
        self.api_key = os.environ.get("WEKA_API_KEY", "")
        self.verify_ssl = os.environ.get("WEKA_VERIFY_SSL", "true").lower() == "true"

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _weka_get(self, path, params=None):
        url = f"https://{self.host}:{self.port}/api/v2{path}"
        resp = requests.get(url, headers=self._headers(), params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def list_filesystems(self, params):
        return self._weka_get("/fileSystems")

    def get_filesystem_stats(self, params):
        fs_id = params.get("id", "")
        if fs_id:
            return self._weka_get(f"/fileSystems/{fs_id}")
        return self._weka_get("/fileSystems")

    def list_quotas(self, params):
        return self._weka_get("/quotas")

    def list_snapshots(self, params):
        return self._weka_get("/snapshots")

    def get_cluster_status(self, params):
        return self._weka_get("/cluster")

    def list_nfs_exports(self, params):
        return self._weka_get("/nfs/permissions")

    def list_s3_buckets(self, params):
        return self._weka_get("/s3/buckets")

    def get_tiering_status(self, params):
        return self._weka_get("/objectStores")

    def list_drives(self, params):
        return self._weka_get("/drives")

    def get_events(self, params):
        return self._weka_get("/events")

    def list_containers(self, params):
        return self._weka_get("/containers")


def create_weka_server():
    server = Server("mcp-weka")
    client = WekaClient()
    runner = AnsibleBridge("stevefulme1.weka")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_filesystems", description="List Weka filesystems", inputSchema={"type": "object"}),
            Tool(name="get_filesystem_stats", description="Get filesystem statistics", inputSchema={"type": "object", "properties": {"id": {"type": "string", "description": "Filesystem ID"}}}),
            Tool(name="list_quotas", description="List filesystem quotas", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="get_cluster_status", description="Get Weka cluster status", inputSchema={"type": "object"}),
            Tool(name="list_nfs_exports", description="List NFS exports", inputSchema={"type": "object"}),
            Tool(name="list_s3_buckets", description="List S3-compatible buckets", inputSchema={"type": "object"}),
            Tool(name="get_tiering_status", description="Get tiering status", inputSchema={"type": "object"}),
            Tool(name="list_drives", description="List cluster drives", inputSchema={"type": "object"}),
            Tool(name="get_events", description="Get recent events", inputSchema={"type": "object"}),
            Tool(name="list_containers", description="List containers", inputSchema={"type": "object"}),
            Tool(name="create_filesystem", description="Create a filesystem (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "total_capacity": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_snapshot", description="Create a snapshot (via Ansible)", inputSchema={"type": "object", "properties": {"filesystem": {"type": "string"}, "name": {"type": "string"}}, "required": ["filesystem", "name"]}),
            Tool(name="set_quota", description="Set filesystem quota (via Ansible)", inputSchema={"type": "object", "properties": {"path": {"type": "string"}, "hard_limit": {"type": "string"}}, "required": ["path"]}),
            Tool(name="create_nfs_export", description="Create NFS export (via Ansible)", inputSchema={"type": "object", "properties": {"filesystem": {"type": "string"}, "path": {"type": "string"}}, "required": ["filesystem"]}),
            Tool(name="create_s3_bucket", description="Create S3 bucket (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_filesystems", "get_filesystem_stats", "list_quotas",
            "list_snapshots", "get_cluster_status", "list_nfs_exports",
            "list_s3_buckets", "get_tiering_status", "list_drives",
            "get_events", "list_containers",
        }
        write_tools = {"create_filesystem", "create_snapshot", "set_quota", "create_nfs_export", "create_s3_bucket"}
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
    server = create_weka_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
