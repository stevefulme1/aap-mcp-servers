"""MCP Server for Datadog monitoring platform."""

import asyncio
import json
import logging
import os
import time

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


class DatadogClient(BaseClient):
    """Direct API client for Datadog.

    Uses DD-API-KEY and DD-APPLICATION-KEY headers.
    Base URL: https://api.datadoghq.com
    """

    def __init__(self):
        self.host = os.environ.get("DATADOG_HOST", "api.datadoghq.com")
        self.api_key = os.environ.get("DATADOG_API_KEY", "")
        self.app_key = os.environ.get("DATADOG_APP_KEY", "")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
        }

    # -- read operations --

    def list_monitors(self, params):
        """GET /api/v1/monitor"""
        qp = {}
        if params.get("tags"):
            qp["monitor_tags"] = params["tags"]
        if params.get("page_size"):
            qp["page_size"] = params["page_size"]
        return self._get("/api/v1/monitor", params=qp)

    def get_monitor_details(self, params):
        """GET /api/v1/monitor/{monitor_id}"""
        mid = params.get("monitor_id", "")
        return self._get(f"/api/v1/monitor/{mid}")

    def query_metrics(self, params):
        """GET /api/v1/query — query metric timeseries."""
        now = int(time.time())
        qp = {
            "query": params.get("query", "avg:system.cpu.user{*}"),
            "from": params.get("from", now - 3600),
            "to": params.get("to", now),
        }
        return self._get("/api/v1/query", params=qp)

    def list_dashboards(self, params):
        """GET /api/v1/dashboard"""
        return self._get("/api/v1/dashboard")

    def get_slo_status(self, params):
        """GET /api/v1/slo"""
        qp = {}
        if params.get("ids"):
            qp["ids"] = params["ids"]
        return self._get("/api/v1/slo", params=qp)

    def search_events(self, params):
        """GET /api/v1/events"""
        now = int(time.time())
        qp = {
            "start": params.get("start", now - 3600),
            "end": params.get("end", now),
        }
        if params.get("tags"):
            qp["tags"] = params["tags"]
        return self._get("/api/v1/events", params=qp)

    def list_synthetics(self, params):
        """GET /api/v1/synthetics/tests"""
        return self._get("/api/v1/synthetics/tests")

    def get_host_tags(self, params):
        """GET /api/v1/tags/hosts"""
        return self._get("/api/v1/tags/hosts")

    def list_incidents(self, params):
        """GET /api/v2/incidents"""
        return self._get("/api/v2/incidents")

    def get_downtime_schedule(self, params):
        """GET /api/v2/downtime"""
        return self._get("/api/v2/downtime")


def create_datadog_server():
    """Create and configure the MCP server."""
    server = Server("mcp-datadog")
    client = DatadogClient()
    runner = AnsibleBridge("stevefulme1.datadog")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="list_monitors",
                description="List Datadog monitors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tags": {"type": "string", "description": "Comma-separated monitor tags to filter"},
                        "page_size": {"type": "integer", "description": "Number of monitors per page"},
                    },
                },
            ),
            Tool(
                name="get_monitor_details",
                description="Get monitor details by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "monitor_id": {"type": "integer", "description": "Monitor ID"},
                    },
                    "required": ["monitor_id"],
                },
            ),
            Tool(
                name="query_metrics",
                description="Query metric timeseries",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Datadog metric query, e.g. avg:system.cpu.user{*}"},
                        "from": {"type": "integer", "description": "Start epoch seconds"},
                        "to": {"type": "integer", "description": "End epoch seconds"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(name="list_dashboards", description="List dashboards", inputSchema={"type": "object"}),
            Tool(
                name="get_slo_status",
                description="Get SLO status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ids": {"type": "string", "description": "Comma-separated SLO IDs"},
                    },
                },
            ),
            Tool(
                name="search_events",
                description="Search events",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start": {"type": "integer", "description": "Start epoch seconds"},
                        "end": {"type": "integer", "description": "End epoch seconds"},
                        "tags": {"type": "string", "description": "Comma-separated tags to filter"},
                    },
                },
            ),
            Tool(name="list_synthetics", description="List Synthetic tests", inputSchema={"type": "object"}),
            Tool(name="get_host_tags", description="Get host tags", inputSchema={"type": "object"}),
            Tool(name="list_incidents", description="List incidents", inputSchema={"type": "object"}),
            Tool(name="get_downtime_schedule", description="Get downtime schedule", inputSchema={"type": "object"}),
            Tool(
                name="create_monitor",
                description="Create a monitor (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "query": {"type": "string"},
                    },
                    "required": ["name", "type", "query"],
                },
            ),
            Tool(
                name="create_dashboard",
                description="Create a dashboard (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                },
            ),
            Tool(
                name="create_slo",
                description="Create an SLO (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "type": {"type": "string"}},
                    "required": ["name", "type"],
                },
            ),
            Tool(
                name="schedule_downtime",
                description="Schedule a downtime (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"scope": {"type": "string"}, "start": {"type": "integer"}, "end": {"type": "integer"}},
                    "required": ["scope"],
                },
            ),
            Tool(
                name="mute_monitor",
                description="Mute a monitor (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"monitor_id": {"type": "integer"}},
                    "required": ["monitor_id"],
                },
            ),
            Tool(
                name="create_incident",
                description="Create an incident (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"title": {"type": "string"}, "severity": {"type": "string"}},
                    "required": ["title"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_monitors", "get_monitor_details", "query_metrics",
            "list_dashboards", "get_slo_status", "search_events",
            "list_synthetics", "get_host_tags", "list_incidents",
            "get_downtime_schedule",
        }
        write_tools = {
            "create_monitor", "create_dashboard", "create_slo",
            "schedule_downtime", "mute_monitor", "create_incident",
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
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_datadog_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()
