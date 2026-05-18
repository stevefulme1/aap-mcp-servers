"""MCP Server for Elastic Stack."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class ElasticClient(BaseClient):
    """Direct API client for Elastic Stack."""

    def __init__(self):
        super().__init__("ELASTIC_HOST", "ELASTIC_API_KEY")


def create_elastic_server():
    """Create and configure the Elastic Stack MCP server."""
    server = create_server("mcp-elastic")
    client = ElasticClient()
    runner = AnsibleBridge("stevefulme1.elastic")

    @server.tool()
    async def search(params: dict) -> str:
        """Search documents across indices"""
        result = await read_op(client, "search", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_health(params: dict) -> str:
        """Get Elasticsearch cluster health"""
        result = await read_op(client, "get_cluster_health", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_indices(params: dict) -> str:
        """List indices with size and doc count"""
        result = await read_op(client, "list_indices", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_ilm_policy(params: dict) -> str:
        """Get ILM policy details"""
        result = await read_op(client, "get_ilm_policy", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_index_stats(params: dict) -> str:
        """Get index statistics"""
        result = await read_op(client, "get_index_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_node_stats(params: dict) -> str:
        """Get cluster node statistics"""
        result = await read_op(client, "get_node_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_snapshots(params: dict) -> str:
        """List available snapshots"""
        result = await read_op(client, "list_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_watcher_alerts(params: dict) -> str:
        """Get recent Watcher alerts"""
        result = await read_op(client, "get_watcher_alerts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_fleet_agents(params: dict) -> str:
        """List Fleet managed agents"""
        result = await read_op(client, "list_fleet_agents", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_kibana_dashboards(params: dict) -> str:
        """List Kibana dashboards"""
        result = await read_op(client, "get_kibana_dashboards", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def search_logs(params: dict) -> str:
        """Search logs with KQL"""
        result = await read_op(client, "search_logs", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_index(params: dict) -> str:
        """Create an Elasticsearch index"""
        result = await write_op(runner, "create_index", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_ilm_policy(params: dict) -> str:
        """Create an ILM policy"""
        result = await write_op(runner, "create_ilm_policy", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_snapshot(params: dict) -> str:
        """Create a snapshot"""
        result = await write_op(runner, "create_snapshot", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def import_dashboard(params: dict) -> str:
        """Import a Kibana dashboard"""
        result = await write_op(runner, "import_dashboard", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def manage_fleet_policy(params: dict) -> str:
        """Manage Fleet agent policy"""
        result = await write_op(runner, "manage_fleet_policy", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Elastic Stack MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_elastic_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()
