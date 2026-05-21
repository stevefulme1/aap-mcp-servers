"""MCP Server for VAST Data storage platform."""

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


class VastDataClient(BaseClient):
    """Direct API client for VAST Data.

    Supports Bearer token or Basic auth.  Base URL: https://{host}/api
    """

    def __init__(self):
        self.host = os.environ.get("VASTDATA_HOST", "localhost")
        self.api_key = os.environ.get("VASTDATA_API_KEY", "")
        self.username = os.environ.get("VASTDATA_USER", "")
        self.password = os.environ.get("VASTDATA_PASSWORD", "")
        self.verify_ssl = os.environ.get("VASTDATA_VERIFY_SSL", "true").lower() == "true"

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.username and self.password:
            cred = b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        return headers

    def _vast_get(self, path, params=None):
        url = f"https://{self.host}/api{path}"
        resp = requests.get(url, headers=self._headers(), params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def list_clusters(self, params):
        return self._vast_get("/clusters/")

    def get_cluster_stats(self, params):
        return self._vast_get("/monitors/ad_hoc_counters_for_overview/")

    def list_views(self, params):
        return self._vast_get("/views/")

    def list_quotas(self, params):
        return self._vast_get("/quotas/")

    def list_snapshots(self, params):
        return self._vast_get("/snapshots/")

    def list_users(self, params):
        return self._vast_get("/users/")

    def get_capacity(self, params):
        return self._vast_get("/capacity/")

    def list_protection_policies(self, params):
        return self._vast_get("/protectionpolicies/")

    def list_s3_policies(self, params):
        return self._vast_get("/s3lifecyclerules/")

    def get_audit_log(self, params):
        return self._vast_get("/auditlog/")

    def get_cluster_overview(self, params):
        return self._vast_get("/clusters/")


def create_vastdata_server():
    server = Server("mcp-vastdata")
    client = VastDataClient()
    runner = AnsibleBridge("stevefulme1.vastdata")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_clusters", description="List VAST clusters", inputSchema={"type": "object"}),
            Tool(name="get_cluster_stats", description="Get cluster statistics", inputSchema={"type": "object"}),
            Tool(name="list_views", description="List views (exports)", inputSchema={"type": "object"}),
            Tool(name="list_quotas", description="List quotas", inputSchema={"type": "object"}),
            Tool(name="list_snapshots", description="List snapshots", inputSchema={"type": "object"}),
            Tool(name="list_users", description="List users", inputSchema={"type": "object"}),
            Tool(name="get_capacity", description="Get capacity summary", inputSchema={"type": "object"}),
            Tool(name="list_protection_policies", description="List protection policies", inputSchema={"type": "object"}),
            Tool(name="list_s3_policies", description="List S3 lifecycle policies", inputSchema={"type": "object"}),
            Tool(name="get_audit_log", description="Get audit log", inputSchema={"type": "object"}),
            Tool(name="get_cluster_overview", description="Get cluster overview", inputSchema={"type": "object"}),
            Tool(name="create_view", description="Create a view (via Ansible)", inputSchema={"type": "object", "properties": {"path": {"type": "string"}, "policy_id": {"type": "integer"}}, "required": ["path"]}),
            Tool(name="create_quota", description="Create quota (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "hard_limit": {"type": "integer"}}, "required": ["name"]}),
            Tool(name="create_snapshot", description="Create snapshot (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}}, "required": ["name", "path"]}),
            Tool(name="create_protection_policy", description="Create protection policy (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_user", description="Create user (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_clusters", "get_cluster_stats", "list_views", "list_quotas",
            "list_snapshots", "list_users", "get_capacity",
            "list_protection_policies", "list_s3_policies", "get_audit_log",
            "get_cluster_overview",
        }
        write_tools = {"create_view", "create_quota", "create_snapshot", "create_protection_policy", "create_user"}
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
    server = create_vastdata_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
