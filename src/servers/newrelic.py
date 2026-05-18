"""MCP Server for New Relic."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class NewrelicClient(BaseClient):
    """Direct API client for New Relic."""

    def __init__(self):
        super().__init__("NEWRELIC_HOST", "NEWRELIC_API_KEY")


def create_newrelic_server():
    """Create and configure the New Relic MCP server."""
    server = create_server("mcp-newrelic")
    client = NewrelicClient()
    runner = AnsibleBridge("stevefulme1.newrelic")

    @server.tool()
    async def nrql_query(params: dict) -> str:
        """Run NRQL query"""
        result = await read_op(client, "nrql_query", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_alert_policies(params: dict) -> str:
        """List alert policies"""
        result = await read_op(client, "list_alert_policies", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_alert_violations(params: dict) -> str:
        """Get alert violations"""
        result = await read_op(client, "get_alert_violations", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_dashboards(params: dict) -> str:
        """List dashboards"""
        result = await read_op(client, "list_dashboards", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_entity_details(params: dict) -> str:
        """Get entity details"""
        result = await read_op(client, "get_entity_details", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_synthetics(params: dict) -> str:
        """List Synthetic monitors"""
        result = await read_op(client, "list_synthetics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_sli_status(params: dict) -> str:
        """Get SLI/SLO status"""
        result = await read_op(client, "get_sli_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_workloads(params: dict) -> str:
        """List workloads"""
        result = await read_op(client, "list_workloads", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_apm_summary(params: dict) -> str:
        """Get APM summary"""
        result = await read_op(client, "get_apm_summary", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_infra_hosts(params: dict) -> str:
        """List infrastructure hosts"""
        result = await read_op(client, "get_infra_hosts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_alert_policy(params: dict) -> str:
        """Create alert policy"""
        result = await write_op(runner, "create_alert_policy", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_alert_condition(params: dict) -> str:
        """Create alert condition"""
        result = await write_op(runner, "create_alert_condition", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_dashboard(params: dict) -> str:
        """Create dashboard"""
        result = await write_op(runner, "create_dashboard", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_synthetic_monitor(params: dict) -> str:
        """Create Synthetic monitor"""
        result = await write_op(runner, "create_synthetic_monitor", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_workload(params: dict) -> str:
        """Create workload"""
        result = await write_op(runner, "create_workload", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def tag_entity(params: dict) -> str:
        """Tag an entity"""
        result = await write_op(runner, "tag_entity", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the New Relic MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_newrelic_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
