"""MCP Server for Datadog."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class DatadogClient(BaseClient):
    """Direct API client for Datadog."""

    def __init__(self):
        super().__init__("DATADOG_HOST", "DATADOG_API_KEY")


def create_datadog_server():
    """Create and configure the Datadog MCP server."""
    server = create_server("mcp-datadog")
    client = DatadogClient()
    runner = AnsibleBridge("stevefulme1.datadog")

    @server.tool()
    async def list_monitors(params: dict) -> str:
        """List Datadog monitors"""
        result = await read_op(client, "list_monitors", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_monitor_details(params: dict) -> str:
        """Get monitor details"""
        result = await read_op(client, "get_monitor_details", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def query_metrics(params: dict) -> str:
        """Query metric timeseries"""
        result = await read_op(client, "query_metrics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_dashboards(params: dict) -> str:
        """List dashboards"""
        result = await read_op(client, "list_dashboards", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_slo_status(params: dict) -> str:
        """Get SLO status"""
        result = await read_op(client, "get_slo_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def search_events(params: dict) -> str:
        """Search events"""
        result = await read_op(client, "search_events", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_synthetics(params: dict) -> str:
        """List Synthetic tests"""
        result = await read_op(client, "list_synthetics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_host_tags(params: dict) -> str:
        """Get host tags"""
        result = await read_op(client, "get_host_tags", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_incidents(params: dict) -> str:
        """List incidents"""
        result = await read_op(client, "list_incidents", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_downtime_schedule(params: dict) -> str:
        """Get downtime schedule"""
        result = await read_op(client, "get_downtime_schedule", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_monitor(params: dict) -> str:
        """Create a monitor"""
        result = await write_op(runner, "create_monitor", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_dashboard(params: dict) -> str:
        """Create a dashboard"""
        result = await write_op(runner, "create_dashboard", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_slo(params: dict) -> str:
        """Create an SLO"""
        result = await write_op(runner, "create_slo", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def schedule_downtime(params: dict) -> str:
        """Schedule a downtime"""
        result = await write_op(runner, "schedule_downtime", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def mute_monitor(params: dict) -> str:
        """Mute a monitor"""
        result = await write_op(runner, "mute_monitor", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_incident(params: dict) -> str:
        """Create an incident"""
        result = await write_op(runner, "create_incident", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Datadog MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_datadog_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
