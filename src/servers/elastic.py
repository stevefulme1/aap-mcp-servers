"""MCP Server for Elastic Stack (Elasticsearch + Kibana)."""

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


class ElasticClient(BaseClient):
    """Direct API client for Elasticsearch.

    Supports Basic auth (user:pass) or API key.
    Base URL: https://{host}:9200
    """

    def __init__(self):
        self.host = os.environ.get("ELASTIC_HOST", "localhost")
        self.port = os.environ.get("ELASTIC_PORT", "9200")
        self.api_key = os.environ.get("ELASTIC_API_KEY", "")
        self.username = os.environ.get("ELASTIC_USER", "elastic")
        self.password = os.environ.get("ELASTIC_PASSWORD", "")
        self.kibana_host = os.environ.get("KIBANA_HOST", self.host)
        self.kibana_port = os.environ.get("KIBANA_PORT", "5601")
        self.verify_ssl = os.environ.get("ELASTIC_VERIFY_SSL", "true").lower() == "true"

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        elif self.password:
            cred = b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        return headers

    def _es_get(self, path, params=None):
        """GET against Elasticsearch."""
        url = f"https://{self.host}:{self.port}{path}"
        resp = requests.get(url, headers=self._headers(), params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    def _es_post(self, path, body=None):
        """POST against Elasticsearch."""
        url = f"https://{self.host}:{self.port}{path}"
        resp = requests.post(url, headers=self._headers(), json=body,
                             timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    def _kibana_get(self, path, params=None):
        """GET against Kibana API."""
        url = f"https://{self.kibana_host}:{self.kibana_port}{path}"
        headers = self._headers()
        headers["kbn-xsrf"] = "true"
        resp = requests.get(url, headers=headers, params=params,
                            timeout=30, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def search(self, params):
        """POST /{index}/_search"""
        index = params.get("index", "*")
        body = params.get("body", {"query": {"match_all": {}}, "size": params.get("size", 10)})
        return self._es_post(f"/{index}/_search", body=body)

    def get_cluster_health(self, params):
        """GET /_cluster/health"""
        return self._es_get("/_cluster/health")

    def list_indices(self, params):
        """GET /_cat/indices?format=json"""
        return self._es_get("/_cat/indices", params={"format": "json", "h": "index,health,status,docs.count,store.size"})

    def get_ilm_policy(self, params):
        """GET /_ilm/policy/{policy}"""
        policy = params.get("policy", "")
        path = f"/_ilm/policy/{policy}" if policy else "/_ilm/policy"
        return self._es_get(path)

    def get_index_stats(self, params):
        """GET /{index}/_stats"""
        index = params.get("index", "_all")
        return self._es_get(f"/{index}/_stats")

    def get_node_stats(self, params):
        """GET /_nodes/stats"""
        return self._es_get("/_nodes/stats")

    def list_snapshots(self, params):
        """GET /_snapshot/{repo}/_all"""
        repo = params.get("repository", "_all")
        return self._es_get(f"/_snapshot/{repo}/_all")

    def get_watcher_alerts(self, params):
        """POST /.watcher-history*/_search for recent alerts."""
        body = {"query": {"match_all": {}}, "size": params.get("size", 20), "sort": [{"trigger_event.triggered_time": "desc"}]}
        return self._es_post("/.watcher-history*/_search", body=body)

    def list_fleet_agents(self, params):
        """GET /api/fleet/agents via Kibana."""
        return self._kibana_get("/api/fleet/agents")

    def get_kibana_dashboards(self, params):
        """GET /api/saved_objects/_find?type=dashboard via Kibana."""
        return self._kibana_get("/api/saved_objects/_find", params={"type": "dashboard", "per_page": params.get("per_page", 20)})

    def search_logs(self, params):
        """Search logs with KQL-style query via Elasticsearch."""
        index = params.get("index", "logs-*")
        q = params.get("query", "*")
        size = params.get("size", 50)
        body = {"query": {"query_string": {"query": q}}, "size": size, "sort": [{"@timestamp": "desc"}]}
        return self._es_post(f"/{index}/_search", body=body)


def create_elastic_server():
    """Create and configure the MCP server."""
    server = Server("mcp-elastic")
    client = ElasticClient()
    runner = AnsibleBridge("stevefulme1.elastic")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="search",
                description="Search documents across indices",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index": {"type": "string", "description": "Index pattern (default: *)"},
                        "body": {"type": "object", "description": "Elasticsearch query body"},
                        "size": {"type": "integer", "description": "Number of results"},
                    },
                },
            ),
            Tool(name="get_cluster_health", description="Get Elasticsearch cluster health", inputSchema={"type": "object"}),
            Tool(name="list_indices", description="List indices with size and doc count", inputSchema={"type": "object"}),
            Tool(
                name="get_ilm_policy",
                description="Get ILM policy details",
                inputSchema={
                    "type": "object",
                    "properties": {"policy": {"type": "string", "description": "Policy name (omit for all)"}},
                },
            ),
            Tool(
                name="get_index_stats",
                description="Get index statistics",
                inputSchema={
                    "type": "object",
                    "properties": {"index": {"type": "string", "description": "Index name (default: _all)"}},
                },
            ),
            Tool(name="get_node_stats", description="Get cluster node statistics", inputSchema={"type": "object"}),
            Tool(
                name="list_snapshots",
                description="List available snapshots",
                inputSchema={
                    "type": "object",
                    "properties": {"repository": {"type": "string", "description": "Snapshot repository name"}},
                },
            ),
            Tool(name="get_watcher_alerts", description="Get recent Watcher alerts", inputSchema={"type": "object"}),
            Tool(name="list_fleet_agents", description="List Fleet managed agents", inputSchema={"type": "object"}),
            Tool(name="get_kibana_dashboards", description="List Kibana dashboards", inputSchema={"type": "object"}),
            Tool(
                name="search_logs",
                description="Search logs with KQL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index": {"type": "string", "description": "Log index pattern (default: logs-*)"},
                        "query": {"type": "string", "description": "KQL query string"},
                        "size": {"type": "integer", "description": "Number of results"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="create_index",
                description="Create an Elasticsearch index (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "settings": {"type": "object"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_ilm_policy",
                description="Create an ILM policy (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "policy": {"type": "object"}},
                    "required": ["name", "policy"],
                },
            ),
            Tool(
                name="create_snapshot",
                description="Create a snapshot (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"repository": {"type": "string"}, "snapshot": {"type": "string"}},
                    "required": ["repository", "snapshot"],
                },
            ),
            Tool(
                name="import_dashboard",
                description="Import a Kibana dashboard (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard": {"type": "object"}},
                    "required": ["dashboard"],
                },
            ),
            Tool(
                name="manage_fleet_policy",
                description="Manage Fleet agent policy (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "namespace": {"type": "string"}},
                    "required": ["name"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "search", "get_cluster_health", "list_indices", "get_ilm_policy",
            "get_index_stats", "get_node_stats", "list_snapshots",
            "get_watcher_alerts", "list_fleet_agents", "get_kibana_dashboards",
            "search_logs",
        }
        write_tools = {
            "create_index", "create_ilm_policy", "create_snapshot",
            "import_dashboard", "manage_fleet_policy",
        }
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
    server = create_elastic_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
